from .utils.comm import get_uuid
import os
# 初始化创建目录
INIT_MENU = [
    {
        "label": "首页",
        "icon": "ep:home-filled",
        "name": "home",
        "status": 1,
        "path": "/home",
        "is_menu": 1,
        "sort": 1,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": '',
        "parentid_id": ''
    },
    {
        "label": "门户收藏夹",
        "icon": "ep:star",
        "name": "favorites",
        "status": 1,
        "path": "/favorites",
        "is_menu": 1,
        "sort": 2,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": '',
        "keepalive": 1,
        "parentid_id": ''
    },
    {
        "label": "可视化大屏",
        "icon": "ep:trend-charts",
        "name": "iframe",
        "status": 1,
        "path": "/iframe",
        "is_menu": 1,
        "sort": 2,
        "has_info": 0,
        "info_view_name": "",
        "is_iframe": 1,
        "iframe_url": "http://grafana:3000",
        "description": "",
        "parentid_id": ''
    },
    {
        "label": "资产配置",
        "icon": "ep:management",
        "name": "cmdb",
        "status": 1,
        "path": "",
        "is_menu": 0,
        "sort": 3,
        "has_info": 0,
        "info_view_name": "",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "parentid_id": ''
    },
    {
      "label": "资源",
      "icon": "ep:message-box",
      "name": "cidata",
      "status": 1,
      "path": "/cidata",
      "is_menu": 1,
      "sort": 0,
      "has_info": 0,
      "info_view_name": '',
      "is_iframe": 0,
      "iframe_url": '',
      "description": "",
      "keepalive": 1,
      "parentid_id": "cmdb",
      "buttons": [
                  {"name":"导入","action":"import"},
                  {"name":"导出","action":"export"},
                  {"name":"显示密码","action":"showPassword"},
                  ]
    },
    {
        "label": "模型管理",
        "icon": "mdi:alpha-m-box-outline",
        "name": "cimodelManage",
        "status": 1,
        "path": "",
        "is_menu": 0,
        "sort": 1,
        "has_info": 0,
        "info_view_name": "",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "cmdb"
    },
    {
        "label": "模型配置",
        "icon": "mdi:table-cog",
        "name": "model",
        "status": 1,
        "path": "/model",
        "is_menu": 1,
        "sort": 0,
        "has_info": 1,
        "info_view_name": "modelinfo",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "cimodelManage"
    },
    {
        "label": "校验配置",
        "icon": "ep:memo",
        "name": "ciConfig",
        "status": 1,
        "path": "ciConfig",
        "is_menu": 1,
        "sort": 3,
        "has_info": 0,
        "info_view_name": "",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "cimodelManage"
    },
    {
        "label": "资产审计",
        "icon": "ep:box",
        "name": "cidataAudit",
        "status": 0,
        "path": "/cidataAudit",
        "is_menu": 1,
        "sort": 2,
        "has_info": 0,
        "info_view_name": "",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "parentid_id": "cmdb"
    },
    {
        "label": "作业平台",
        "icon": "clarity:wrench-line",
        "name": "workingPlatform",
        "status": 1,
        "path": "",
        "is_menu": 0,
        "sort": 4,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "parentid_id": "",
    },
    {
      "label": "资产同步",
      "icon": "clarity:repeat-line",
      "name": "ciSyncZabbix",
      "status": 1,
      "path": "/ciSyncZabbix",
      "is_menu": 1,
      "sort": 0,
      "has_info": 0,
      "info_view_name": '',
      "is_iframe": 0,
      "iframe_url": '',
      "description": "",
      "keepalive": 1,
      "parentid_id": "workingPlatform",
    },
    {
        "label": "日志应用",
        "icon": "ep:reading",
        "name": "log",
        "status": 1,
        "path": "",
        "is_menu": 0,
        "sort": 4,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "parentid_id": ''
    },
    {
        "label": "日志检索",
        "icon": "ep:search",
        "name": "loki",
        "status": 1,
        "path": "/loki",
        "is_menu": 1,
        "sort": 0,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "log"
    },
    {
        "label": "流程日志",
        "icon": "ep:connection",
        "name": "logAnalysis",
        "status": 1,
        "path": "/logAnalysis",
        "is_menu": 1,
        "sort": 1,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "log"
    },
    {
        "label": "环节配置",
        "icon": "ep:guide",
        "name": "logModule",
        "status": 1,
        "path": "/logModule",
        "is_menu": 1,
        "sort": 3,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "配置日志环节日志",
        "keepalive": 1,
        "parentid_id": "log"
    },
    {
        "label": "分析记录",
        "icon": "ep:scale-to-original",
        "name": "logFlowMission",
        "status": 1,
        "path": "/logFlowMission",
        "is_menu": 1,
        "sort": 4,
        "has_info": 1,
        "info_view_name": "logFlowInfo",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "log"
    },

    {
        "label": "系统管理",
        "icon": "ep:setting",
        "name": "settings",
        "status": 1,
        "path": '',
        "is_menu": 0,
        "sort": 5,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "parentid_id": ''
    },
    {
        "label": "用户管理",
        "icon": "ep:user",
        "name": "user",
        "status": 1,
        "path": "/user",
        "is_menu": 1,
        "sort": 1,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": '',
        "keepalive": 1,
        "parentid_id": "settings"
    },
    {
        "label": "用户组管理",
        "icon": "material-symbols:group-outline",
        "name": "userGroup",
        "status": 1,
        "path": "/userGroup",
        "is_menu": 1,
        "sort": 2,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": '',
        "keepalive": 1,
        "parentid_id": "settings"
    },
    {
        "label": "角色管理",
        "icon": "ep:avatar",
        "name": "role",
        "status": 1,
        "path": "/role",
        "is_menu": 1,
        "sort": 3,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "settings"
    },
    {
        "label": "菜单管理",
        "icon": "ep:menu",
        "name": "menu",
        "status": 1,
        "path": "/menu",
        "is_menu": 1,
        "sort": 4,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "settings"
    },

    {
        "label": "门户配置",
        "icon": "ep:platform",
        "name": "portal",
        "status": 1,
        "path": "/portal",
        "is_menu": 1,
        "sort": 5,
        "has_info": 1,
        "info_view_name": "test",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "settings"
    },
    {
        "label": "数据源配置",
        "icon": "ep:list",
        "name": "datasource",
        "status": 1,
        "path": "/datasource",
        "is_menu": 1,
        "sort": 6,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "settings"
    },
    {
        "label": "系统参数",
        "icon": "carbon:cloud-satellite-config",
        "name": "sysconfig",
        "status": 1,
        "path": "/sysconfig",
        "is_menu": 1,
        "sort": 7,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": "settings"
    },
    {
        "label": "其它",
        "icon": "ep:tools",
        "name": "other",
        "status": 0,
        "path": "/other",
        "is_menu": 1,
        "sort": 6,
        "has_info": 0,
        "info_view_name": '',
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": ''
    },
    {
        "label": "工具集",
        "icon": "ep:fork-spoon",
        "name": "tools",
        "status": 1,
        "path": "tools",
        "is_menu": 1,
        "sort": 99,
        "has_info": 0,
        "info_view_name": "",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "keepalive": 1,
        "parentid_id": ''
    },
    {
        "label": "测试页1",
        "icon": "ep:promotion",
        "name": "debug",
        "status": 0,
        "path": "debug",
        "is_menu": 1,
        "sort": 100,
        "has_info": 0,
        "info_view_name": "",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "parentid_id": ''
    },
    {
        "label": "测试页2",
        "icon": "ep:promotion",
        "name": "test",
        "status": 0,
        "path": "test",
        "is_menu": 1,
        "sort": 100,
        "has_info": 0,
        "info_view_name": "",
        "is_iframe": 0,
        "iframe_url": '',
        "description": "",
        "parentid_id": ''
    }
]

