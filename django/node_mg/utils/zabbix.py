from django.core.cache import cache
import threading
import requests
import json
import logging
from . import zabbix_config

logger = logging.getLogger(__name__)

# TODO: 添加zabbix可用性验证，避免失败调用


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
        if not zabbix_config.is_zabbix_sync_enabled():
            return

        config = zabbix_config.get_all()
        self.url = config.get('zabbix_url')
        self.username = config.get('zabbix_username')
        self.password = config.get('zabbix_password')
        self.interval = int(config.get('zabbix_interval', 0))
        self.token = None
        self._refresh_token()

    def _refresh_token(self):
        """刷新 token"""
        try:
            response = self._login()
            self.token = response
            logger.info(f"Zabbix token refreshed.")
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
                "username": self.username,
                "password": self.password
            },
            "id": 1
        }
        response = requests.post(self.url, json=payload, verify=False)
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
        self.url = zabbix_config.get('zabbix_url')
        self.template = zabbix_config.get('zabbix_host_template')
        self.template_host_name = zabbix_config.config.get('zabbix_host_template','Linux by Zabbix agent')
        self.template_ipmi_name = zabbix_config.config.get('zabbix_ipmi_template','Chassis by IPMI')
        self.template_network_name = zabbix_config.config.get('zabbix_network_template','Generic by SNMP')
        self.session = requests.Session()
        self.session.verify = False
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
        result = response.json()
        if result.get('result'):
            logger.info(f"status: success action: {method} params: {payload} result: {result}")
            return result
        else:
            logger.error(f"status: failed  action: {method} params: {payload} result: {result}")
            return result

    def host_get(self,host, output=None,other_args=None):

        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": output if output else ["hostid"],
                "filter": {
                    "host": host
                }
            },
            "id": 1,
            "auth": self.auth
        }
        if other_args:
            for k, v in other_args.items():
                data["params"][k] = v
        result = self._call("host.get", data["params"])
        if result.get('result'):
            return result["result"]
        return None

    def host_create_old(self, host, name, ip, groups=None, proxy_id=None):
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
        if proxy_id:
            data["params"]["proxy_hostid"] = proxy_id

        result = self._call("host.create", data["params"])
        logger.info(f"Host created: {result}")
        return result["result"]
    def host_create(self, host, name,interfaces=None,groups=None,template_names=None,proxy_id=None,other_args=None):
        data = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": host,
                "name": name,
                "interfaces": interfaces,
                "groups": [
                    {
                        "groupid": group_id
                    } for group_id in groups
                ] if groups else [
                    {
                        "groupid": self.default_group_id
                    }
                ],

            },
            "id": 1,
            "auth": self.auth
        }
        if proxy_id:
            data["params"]["proxy_hostid"] = proxy_id
        #模板获取
        template_ids = self.get_default_template_by_interfaces(interfaces)
        if template_names:
            get_template_ids = self.get_template(template_names)
            if get_template_ids:
                template_ids.extend(get_template_ids)
        data["params"]["templates"] = [ {"templateid": template_id } for template_id in list(set(template_ids)) ]   
        # 根据接口类型，获取默认模板
        if other_args:
            for k, v in other_args.items():
                data["params"][k] = v
        result = self._call("host.create", data["params"])
        logger.info(f"Host created: {result}")
        return result["result"]

    def host_get_interfaces(self, hostid):
        """获取主机接口信息"""
        data = {
            "jsonrpc": "2.0",
            "method": "hostinterface.get",
            "params": {
                "output": "extend",
                "filter": {
                    "hostid": hostid
                }
            },
            "auth": self.auth,
            "id": 1
        }
        result = self._call("hostinterface.get", data["params"])
        if result.get('result'):
            return result["result"]
        return None
    def create_interfaces(self, hostid,interface):
        """创建主机接口信息"""
        #根据interface类型，获取默认模板ID
        template_id = self.get_default_template_by_interface(interface)
        data = {
            "jsonrpc": "2.0",
            "method": "hostinterface.create",
            "params": {
                "hostid": hostid,
            },
            "auth": self.auth,
            "id": 1
        }
        data["params"].update(interface)
        result = self._call("hostinterface.create", data["params"])
        if result.get('result'):
            # 接口添加成功，则添加模板
            if template_id:
                self.host_update(hostid,add_template=[template_id])
            return result["result"]
        return None
    def delete_interfaces(self, hostid,interface):

        """删除主机接口信息"""
        # 只处理type=3，ipmi接口
        if str(interface["type"]) != "3":
            return None
        # 删除接口前，清理模板
        template_id = self.get_default_template_by_interface(interface)
        self.host_update(hostid,other_args={"templates_clear":[{"templateid":template_id}]})
        host_interfaces = self.host_get_interfaces(hostid=hostid)
        interface_id = None
        if host_interfaces:
            for host_interface in host_interfaces:
                if str(host_interface["type"]) == "3":
                    interface_id = host_interface["interfaceid"]

        if interface_id:
            data = {
                "jsonrpc": "2.0",
                "method": "hostinterface.delete",
                "params": [interface_id],
                "auth": self.auth,
                "id": 1
            }
            result = self._call("hostinterface.delete", data["params"])
            if result.get('result'):
                return result["result"]
            return None        
    def update_interfaces(self, hostid,interfaces):
        """获取主机接口信息"""
        host_interfaces = self.host_get_interfaces(hostid=hostid)
        host_interfaces_dict = {}
        if host_interfaces:
            for host_interface in host_interfaces:
                host_interfaces_dict[host_interface["type"]] = host_interface

        for interface in interfaces:
            if interface["type"] in host_interfaces_dict.keys():
                data = {
                        "jsonrpc": "2.0",
                        "method": "hostinterface.update",
                        "params": {
                            "interfaceid": host_interfaces_dict[interface["type"]]["interfaceid"],
                        },
                        "auth": self.auth,
                        "id": 1
                    }
                data["params"].update(interface)
                result = self._call("hostinterface.update", data["params"])
                if result.get('result'):
                    return result["result"]
                return None    
    def host_update_old(self, hostid, host, name, ip=None, proxy=None):
        """更新主机可见名称/IP/代理"""
        # 获取现有接口
        interfaces = self.host_get_interfaces(hostid)

        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": hostid,
                "host": host,
                "name": name
            },
            "id": 1,
            "auth": self.auth
        }

        # ip变更
        if ip:
            data["params"]["interfaces"] = [
                {
                    "ip": ip,
                    "dns": "",
                    "port": "10050",
                    "type": 1,
                    "main": 1,
                    "useip": 1
                }
            ]
            if interfaces:
                interface_id = [i["interfaceid"] for i in interfaces if i['type'] == '1']
                data["params"]["interfaces"][0]["interfaceid"] = interface_id[0]

        # 代理变更
        if proxy is not None:
            data["params"]["proxy_hostid"] = proxy

        result = self._call("host.update", data["params"])
        logger.info(f"Host updated: {result}")
        return result["result"]

    def host_update(self,hostid,host=None, name=None,interfaces=None,groups=None,template_names=None,add_template=None,proxy_id=None,other_args=None):
        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": hostid,
                # "interfaces": interfaces,
            },
            "id": 1,
            "auth": self.auth
        }
        if host:   
            data["params"]["host"] = host
        if name:
            data["params"]["name"] = name
        # 接口
        if groups:
            data["params"]["groups"] = [
                    {
                        "groupid": group_id
                    } for group_id in groups
                ] 
        if proxy_id:
            data["params"]["proxy_hostid"] = proxy_id
        if template_names:
            get_template_ids = self.get_template(template_names)
            if get_template_ids:
                data["params"]["templates"] = [
                    {
                        "templateid": template_id
                    } for template_id in get_template_ids
                ]
        # 新增模板
        if add_template:
            # 获取现有的templateid
            existing_templates = self.get_template_by_id(hostid=hostid)
            if existing_templates:
                existing_templates.extend(add_template)
            else:
                existing_templates = add_template
            data["params"]["templates"] = [{"templateid": tid} for tid in existing_templates]

        # 其他参数
        if other_args:
            for k, v in other_args.items():
                data["params"][k] = v
        
        result = self._call("host.update", data["params"])
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

    def host_update_proxy(self, hostid, proxy_id):
        """更新主机代理"""
        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": hostid,
                "proxy_hostid": proxy_id
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.update", data["params"])
        if result.get("result"):
            return result["result"]
        return None

    def host_clear_proxy(self, hostid):
        """清除主机代理"""
        data = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": hostid,
                "proxy_hostid": "0"
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("host.update", data["params"])
        if result.get("result"):
            return result["result"]
        return None
    def host_massclear_proxy(self, hostids=[]):
        """清除主机代理"""
        data = {
            "params": {
                "hostid": hostids,
                "proxy_hostid": "0"
            },
        }
        result = self._call("host.massupdate", data["params"])
        if result.get("result"):
            return result["result"]
        return None    
    def get_default_template(self, template_name):
        target = template_name or self.template_host_name
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
            tn = self.template_host_name
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

    def get_proxies(self):
        """获取代理列表"""
        data = {
            "jsonrpc": "2.0",
            "method": "proxy.get",
            "params": {
                "output": ["proxyid", "host", "status", "lastaccess", "description"]
            },
            "auth": self.auth,
            "id": 1
        }
        result = self._call("proxy.get", data["params"])
        if result.get("result"):
            return result["result"]
        return None

    def get_proxy_by_name(self, proxy_name):
        data = {
            "params": {
                "output": ["proxyid", "host", "status", "lastaccess", "description"],
                "filter": {
                    "host": proxy_name
                }
            },
        }
        result = self._call("proxy.get", data["params"])
        if result.get("result"):
            return result["result"][0]
        return None
    def get_proxy_by_proxy_address(self, ip_address):
        data = {
            "params": {
                "output": ["proxyid", "host", "status", "lastaccess", "description"],
                "filter": {
                    "proxy_address": ip_address
                }
            },
        }
        result = self._call("proxy.get", data["params"])
        if result.get("result"):
            return result["result"][0]
        return None
    def create_proxy(self, proxy_name,proxy_ip=None,status=5):
        data = {
            "params": {
                "host": proxy_name,
                "status":status,
                "proxy_address": proxy_ip,
                "hosts": []
            },
        }
        result = self._call("proxy.create", data["params"])
        if result.get("result"):
            return result["result"]
        return None

    def update_proxy(self, proxyId, proxy_name,proxy_ip=None,hosts=[]):
        data = {
            "params": {
                "proxyid": proxyId,
                "host": proxy_name,
                "proxy_address": proxy_ip,
                "hosts": hosts
            },
        }
        result = self._call("proxy.update", data["params"])
        if result.get("result"):
            return result["result"]
        return None
    def delete_proxy(self, proxyId):
        data = {
            "params": proxyId,
        }
        result = self._call("proxy.delete", data["params"])
        if result.get("result"):
            return result["result"][0]
        return None
    def delete_proxy_by_name(self, proxy_name):
        proxy = self.get_proxy_by_name(proxy_name)
        if proxy:
            return self.delete_proxy(proxy["proxyid"])
    def get_template_by_id(self,hostid,output=None,other_args=None):
        """获取主机关联的模板"""
        data = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": output if output else ["templateid","host"],
                "hostids": hostid
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("template.get", data["params"])
        if result.get("result"):
            return [  i["templateid"] for i in result["result"] ]
        return None

    def get_template(self,template_names):
        """获取所有模板"""
        data = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": ["templateid", "host"],
                "filter": {
                    "host": 
                        template_names if isinstance(template_names, list) else [template_names]   
                        }
            },
            "id": 1,
            "auth": self.auth
        }
        result = self._call("template.get", data["params"])
        if result.get("result"):
            return  [ i["templateid"] for i in result["result"] ]
        return None
    def get_default_template_by_interfaces(self,interfaces):
        """根据多个接口类型获取默认模板"""
        template_ids = []
        if not interfaces:
            return template_ids
        types = [ int(i.get('type')) for i in interfaces ]
        if 1 in types:
            template_ids.append( self.get_default_template(self.template_host_name) )
        if 2 in types:
            template_ids.append( self.get_default_template(self.template_network_name) )
        if 3 in types:
            template_ids.append( self.get_default_template(self.template_ipmi_name) )
        return list(set(template_ids))
    def get_default_template_by_interface(self,interface):
        """根据单个接口类型获取默认模板"""
        template_id = None
        if not interface:
            return template_id
        types = [ int(interface.get('type')) ]
        if 1 in types:
            template_id =  self.get_default_template(self.template_host_name) 
        if 2 in types:
            template_id =  self.get_default_template(self.template_network_name) 
        if 3 in types:
            template_id =  self.get_default_template(self.template_ipmi_name) 
        return template_id