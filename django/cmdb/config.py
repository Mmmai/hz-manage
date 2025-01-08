# config.py


re_pattern = {
    'ipv4': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
    'ipv6': r'^(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$',
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^1[3-9]\d{9}$',
    'URL': r'^https?://\S+$',
}


BUILT_IN_MODELS = {
    'rooms': {
        'verbose_name': '机房',
        'description': '机房资源管理',
        'model_group': 'resource',
        'icon': 'clarity:building-line',
        'fields': [
            {
                'name': 'room_name',
                'type': 'string',
                'verbose_name': '机房名称',
                'required': True,
                'editable': True,
                'order': 1
            },
            {
                'name': 'address',
                'type': 'string',
                'verbose_name': '机房地址',
                'required': True,
                'editable': True,
                'order': 2
            },
            {
                'name': 'contact',
                'type': 'string',
                'verbose_name': '联系人',
                'required': True,
                'editable': True,
                'order': 3
            },
            {
                'name': 'phone',
                'type': 'string',
                'verbose_name': '联系电话',
                'required': True,
                'editable': True,
                'order': 4,
                'validation_rule': 'phone'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True,
                'order': 5
            }
        ]
    },
    'cabinets': {
        'verbose_name': '机柜',
        'description': '机柜资源管理',
        'model_group': 'resource',
        'icon': 'mdi:file-cabinet',
        'fields': [
            {
                'name': 'cabinet_name',
                'type': 'string',
                'verbose_name': '机柜编号',
                'required': True,
                'editable': True,
                'order': 1
            },
            {
                'name': 'room',
                'type': 'model_ref',
                'verbose_name': '所属机房',
                'required': True,
                'editable': True,
                'ref_model': 'rooms',
                'order': 2
            },
            {
                'name': 'capacity',
                'type': 'integer',
                'verbose_name': '总U位',
                'required': True,
                'editable': True,
                'order': 3
            },
            {
                'name': 'power',
                'type': 'float',
                'verbose_name': '功率',
                'required': False,
                'editable': True,
                'order': 4
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True,
                'order': 5
            }
        ]
    },
    'projects': {
        'verbose_name': '项目',
        'description': '项目管理',
        'model_group': 'resource',
        'icon': 'octicon:project-roadmap-24',
        'fields': [
            {
                'name': 'project_name',
                'type': 'string',
                'verbose_name': '项目名称',
                'required': True,
                'editable': True,
                'order': 1
            },
            {
                'name': 'project_code',
                'type': 'string',
                'verbose_name': '项目编号',
                'required': True,
                'editable': True,
                'order': 2
            },
            {
                'name': 'manager',
                'type': 'string',
                'verbose_name': '项目经理',
                'required': True,
                'editable': True,
                'order': 3
            },
            {
                'name': 'status',
                'type': 'enum',
                'verbose_name': '项目状态',
                'required': True,
                'editable': True,
                'order': 4
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True,
                'order': 5
            }
        ]
    },
    'hosts': {
        'verbose_name': '主机',
        'description': '主机资源管理', 
        'model_group': 'host',
        'icon': 'clarity:host-line',
        'fields': [
            # 基础配置字段
            {
                'name': 'ip',
                'type': 'string',
                'verbose_name': '业务IP',
                'required': True,
                'editable': True,
                'order': 1,
                'validation_rule': 'ip'
            },
            {
                'name': 'mgmt_ip',
                'type': 'string', 
                'verbose_name': 'BMC IP',
                'required': False,
                'editable': True,
                'order': 2,
                'validation_rule': 'ip'
            },
            {
                'name': 'cluster_ip',
                'type': 'string',
                'verbose_name': '管理IP',
                'required': False,
                'editable': True,
                'order': 3,
                'validation_rule': 'ip'
            },
            {
                'name': 'project_name',
                'type': 'model_ref',
                'verbose_name': '项目名称',
                'ref_model': 'projects',
                'required': False,
                'editable': True,
                'order': 6
            },
            {
                'name': 'operator',
                'type': 'string',
                'verbose_name': '运维负责人',
                'required': False,
                'editable': True,
                'order': 7
            },
            {
                'name': 'operator_backup',
                'type': 'string',
                'verbose_name': '备用负责人',
                'required': False,
                'editable': True,
                'order': 8
            },
            {
                'name': 'asset_id',
                'type': 'string',
                'verbose_name': '资产编号',
                'required': False,
                'editable': True,
                'order': 9
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'verbose_name': '序列号',
                'required': False,
                'editable': True,
                'order': 10
            },
            {
                'name': 'mgmt_user',
                'type': 'string',
                'verbose_name': '管理用户',
                'required': False,
                'editable': True,
                'order': 11
            },
            {
                'name': 'mgmt_password',
                'type': 'password',
                'verbose_name': '管理密码',
                'required': False,
                'editable': True,
                'order': 12
            },
            {
                'name': 'root_password',
                'type': 'password',
                'verbose_name': 'ROOT密码',
                'required': True,
                'editable': True,
                'order': 13
            },
            {
                'name': 'device_status',
                'type': 'enum',
                'verbose_name': '设备状态',
                'required': True,
                'editable': True,
                'order': 14,
                'validation_rule': 'device_status'
            },
            {
                'name': 'comment',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True,
                'order': 15
            },
            
            # 设备详情字段
            {
                'name': 'hostname',
                'type': 'string',
                'verbose_name': '主机名',
                'required': False,
                'editable': True,
                'order': 16,
                'validation_rule': 'hostname'
            },
            {
                'name': 'os_type',
                'type': 'enum',
                'verbose_name': '操作系统类型',
                'default': 'linux',
                'required': False,
                'editable': True,
                'order': 17,
                'validation_rule': 'os_type'
            },
            {
                'name': 'os_name',
                'type': 'string',
                'verbose_name': '操作系统名称',
                'required': False,
                'editable': True,
                'order': 18
            },
            {
                'name': 'os_version',
                'type': 'string',
                'verbose_name': '操作系统版本',
                'required': False,
                'editable': True,
                'order': 19
            },
            {
                'name': 'os_bit',
                'type': 'string',
                'verbose_name': '系统位数',
                'required': False,
                'editable': True,
                'order': 20
            },
            {
                'name': 'warranty_term',
                'type': 'string',
                'verbose_name': '质保期限',
                'required': False,
                'editable': True,
                'order': 21
            },
            {
                'name': 'province_name',
                'type': 'enum',
                'verbose_name': '省份',
                'required': False,
                'editable': True,
                'order': 22,
                'validation_rule': 'province'
            },
            {
                'name': 'city_name',
                'type': 'enum',
                'verbose_name': '城市',
                'required': False,
                'editable': True,
                'order': 23,
                'validation_rule': 'city'
            },
            {
                'name': 'isp_name',
                'type': 'enum',
                'verbose_name': '运营商',
                'required': False,
                'editable': True,
                'order': 24,
                'validation_rule': 'isp'
            },
            {
                'name': 'room',
                'type': 'model_ref',
                'verbose_name': '机房',
                'ref_model': 'rooms',
                'required': True,
                'editable': True,
                'order': 25
            },
            {
                'name': 'cabinet',
                'type': 'model_ref',
                'verbose_name': '机柜',
                'ref_model': 'cabinets',
                'required': True,
                'editable': True,
                'order': 26
            },
            {
                'name': 'cabinet_position',
                'type': 'string',
                'verbose_name': 'U位',
                'required': True,
                'editable': True,
                'order': 27
            },
            {
                'name': 'device_purpose',
                'type': 'string',
                'verbose_name': '设备用途',
                'required': False,
                'editable': True,
                'order': 28
            },
            {
                'name': 'device_config',
                'type': 'text',
                'verbose_name': '设备配置',
                'required': False,
                'editable': True,
                'order': 29
            },
            {
                'name': 'online_time',
                'type': 'datetime',
                'verbose_name': '上线时间',
                'required': False,
                'editable': True,
                'order': 30,
                'validation_rule': 'datetime'
            },
            {
                'name': 'public_config',
                'type': 'text',
                'verbose_name': '对外配置',
                'required': False,
                'editable': True,
                'order': 31
            },
            {
                'name': 'public_model',
                'type': 'string',
                'verbose_name': '对外型号',
                'required': False,
                'editable': True,
                'order': 32
            },
            {
                'name': 'is_special',
                'type': 'boolean',
                'verbose_name': '专用设备',
                'required': False,
                'editable': True,
                'order': 33,
                'validation_rule': 'boolean'
            },
            {
                'name': 'warranty_expiration',
                'type': 'datetime',
                'verbose_name': '质保到期时间',
                'required': False,
                'editable': True,
                'order': 34,
                'validation_rule': 'datetime'
            },
            {
                'name': 'create_time',
                'type': 'datetime',
                'verbose_name': '录入时间',
                'required': False,
                'editable': True,
                'order': 35,
                'validation_rule': 'datetime'
            },
            {
                'name': 'import_from',
                'type': 'enum',
                'verbose_name': '录入方式',
                'required': False,
                'editable': True,
                'order': 36,
                'validation_rule': 'import_from'
            },
            {
                'name': 'device_name',
                'type': 'string',
                'verbose_name': '设备名称',
                'required': False,
                'editable': True,
                'order': 37
            },
            {
                'name': 'device_model',
                'type': 'string',
                'verbose_name': '设备型号',
                'required': False,
                'editable': True,
                'order': 38
            },
            
            # 自动发现字段
            {
                'name': 'cpu_info',
                'type': 'json',
                'verbose_name': 'CPU信息',
                'required': False,
                'editable': True,
                'order': 39,
                'validation_rule': 'json'
            },
            {
                'name': 'memory_info',
                'type': 'json',
                'verbose_name': '内存信息',
                'required': False,
                'editable': True,
                'order': 40,
                'validation_rule': 'json'
            },
            {
                'name': 'disk_info',
                'type': 'json',
                'verbose_name': '磁盘信息',
                'required': False,
                'editable': True,
                'order': 41,
                'validation_rule': 'json'
            },
            {
                'name': 'disk_size',
                'type': 'float',
                'verbose_name': '磁盘总大小',
                'required': False,
                'editable': True,
                'order': 42
            }
        ]
    },
    'switches': {
        'verbose_name': '交换机',
        'description': '交换机设备管理',
        'model_group': 'network',
        'icon': 'clarity:network-switch-line',
        'fields': [
            {
                'name': 'ip',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '管理IP地址',
                'order': 1,
                'validation_rule': 'ip'
            },
            {
                'name': 'vendor',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '厂商',
                'order': 2,
                'validation_rule': 'switch_vendor'
            },
            {
                'name': 'device_model',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '设备型号',
                'order': 3
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '序列号',
                'order': 4
            },
            {
                'name': 'ports',
                'type': 'integer',
                'required': True,
                'editable': True,
                'verbose_name': '端口数量',
                'order': 5
            },
            {
                'name': 'firmware_version',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '固件版本',
                'order': 6
            },
            {
                'name': 'remarks',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '备注信息',
                'order': 7
            }
        ]
    },
    'firewalls': {
        'verbose_name': '防火墙',
        'description': '防火墙设备管理',
        'model_group': 'security',
        'icon': 'clarity:firewall-line',
        'fields': [
            {
                'name': 'ip',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '管理IP地址',
                'order': 1,
                'validation_rule': 'ip'
            },
            {
                'name': 'vendor',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '厂商',
                'order': 2,
                'validation_rule': 'firewall_vendor'
            },
            {
                'name': 'device_model',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '设备型号',
                'order': 3
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '序列号',
                'order': 4
            },
            {
                'name': 'firmware_version',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '固件版本',
                'order': 5
            },
            {
                'name': 'ha_status',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': 'HA状态',
                'order': 6,
                'validation_rule': 'ha_status'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '备注信息',
                'order': 7
            }
        ]
    },
    'dwdm': {
        'verbose_name': '波分设备',
        'description': '波分复用设备管理',
        'model_group': 'network',
        'icon': 'clarity:bundle-line',
        'fields': [
            {
                'name': 'ip',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '管理IP地址',
                'order': 1,
                'validation_rule': 'ip'
            },
            {
                'name': 'vendor',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '厂商',
                'order': 2,
                'validation_rule': 'dwdm_vendor'
            },
            {
                'name': 'device_model',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '设备型号',
                'order': 3
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '序列号',
                'order': 4
            },
            {
                'name': 'wavelength_number',
                'type': 'integer',
                'required': True,
                'editable': True,
                'verbose_name': '波长数量',
                'order': 5
            },
            {
                'name': 'transmission_rate',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '传输速率',
                'order': 6
            },
            {
                'name': 'remarks',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '备注信息',
                'order': 7
            }
        ],
    },
}