INIT_CONFIG = [
    {
        "verbose_name": "sm4加密key",
        "param_name": "secret_key",
        "param_value": get_uuid(),
        "param_type": "string",
        "description": "",
    },
    {
        "verbose_name":"sm4加密模式",
        "param_name":"secret_mode",
        "param_value": "ecb",
        "param_type": "string",
        "description":"",
    },
    {
        "verbose_name": "开启同步",
        "param_name": "zabbix_is_sync",
        "param_value": 1,
        "param_type": "int",
        "description":"是否开启资产同步zabbix监控",
    },
    {
        "verbose_name":"zabbix地址",
        "param_name":"zabbix_url",
        "param_value": os.environ.get('ZABBIX_URL', ''),
        "param_type": "string",
        "description":"例如: http://127.0.0.1/api_jsonrpc.php",
    },
    {
        "verbose_name":"zabbix-server的IP",
        "param_name":"zabbix_server",
        "param_type": "string",
        "param_value": os.environ.get('ZABBIX_SERVER', '127.0.0.1'),
        "description":"例如: zabbix-server的IP地址",
    },
    {
        "verbose_name":"zabbix管理用户",
        "param_name":"zabbix_username",
        "param_type": "string",
        "param_value": os.environ.get('ZABBIX_USERNAME', 'Admin'),
        "description":"",
    },
    {
        "verbose_name":"密码",
        "param_name":"zabbix_password",
        "param_type": "string",
        "param_value": os.environ.get('ZABBIX_PASSWORD', 'zabbix'),
        "description":"",
    },
    {
        "verbose_name":"主机模板",
        "param_name": "zabbix_host_template",
        "param_type": "string",
        "param_value": os.environ.get('ZABBIX_DEFAULT_HOST_TEMPLATE'),
        "description":"填写zabbix主机监控模板的名称(全英文，不是模板可见名称!)",
    },
    {
        "verbose_name":"network模板",
        "param_name": "zabbix_network_template",
        "param_type": "string",
        "param_value": os.environ.get('ZABBIX_DEFAULT_NETWORK_TEMPLATE'),
        "description":"填写zabbix网络监控模板的名称(全英文，不是模板可见名称!)",
    },
    {
        "verbose_name":"token注销时间",
        "param_name":"zabbix_interval",
        "param_type": "int",
        "param_value": os.environ.get('ZABBIX_INTERVAL', 0),
        "description":"单位秒,0表示不过期",
    },

]