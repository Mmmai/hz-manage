# config.py


re_pattern = {
    'ipv4': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
    'ipv6': r'^(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$',
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^1[3-9]\d{9}$',
    'URL': r'^https?://\S+$',
}

BUILT_IN_MODELS = {
    'hosts': {
        'verbose_name': '主机',
        'description': '主机资源管理',
        'model_group': 'host',
        'icon': 'Box',
        'fields': [
            {
                'name': 'ip',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '业务IP地址',
                'order': 1,
                'validation_rule': 'ip'
            },
            {
                'name': 'mgmt_ip',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '管理IP地址',
                'order': 2,
                'validation_rule': 'ip'
            },
            {
                'name': 'vendor',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '厂商',
                'order': 3,
                'validation_rule': 'host_vendor'
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '序列号',
                'order': 4
            },
            {
                'name': 'architecture',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '系统架构',
                'order': 5,
                'validation_rule': 'host_architecture'
            },
            {
                'name': 'cpu_info',
                'type': 'json',
                'required': False,
                'editable': True,
                'verbose_name': 'CPU信息',
                'order': 6,
                'validation_rule': 'json'
            },
            {
                'name': 'memory_info',
                'type': 'json',
                'required': False,
                'editable': True,
                'verbose_name': '内存信息',
                'order': 7,
                'validation_rule': 'json'
            },
            {
                'name': 'os_arch',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '系统位数',
                'order': 8
            },
            {
                'name': 'os_version',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '操作系统版本',
                'order': 9
            },
            {
                'name': 'os_kernel_version',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '操作系统内核版本',
                'order': 10
            },
            {
                'name': 'hostname',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '主机名',
                'order': 11
            },
            {
                'name': 'remarks',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '备注信息',
                'order': 12
            },
            {
                'name': 'enabled_at',
                'type': 'datetime',
                'required': False,
                'editable': True,
                'verbose_name': '启用时间',
                'order': 13
            },
            {
                'name': 'fault_status',
                'type': 'boolean',
                'required': False,
                'editable': True,
                'verbose_name': '故障状态',
                'order': 14
            },
            {
                'name': 'price',
                'type': 'float',
                'required': False,
                'editable': True,
                'verbose_name': '价格',
                'order': 15,
                'validation_rule': 'price_range'
            }
        ]
    },
    'switches': {
        'verbose_name': '交换机',
        'description': '交换机设备管理',
        'model_group': 'network',
        'icon': 'Box',
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
                'name': 'model',
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
        'icon': 'Box',
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
                'name': 'model',
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
    'vpn': {
        'verbose_name': 'VPN设备',
        'description': 'VPN设备管理',
        'model_group': 'security',
        'icon': 'Box',
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
                'validation_rule': 'vpn_vendor'
            },
            {
                'name': 'model',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '设备型号',
                'order': 3
            },
            {
                'name': 'vpn_type',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': 'VPN类型',
                'order': 4,
                'validation_rule': 'vpn_type'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '备注信息',
                'order': 5
            }
        ]
    },
    'dwdm': {
        'verbose_name': '波分设备',
        'description': '波分复用设备管理',
        'model_group': 'network',
        'icon': 'Box',
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
                'name': 'model',
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
        ]
    }
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
    }
}