# 添加到内置验证规则配置
BUILT_IN_VALIDATION_RULES = {
    'ip': {
        'name': 'ip',
        'verbose_name': 'IP地址',
        'field_type': 'string',
        'type': 'ip',
        'rule': re_pattern['ipv4'] + '|' + re_pattern['ipv6'],
        'editable': False,
        'description': 'IP地址格式验证(支持IPv4和IPv6)'
    },
    'ipv4': {
        'name': 'ipv4',
        'verbose_name': 'IPv4地址',
        'field_type': 'string',
        'type': 'ipv4',
        'rule': re_pattern['ipv4'],
        'editable': False,
        'description': 'IPv4地址格式验证'
    },
    'ipv6': {
        'name': 'ipv6',
        'verbose_name': 'IPv6地址',
        'field_type': 'string',
        'type': 'ipv6',
        'rule': re_pattern['ipv6'],
        'editable': False,
        'description': 'IPv6地址格式验证'
    },
    'email': {
        'verbose_name': '邮箱校验',
        'field_type': 'string',
        'type': 'email',
        'rule': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'editable': False,
        'description': '验证邮箱地址格式'
    },
    'phone': {
        'verbose_name': '手机号校验',
        'field_type': 'string',
        'type': 'phone',
        'rule': r'^1[3-9]\d{9}$',
        'editable': False,
        'description': '验证中国大陆手机号格式'
    }, 
    'url': {
        'verbose_name': 'URL校验',
        'field_type': 'string',
        'type': 'url',
        'rule': r'^https?://\S+$',
        'editable': False,
        'description': '验证URL地址格式'
    },
    'json': {
        'verbose_name': 'JSON校验',
        'field_type': 'json',
        'type': 'json',
        'rule': '',
        'editable': False,
        'description': '验证JSON格式'
    },
    'date': {
        'verbose_name': '日期校验',
        'field_type': 'date',
        'type': 'date',
        'rule': '',
        'editable': False,
        'description': '验证日期格式'
    },
    'datetime': {
        'verbose_name': '日期时间校验',
        'field_type': 'datetime',
        'type': 'datetime',
        'rule': '',
        'editable': False,
        'description': '验证日期时间格式'
    },
    'timestamp': {
        'verbose_name': '时间戳校验',
        'field_type': 'datetime',
        'type': 'timestamp',
        'rule': '',
        'editable': False,
        'description': '验证时间戳格式'
    },
    'boolean': {
        'verbose_name': '布尔值校验',
        'field_type': 'boolean',
        'type': 'boolean',
        'rule': '',
        'editable': False,
        'description': '验证布尔值格式' 
    },
    'host_architecture': {
        'verbose_name': '主机架构',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"x86_64\": \"x86_64架构\", \"aarch64\": \"ARM64架构\"}",
        'description': '主机系统架构'
    },
    'host_vendor': {
        'verbose_name': '主机厂商',
        'field_type': 'enum',
        'type': 'enum',
        "rule": "{\"huawei\": \"华为\", \"h3c\": \"新华三\", \"sugon\": \"曙光\", \"zte\": \"中兴\", \"lenovo\": \"联想\", \"other\": \"其他\"}",
        'description': '主机厂商列表'
    },
    'switch_vendor': {
        'verbose_name': '交换机厂商',
        'field_type': 'enum',
        'type': 'enum',
        "rule": "{\"huawei\": \"华为\", \"h3c\": \"新华三\", \"zte\": \"中兴\", \"ruijie\": \"锐捷\", \"other\": \"其他\"}",
        'description': '交换机厂商列表'
    },
    'firewall_vendor': {
        'verbose_name': '防火墙厂商',
        'field_type': 'enum', 
        'type': 'enum',
        "rule": "{\"huawei\": \"华为\", \"h3c\": \"新华三\", \"hillstone\": \"山石网科\", \"venustech\": \"启明星辰\", \"other\": \"其他\"}",
        'description': '防火墙厂商列表'
    },
    'vpn_vendor': {
        'verbose_name': 'VPN设备厂商',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"huawei\": \"华为\", \"sangfor\": \"深信服\", \"qi-anxin\": \"奇安信\", \"venustech\": \"启明星辰\", \"other\": \"其他\"}",
        'description': 'VPN设备厂商列表'
    },
    'dwdm_vendor': {
        'verbose_name': '波分设备厂商',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"huawei\": \"华为\", \"zte\": \"中兴\", \"fiberhome\": \"烽火\", \"other\": \"其他\"}",
        'description': '波分设备厂商列表'
    },
    'ha_status': {
        'verbose_name': 'HA状态',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"master\": \"主设备\", \"slave\": \"从设备\", \"standalone\": \"独立设备\"}",
        'description': '高可用状态'
    },
    'vpn_type': {
        'verbose_name': 'VPN类型',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"ssl-vpn\": \"SSL VPN\", \"ipsec-vpn\": \"IPSec VPN\", \"other\": \"其他类型\"}",
        'description': 'VPN连接类型'
    },
    'province': {
        'verbose_name': '省份',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"beijing\": \"北京\", \"shanghai\": \"上海\", \"guangdong\": \"广东\", \"jiangsu\": \"江苏\", \"zhejiang\": \"浙江\", \"shandong\": \"山东\", \"henan\": \"河南\", \"sichuan\": \"四川\", \"hubei\": \"湖北\", \"hebei\": \"河北\", \"shanxi\": \"山西\", \"neimenggu\": \"内蒙古\", \"liaoning\": \"辽宁\", \"jilin\": \"吉林\", \"heilongjiang\": \"黑龙江\", \"jiangxi\": \"江西\", \"fujian\": \"福建\", \"anhui\": \"安徽\", \"guangxi\": \"广西\", \"hainan\": \"海南\", \"chongqing\": \"重庆\", \"hunan\": \"湖南\", \"guizhou\": \"贵州\", \"yunnan\": \"云南\", \"xizang\": \"西藏\", \"shanxi\": \"陕西\", \"gansu\": \"甘肃\", \"qinghai\": \"青海\", \"ningxia\": \"宁夏\", \"xinjiang\": \"新疆\", \"taiwan\": \"台湾\", \"hongkong\": \"香港\", \"macao\": \"澳门\"}",
        'description': '省份列表'
    },
    'city': {
        'verbose_name': '城市',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"corps\": \"总队\"}",
        'description': '城市列表'
    },
    'isp': {
        'verbose_name': '运营商',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"unicom\": \"联通\", \"mobile\": \"移动\", \"telecom\": \"电信\", \"cbn\":\"广电\", \"other\": \"其他\"}",
        'description': '运营商列表'
    },
    'hostname': {
        'verbose_name': '主机名校验',
        'field_type': 'string',
        'type': 'regex',
        'rule': '^[a-zA-Z][a-zA-Z0-9-]{1,63}$',
        'editable': False,
        'description': '主机名格式校验',
        'validation_rule': 'hostname'
    },
    'port_range': {
        'verbose_name': '端口范围',
        'field_type': 'integer',
        'type': 'range',
        'rule': '1,65535',
        'editable': False,
        'description': '有效端口范围1-65535'
    },
    'price_range': {
        'verbose_name': '价格范围',
        'field_type': 'float',
        'type': 'range',
        'rule': '0,1000000000',
        'editable': False,
        'description': '价格范围0-1000000000'
    },
    'import_from': {
        'verbose_name': '录入方式',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"manual\": \"手动录入\", \"import\": \"表格导入\", \"auto\": \"自动发现\"}",
        'description': '设备录入方式'
    },
    'device_status': {
        'verbose_name': '设备状态',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"in-use\": \"在用\", \"standby\": \"备用\", \"idle\": \"闲置\", \"disabled\": \"停用\", \"fault\": \"故障\"}",
        'description': '设备状态'
    },
    'os_type': {
        'verbose_name': '操作系统类型',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"linux\": \"Linux\", \"windows\": \"Windows\", \"unix\": \"Unix\", \"other\": \"其他\"}",
        'description': '操作系统类型'
    },
}
