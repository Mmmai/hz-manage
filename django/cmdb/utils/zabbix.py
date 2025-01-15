from django.core.cache import cache
from django.conf import settings
import threading
import requests
import json
import logging

logger = logging.getLogger(__name__)


class ZabbixTokenManager:
    _lock = threading.Lock()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not getattr(self, '_initialized', False):
            self.token = None
            self.url = None
            self.username = None
            self.password = None
            self.interval = 0
            self._refresh_timer = None
            self._running = False
            self._initialized = True

    def initialize(self):
        """初始化 token 管理"""
        config = getattr(settings, 'ZABBIX_CONFIG', {})
        self.url = config.get('url')
        self.username = config.get('username')
        self.password = config.get('password')
        self.interval = config.get('interval', 0)
        self.token = None
        self._refresh_token()

    def _refresh_token(self):
        """刷新 token"""
        try:
            response = self._login()
            self.token = response
            # logger.debug(f"Refreshed token to: {self.token}")
            if self.interval > 0:
                cache.set('zabbix_token', self.token, timeout=self.interval)
                self._schedule_next_refresh()
            else:
                cache.set('zabbix_token', self.token, timeout=None)
        except Exception as e:
            logger.error(f"Zabbix token refresh failed: {str(e)}")

    def _login(self):
        """登录获取 token"""
        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.username,
                "password": self.password
            },
            "id": 1
        }
        response = requests.post(self.url, json=payload)
        response.raise_for_status()
        return response.json()['result']

    def _schedule_next_refresh(self):
        """计划下次刷新"""
        if self._refresh_timer:
            self._refresh_timer.cancel()
        self._refresh_timer = threading.Timer(self.interval, self._refresh_token)
        self._refresh_timer.start()

    def get_token(self):
        if not self.token:
            self.token = cache.get('zabbix_token')
        return self.token


class ZabbixAPI:
    _default_group_id = None

    def __init__(self):
        self.url = getattr(settings, 'ZABBIX_CONFIG', {}).get('url')
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json-rpc"})
        self.token_manager = ZabbixTokenManager()

    @property
    def auth(self):
        return self.token_manager.get_token()

    def _call(self, method, params=None):
        """统一API调用方法"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1,
            "auth": self.auth
        }
        response = self.session.post(self.url, json=payload)
        return response.json()

    def host_get(self, host):
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "host"],
                "filter": {
                    "host": host
                }
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.get", data["params"])
        return result["result"]

    def host_create(self, host, name, ip):
        data = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": host,
                "name": name,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": self.default_group_id
                    }
                ],
                "templates": [
                    {
                        "templateid": "10001"
                    }
                ]
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.create", data["params"])
        logger.info(f"Host created: {result}")
        return result["result"]

    def host_get_interfaces(self, hostid):
        """获取主机接口信息"""
        data = {
            "jsonrpc": "2.0",
            "method": "hostinterface.get",
            "params": {
                "hostids": hostid,
                "output": "extend"
            },
            "auth": self.auth,
            "id": 1
        }
        result = self._call("hostinterface.get", data["params"])
        return result["result"]

    def host_update(self, hostid, host, name, ip):
        """更新主机IP"""
        # 获取现有接口
        interfaces = self.host_get_interfaces(hostid)
        if not interfaces:
            raise Exception("No interfaces found for host")

        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": hostid,
                "host": host,
                "name": name,
                "interfaces": [
                    {
                        "interfaceid": interfaces[0]["interfaceid"],
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "10050"
                    }
                ]
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.update", data["params"])
        logger.info(f"Host updated: {result}")
        return result["result"]

    def host_enable(self, host):
        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": host,
                "status": 0
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.update", data["params"])
        return result["result"]

    def host_disable(self, host):
        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": host,
                "status": 1
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.update", data["params"])
        return result["result"]

    def host_delete(self, hostid):
        data = {
            "jsonrpc": "2.0",
            "method": "host.delete",
            "params": [hostid],
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.delete", data["params"])
        return result["result"]

    def create_hostgroup(self, group_name):
        """创建主机组"""
        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.create",
            "params": {
                "name": group_name
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("hostgroup.create", data["params"])
        if result.get("result"):
            return result["result"]["groupids"][0]
        else:
            logger.error(f"Failed to create hostgroup: {result}")
        return result

    @property
    def default_group_id(self):
        """获取空闲池组ID"""
        if self._default_group_id is None:
            try:
                data = {
                    "jsonrpc": "2.0",
                    "method": "hostgroup.get",
                    "params": {
                        "filter": {
                            "name": "空闲池"
                        }
                    },
                    "id": 1,
                    "auth": self.auth
                }
                result = self._call("hostgroup.get", data["params"])

                if result.get("result"):
                    self._default_group_id = result["result"][0]["groupid"]
                else:
                    self._default_group_id = self.create_hostgroup("空闲池")

            except Exception as e:
                logger.error(f"Failed to get/create idle group: {str(e)}")
                raise

        return self._default_group_id
