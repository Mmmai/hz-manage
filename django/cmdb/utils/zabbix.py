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
    _default_template_id = None

    def __init__(self):
        self.url = getattr(settings, 'ZABBIX_CONFIG', {}).get('url')
        self.template = getattr(settings, 'ZABBIX_CONFIG', {}).get('template')
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
                "output": ["hostid"],
                "filter": {
                    "host": host
                }
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.get", data["params"])
        return result["result"]

    def host_create(self, host, name, ip, groups=None):
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
                        "groupid": group_id
                    } for group_id in groups
                ] if groups else [
                    {
                        "groupid": self.default_group_id
                    }
                ],
                "templates": [
                    {
                        "templateid": self.default_template_id
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

    def host_sync(self, hostid, name=None, groups=None):
        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": hostid
            },
            "id": 1,
            "auth": self.auth
        }
        if name:
            data["params"]["name"] = name
        if groups:
            data["params"]["groups"] = [
                {
                    "groupid": group_id
                } for group_id in groups
            ]
        result = self._call("host.update", data["params"])
        if result.get("result"):
            return result["result"]
        else:
            logger.error(f"Failed to sync host: {result}")
            return None

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

    def get_default_template(self, template_name):
        target = template_name or 'Template OS Linux V3.1'
        data = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "extend",
                "filter": {
                    "host": [target]
                }
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("template.get", data["params"])
        if result.get("result"):
            return result["result"][0]["templateid"]
        else:
            logger.error(f"Template not found: {target}")
            return None

    @property
    def default_template_id(self):
        if self._default_template_id is None:
            tn = self.template
            self._default_template_id = self.get_default_template(tn) or "10001"
        return self._default_template_id

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

    def get_hostgroup(self, group_name):
        """获取主机组"""
        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "filter": {
                    "name": group_name
                }
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("hostgroup.get", data["params"])
        if result.get("result"):
            return result["result"][0]["groupid"]
        return None

    def get_hostgroups(self):
        """获取所有主机组"""
        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": ["groupid", "name"]
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("hostgroup.get", data["params"])
        if result.get("result"):
            return result["result"]
        return None

    def get_or_create_hostgroup(self, group_name):
        """获取或创建主机组"""
        group = self.get_hostgroup(group_name)
        if group:
            return group
        return self.create_hostgroup(group_name)

    def update_hostgroup(self, groupid, group_name):
        """更新主机组"""
        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.update",
            "params": {
                "groupid": groupid,
                "name": group_name
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("hostgroup.update", data["params"])
        return result["result"]

    def delete_hostgroup(self, group_name):
        """删除主机组"""
        group_id = self.get_hostgroup(group_name)
        if group_id:
            data = {
                "jsonrpc": "2.0",
                "method": "hostgroup.delete",
                "params": {
                    "groupid": group_id,
                },
                "id": 1,
                "auth": self.auth
            }
            result = self._call("hostgroup.delete", data["params"])
            return result["result"]
        logger.error(f"Hostgroup not found: {group_name}")
        return None

    def rename_hostgroup(self, old_name, new_name):
        """重命名主机组"""
        groupid = self.get_hostgroup(old_name)
        if groupid:
            return self.update_hostgroup(groupid, new_name)
        return self.get_or_create_hostgroup(new_name)

    def replace_host_hostgroup(self, hosts, groups):
        """替换主机组"""
        logger.info(f'Replace host group: {groups} -> {hosts}')
        groupids = [self.get_or_create_hostgroup(g) for g in groups]
        hostids = [self.host_get(h)[0]["hostid"] for h in hosts]
        data = {
            "jsonrpc": "2.0",
            "method": "host.massupdate",
            "params": {
                "hosts": [{'hostid': hostid} for hostid in hostids],
                "groups": [{"groupid": groupid} for groupid in groupids]
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.massupdate", data["params"])
        if result.get("result"):
            return result["result"]
        else:
            logger.error(f"Failed to replace host group: {result}")
            return None

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

    def get_hosts_interface_availability(self, host_ids):
        """获取主机接口可用性状态"""
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "name", "status"],
                "selectInterfaces": ["interfaceid", "ip", "type", "available"],
                "hostids": host_ids
            },
            "auth": self.auth,
            "id": 1
        }
        return self._call('host.get', data["params"]) or []
