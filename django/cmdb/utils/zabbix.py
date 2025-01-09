import threading
import urllib3
import json
import logging
logger = logging.getLogger(__name__)

class ZabbixTokenManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.api = None
        
    def initialize(self, config):
        """初始化Zabbix API连接"""
        if self.api is None:
            self.api = ZabbixAPI(
                url=config.get('url'),
                username=config.get('username'),
                password=config.get('password'),
                interval=config.get('interval')
            )
            self.api.start_token_refresh()
            
    def stop(self):
        """停止token刷新"""
        if self.api:
            self.api.stop_token_refresh()

class ZabbixAPI:
    def __init__(self, url, username, password, interval=0):
        self.url = url
        self.username = username
        self.password = password
        self.auth = None
        self.interval = interval if interval > 0 else 0
        self.header = {"Content-Type": "application/json-rpc"}
        
        self.http = urllib3.PoolManager()
        
        self._timer = None
        self._running = False
        
    def start_token_refresh(self):
        """启动token自动刷新"""
        if self.interval <= 0:
            logger.info("Token auto-refresh disabled")
            if self.auth is None:
                self.login()
                return
        self._running = True
        self.login()
        self._schedule_next_refresh()
    
    def stop_token_refresh(self):
        """停止token自动刷新"""
        self._running = False
        if self._timer:
            self._timer.cancel()
    
    def _schedule_next_refresh(self):
        """调度下一次token刷新"""
        if self._running and self.interval > 0:
            self._timer = threading.Timer(self.interval, self._refresh_token)
            self._timer.daemon = True
            self._timer.start()
    
    def _refresh_token(self):
        """刷新token的执行函数"""
        try:
            self.login()
            self._schedule_next_refresh()
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            # 发生错误时5分钟后重试
            if self._running:
                self._timer = threading.Timer(300, self._refresh_token)
                self._timer.daemon = True
                self._timer.start()
        
    def login(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.username,
                "password": self.password
            },
            "id": 1,
            "auth": None
        }
        response = self.http.request("POST", self.url, headers=self.header, body=json.dumps(data))
        result = json.loads(response.data.decode())
        self.auth = result["result"]
        logger.info(f"Zabbix API login successful: {result}", )

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
        response = self.http.request("POST", self.url, headers=self.header, body=json.dumps(data))
        result = json.loads(response.data.decode())
        return result["result"]

    def host_create(self, host, ip):
        data = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": host,
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
                        "groupid": "2"
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
        response = self.http.request("POST", self.url, headers=self.header, body=json.dumps(data))
        result = json.loads(response.data.decode())
        return result["result"]

    def host_delete(self, host):
        data = {
            "jsonrpc": "2.0",
            "method": "host.delete",
            "params": [host],
            "id": 1,
            "auth": self.auth
        }
        response = self.http.request("POST", self.url, headers=self.header, body=json.dumps(data))
        result = json.loads(response.data.decode())
        return result["result"]