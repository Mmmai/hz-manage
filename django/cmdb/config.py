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
                'editable': True
            },
            {
                'name': 'address',
                'type': 'string',
                'verbose_name': '机房地址',
                'required': True,
                'editable': True
            },
            {
                'name': 'contact',
                'type': 'string',
                'verbose_name': '联系人',
                'required': False,
                'editable': True
            },
            {
                'name': 'province_name',
                'type': 'enum',
                'verbose_name': '省份',
                'required': False,
                'editable': True,
                'validation_rule': 'province'
            },
            {
                'name': 'city_name',
                'type': 'enum',
                'verbose_name': '城市',
                'required': False,
                'editable': True,
                'validation_rule': 'city'
            },
            {
                'name': 'isp_name',
                'type': 'enum',
                'verbose_name': '运营商',
                'required': False,
                'editable': True,
                'validation_rule': 'isp'
            },
            {
                'name': 'phone',
                'type': 'string',
                'verbose_name': '联系电话',
                'required': False,
                'editable': True,
                'validation_rule': 'phone'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
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
                'editable': True
            },
            {
                'name': 'room',
                'type': 'model_ref',
                'verbose_name': '所属机房',
                'required': True,
                'editable': True,
                'ref_model': 'rooms'
            },
            {
                'name': 'capacity',
                'type': 'integer',
                'verbose_name': '总U位',
                'required': True,
                'editable': True
            },
            {
                'name': 'power',
                'type': 'float',
                'verbose_name': '功率',
                'required': False,
                'editable': True
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
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
                'editable': True
            },
            {
                'name': 'project_code',
                'type': 'string',
                'verbose_name': '项目编号',
                'required': True,
                'editable': True
            },
            {
                'name': 'contract_code',
                'type': 'string',
                'verbose_name': '客户合同编号',
                'required': False,
                'editable': True
            },
            {
                'name': 'contract_duration',
                'type': 'datetime',
                'verbose_name': '合同工期要求',
                'required': False,
                'editable': True
            },
            {
                'name': 'client_org',
                'type': 'string',
                'verbose_name': '甲方单位',
                'required': True,
                'editable': True,
                'validation_rule': 'organization'
            },
            {
                'name': 'supervisor_org',
                'type': 'string',
                'verbose_name': '监理单位',
                'required': False,
                'editable': True
            },
            {
                'name': 'manager',
                'type': 'string',
                'verbose_name': '项目经理',
                'required': True,
                'editable': True
            },
            {
                'name': 'status',
                'type': 'enum',
                'verbose_name': '项目状态',
                'required': True,
                'editable': True,
                'validation_rule': 'project_status'
            },
            {
                'name': 'preliminary_acceptance_time',
                'type': 'datetime',
                'verbose_name': '初验时间',
                'required': False,
                'editable': True
            },
            {
                'name': 'final_acceptance_time',
                'type': 'datetime',
                'verbose_name': '终验时间',
                'required': False,
                'editable': True
            },
            {
                'name': 'warranty_expiration',
                'type': 'datetime',
                'verbose_name': '维保到期时间',
                'required': False,
                'editable': True
            },
            {
                'name': 'security_level',
                'type': 'enum',
                'verbose_name': '密级',
                'required': True,
                'editable': True,
                'validation_rule': 'project_security_level'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
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
                'validation_rule': 'ip'
            },
            {
                'name': 'mgmt_ip',
                'type': 'string',
                'verbose_name': 'BMC IP',
                'required': False,
                'editable': True,
                'validation_rule': 'ip'
            },
            {
                'name': 'cluster_ip',
                'type': 'string',
                'verbose_name': '管理IP',
                'required': False,
                'editable': True,
                'validation_rule': 'ip'
            },
            {
                'name': 'business',
                'type': 'enum',
                'verbose_name': '业务',
                'required': True,
                'editable': True,
                'validation_rule': 'business'
            },
            {
                'name': 'asset_owner',
                'type': 'string',
                'verbose_name': '资产归属',
                'required': True,
                'editable': True,
                'validation_rule': 'organization'
            },
            {
                'name': 'vendor_agent',
                'type': 'string',
                'verbose_name': '设备代理商',
                'required': False,
                'editable': True
            },
            {
                'name': 'project_name',
                'type': 'model_ref',
                'verbose_name': '项目名称',
                'ref_model': 'projects',
                'required': False,
                'editable': True
            },
            {
                'name': 'asset_id',
                'type': 'string',
                'verbose_name': '资产编号',
                'required': False,
                'editable': True
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'verbose_name': '序列号',
                'required': False,
                'editable': True
            },
            {
                'name': 'mgmt_user',
                'type': 'string',
                'verbose_name': '管理用户',
                'required': False,
                'editable': True
            },
            {
                'name': 'mgmt_password',
                'type': 'password',
                'verbose_name': '管理密码',
                'required': False,
                'editable': True
            },
            {
                'name': 'system_user',
                'type': 'string',
                'verbose_name': '系统用户',
                'required': True,
                'editable': True
            },
            {
                'name': 'system_password',
                'type': 'password',
                'verbose_name': '用户密码',
                'required': True,
                'editable': True
            },
            {
                'name': 'device_status',
                'type': 'enum',
                'verbose_name': '设备状态',
                'required': True,
                'editable': True,
                'validation_rule': 'device_status'
            },
            {
                'name': 'comment',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
            },
            {
                'name': 'warranty_term',
                'type': 'string',
                'verbose_name': '质保期限',
                'required': False,
                'editable': True
            },
            {
                'name': 'province_name',
                'type': 'enum',
                'verbose_name': '省份',
                'required': False,
                'editable': True,
                'validation_rule': 'province'
            },
            {
                'name': 'city_name',
                'type': 'enum',
                'verbose_name': '城市',
                'required': False,
                'editable': True,
                'validation_rule': 'city'
            },
            {
                'name': 'isp_name',
                'type': 'enum',
                'verbose_name': '运营商',
                'required': False,
                'editable': True,
                'validation_rule': 'isp'
            },
            {
                'name': 'room',
                'type': 'model_ref',
                'verbose_name': '机房',
                'ref_model': 'rooms',
                'required': True,
                'editable': True
            },
            {
                'name': 'cabinet',
                'type': 'model_ref',
                'verbose_name': '机柜',
                'ref_model': 'cabinets',
                'required': True,
                'editable': True
            },
            {
                'name': 'cabinet_position',
                'type': 'string',
                'verbose_name': 'U位',
                'required': True,
                'editable': True,
                'description': '填写样例：3-5 / 3-5U / 3U-5U',
                'validation_rule': 'cabinet_position'
            },
            {
                'name': 'device_purpose',
                'type': 'string',
                'verbose_name': '设备用途',
                'required': False,
                'editable': True
            },
            {
                'name': 'device_config',
                'type': 'text',
                'verbose_name': '设备配置',
                'required': False,
                'editable': True
            },
            {
                'name': 'online_time',
                'type': 'datetime',
                'verbose_name': '上线时间',
                'required': False,
                'editable': True,
                'validation_rule': 'datetime'
            },
            {
                'name': 'contract_device_name',
                'type': 'string',
                'verbose_name': '合同设备名称',
                'required': False,
                'editable': True
            },
            {
                'name': 'public_config',
                'type': 'text',
                'verbose_name': '对外配置',
                'required': False,
                'editable': True
            },
            {
                'name': 'public_model',
                'type': 'string',
                'verbose_name': '对外型号',
                'required': False,
                'editable': True
            },
            {
                'name': 'is_special',
                'type': 'boolean',
                'verbose_name': '专用设备',
                'required': False,
                'editable': True,
                'validation_rule': 'boolean'
            },
            {
                'name': 'warranty_expiration',
                'type': 'datetime',
                'verbose_name': '质保到期时间',
                'required': False,
                'editable': True,
                'validation_rule': 'datetime'
            },
            {
                'name': 'device_name',
                'type': 'string',
                'verbose_name': '设备名称',
                'required': False,
                'editable': True
            },
            {
                'name': 'device_model',
                'type': 'string',
                'verbose_name': '设备型号',
                'required': False,
                'editable': True
            },

            # 自动发现分组字段
            {
                'name': 'hostname',
                'type': 'string',
                'verbose_name': '主机名',
                'required': False,
                'editable': True,
                'validation_rule': 'hostname',
                'group': 'auto_discover'
            },
            {
                'name': 'os_type',
                'type': 'enum',
                'verbose_name': '操作系统类型',
                'default': 'linux',
                'required': False,
                'editable': True,
                'validation_rule': 'os_type',
                'group': 'auto_discover'
            },
            {
                'name': 'os_name',
                'type': 'string',
                'verbose_name': '操作系统名称',
                'required': False,
                'editable': True,
                'group': 'auto_discover'
            },
            {
                'name': 'os_version',
                'type': 'string',
                'verbose_name': '操作系统版本',
                'required': False,
                'editable': True,
                'group': 'auto_discover'
            },
            {
                'name': 'os_arch',
                'type': 'enum',
                'verbose_name': '系统架构',
                'required': False,
                'editable': True,
                'validation_rule': 'host_architecture',
                'group': 'auto_discover'
            },
            {
                'name': 'os_bit',
                'type': 'string',
                'verbose_name': '系统位数',
                'required': False,
                'editable': True,
                'group': 'auto_discover'
            },
            {
                'name': 'hardware_info',
                'type': 'json',
                'verbose_name': '硬件信息',
                'required': False,
                'editable': True,
                'validation_rule': 'json',
                'group': 'auto_discover'
            },
            {
                'name': 'cpu_info',
                'type': 'json',
                'verbose_name': 'CPU信息',
                'required': False,
                'editable': True,
                'validation_rule': 'json',
                'group': 'auto_discover'
            },
            {
                'name': 'memory_info',
                'type': 'json',
                'verbose_name': '内存信息',
                'required': False,
                'editable': True,
                'validation_rule': 'json',
                'group': 'auto_discover'
            },
            {
                'name': 'disk_info',
                'type': 'json',
                'verbose_name': '磁盘信息',
                'required': False,
                'editable': True,
                'validation_rule': 'json',
                'group': 'auto_discover'
            },
            {
                'name': 'disk_size',
                'type': 'float',
                'verbose_name': '磁盘总大小',
                'required': False,
                'editable': True,
                'group': 'auto_discover'
            }
        ]
    },
    'virtual_machines': {
        'verbose_name': '虚拟机',
        'description': '虚拟机或云主机资源管理',
        'model_group': 'host',
        'icon': 'clarity:host-group-line',
        'fields': [
            {
                'name': 'ip',
                'type': 'string',
                'verbose_name': '业务IP',
                'required': True,
                'editable': True,
                'validation_rule': 'ip'
            },
            {
                'name': 'mgmt_ip',
                'type': 'string',
                'verbose_name': 'BMC IP',
                'required': False,
                'editable': True,
                'validation_rule': 'ip'
            },
            {
                'name': 'business',
                'type': 'enum',
                'verbose_name': '业务',
                'required': True,
                'editable': True,
                'validation_rule': 'business'
            },
            {
                'name': 'system_user',
                'type': 'string',
                'verbose_name': '系统用户',
                'required': True,
                'editable': True
            },
            {
                'name': 'system_password',
                'type': 'password',
                'verbose_name': '用户密码',
                'required': True,
                'editable': True
            },
            {
                'name': 'device_status',
                'type': 'enum',
                'verbose_name': '设备状态',
                'required': True,
                'editable': True,
                'validation_rule': 'device_status'
            },
            {
                'name': 'comment',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
            },
            {
                'name': 'province_name',
                'type': 'enum',
                'verbose_name': '省份',
                'required': False,
                'editable': True,
                'validation_rule': 'province'
            },
            {
                'name': 'city_name',
                'type': 'enum',
                'verbose_name': '城市',
                'required': False,
                'editable': True,
                'validation_rule': 'city'
            },
            {
                'name': 'isp_name',
                'type': 'enum',
                'verbose_name': '运营商',
                'required': False,
                'editable': True,
                'validation_rule': 'isp'
            },
            {
                'name': 'device_purpose',
                'type': 'string',
                'verbose_name': '设备用途',
                'required': False,
                'editable': True
            },
            {
                'name': 'device_config',
                'type': 'text',
                'verbose_name': '设备配置',
                'required': False,
                'editable': True
            },
            {
                'name': 'online_time',
                'type': 'datetime',
                'verbose_name': '上线时间',
                'required': False,
                'editable': True
            },
            {
                'name': 'device_name',
                'type': 'string',
                'verbose_name': '设备名称',
                'required': False,
                'editable': True
            },
            {
                'name': 'vm_vendor',
                'type': 'string',
                'verbose_name': '虚拟化厂商',
                'required': True,
                'editable': True
            },
            {
                'name': 'hypervisor_name',
                'type': 'string',
                'verbose_name': '宿主机名称',
                'required': False,
                'editable': True
            },
            {
                'name': 'hypervisor_ip',
                'type': 'string',
                'verbose_name': '宿主机IP',
                'required': False,
                'editable': True,
                'validation_rule': 'ip'
            },
            {
                'name': 'hypervisor_mgmt_info',
                'type': 'text',
                'verbose_name': '宿主机管理信息',
                'required': False,
                'editable': True
            },
            {
                'name': 'vendor_agent',
                'type': 'string',
                'verbose_name': '设备代理商',
                'required': False,
                'editable': True
            },
            {
                'name': 'hostname',
                'type': 'string',
                'verbose_name': '主机名',
                'required': False,
                'editable': True,
                'validation_rule': 'hostname',
                'group': 'auto_discover'
            },
            {
                'name': 'os_type',
                'type': 'enum',
                'verbose_name': '操作系统类型',
                'required': False,
                'editable': True,
                'validation_rule': 'os_type',
                'group': 'auto_discover'
            },
            {
                'name': 'os_name',
                'type': 'string',
                'verbose_name': '操作系统名称',
                'required': False,
                'editable': True,
                'group': 'auto_discover'
            },
            {
                'name': 'os_version',
                'type': 'string',
                'verbose_name': '操作系统版本',
                'required': False,
                'editable': True,
                'group': 'auto_discover'
            },
            {
                'name': 'os_arch',
                'type': 'enum',
                'verbose_name': '系统架构',
                'required': False,
                'editable': True,
                'validation_rule': 'host_architecture',
                'group': 'auto_discover'
            },
            {
                'name': 'os_bit',
                'type': 'string',
                'verbose_name': '系统位数',
                'required': False,
                'editable': True,
                'group': 'auto_discover'
            },
            {
                'name': 'cpu_info',
                'type': 'json',
                'verbose_name': 'CPU信息',
                'required': False,
                'editable': True,
                'validation_rule': 'json',
                'group': 'auto_discover'
            },
            {
                'name': 'memory_info',
                'type': 'json',
                'verbose_name': '内存信息',
                'required': False,
                'editable': True,
                'validation_rule': 'json',
                'group': 'auto_discover'
            },
            {
                'name': 'hardware_info',
                'type': 'json',
                'verbose_name': '硬件信息',
                'required': False,
                'editable': True,
                'validation_rule': 'json',
                'group': 'auto_discover'
            },
            {
                'name': 'disk_info',
                'type': 'json',
                'verbose_name': '磁盘信息',
                'required': False,
                'editable': True,
                'validation_rule': 'json',
                'group': 'auto_discover'
            },
            {
                'name': 'disk_size',
                'type': 'float',
                'verbose_name': '磁盘总大小',
                'required': False,
                'editable': True,
                'group': 'auto_discover'
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
                'validation_rule': 'ip'
            },
            {
                'name': 'vendor',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '厂商',
                'validation_rule': 'switch_vendor'
            },
            {
                'name': 'device_model',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '设备型号'
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '序列号'
            },
            {
                'name': 'ports',
                'type': 'integer',
                'required': True,
                'editable': True,
                'verbose_name': '端口数量'
            },
            {
                'name': 'switch_type',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '交换机类型',
                'validation_rule': 'switch_type'
            },
            {
                'name': 'mgmt_user',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '管理用户'
            },
            {
                'name': 'mgmt_password',
                'type': 'password',
                'required': False,
                'editable': True,
                'verbose_name': '管理密码'
            },
            {
                'name': 'room',
                'type': 'model_ref',
                'required': True,
                'editable': True,
                'verbose_name': '机房',
                'ref_model': 'rooms'
            },
            {
                'name': 'cabinet',
                'type': 'model_ref',
                'required': True,
                'editable': True,
                'verbose_name': '机柜',
                'ref_model': 'cabinets'
            },
            {
                'name': 'cabinet_position',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': 'U位',
                'validation_rule': 'cabinet_position'
            },
            {
                'name': 'device_purpose',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '设备用途'
            },
            {
                'name': 'device_config',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '设备配置'
            },
            {
                'name': 'project_name',
                'type': 'model_ref',
                'required': False,
                'editable': True,
                'verbose_name': '项目名称',
                'ref_model': 'projects'
            },
            {
                'name': 'business',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '所属业务',
                'validation_rule': 'business'
            },
            {
                'name': 'online_time',
                'type': 'datetime',
                'required': False,
                'editable': True,
                'verbose_name': '上线时间'
            },
            {
                'name': 'warranty_expiration',
                'type': 'datetime',
                'required': False,
                'editable': True,
                'verbose_name': '质保到期时间'
            },
            {
                'name': 'device_status',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '设备状态',
                'validation_rule': 'device_status'
            },
            {
                'name': 'province_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '省份',
                'validation_rule': 'province'
            },
            {
                'name': 'city_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '城市',
                'validation_rule': 'city'
            },
            {
                'name': 'isp_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '运营商',
                'validation_rule': 'isp'
            },
            {
                'name': 'firmware_version',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '固件版本'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '备注信息'
            }
        ]
    },
    'npb': {
        'verbose_name': '汇聚分流器',
        'description': '汇聚分流设备管理',
        'model_group': 'network',
        'icon': 'clarity:router-line',
        'fields': [
            {
                'name': 'ip',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '管理IP地址',
                'validation_rule': 'ip'
            },
            {
                'name': 'vendor',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '厂商',
                'validation_rule': 'switch_vendor'
            },
            {
                'name': 'device_model',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '设备型号'
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '序列号'
            },
            {
                'name': 'ports',
                'type': 'integer',
                'required': True,
                'editable': True,
                'verbose_name': '端口数量'
            },
            {
                'name': 'mgmt_user',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '管理用户'
            },
            {
                'name': 'mgmt_password',
                'type': 'password',
                'required': False,
                'editable': True,
                'verbose_name': '管理密码'
            },
            {
                'name': 'room',
                'type': 'model_ref',
                'required': True,
                'editable': True,
                'verbose_name': '机房',
                'ref_model': 'rooms'
            },
            {
                'name': 'cabinet',
                'type': 'model_ref',
                'required': True,
                'editable': True,
                'verbose_name': '机柜',
                'ref_model': 'cabinets'
            },
            {
                'name': 'cabinet_position',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': 'U位',
                'validation_rule': 'cabinet_position'
            },
            {
                'name': 'device_purpose',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '设备用途'
            },
            {
                'name': 'device_config',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '设备配置'
            },
            {
                'name': 'project_name',
                'type': 'model_ref',
                'required': False,
                'editable': True,
                'verbose_name': '项目名称',
                'ref_model': 'projects'
            },
            {
                'name': 'business',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '所属业务',
                'validation_rule': 'business'
            },
            {
                'name': 'online_time',
                'type': 'datetime',
                'required': False,
                'editable': True,
                'verbose_name': '上线时间'
            },
            {
                'name': 'warranty_expiration',
                'type': 'datetime',
                'required': False,
                'editable': True,
                'verbose_name': '质保到期时间'
            },
            {
                'name': 'device_status',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '设备状态',
                'validation_rule': 'device_status'
            },
            {
                'name': 'province_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '省份',
                'validation_rule': 'province'
            },
            {
                'name': 'city_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '城市',
                'validation_rule': 'city'
            },
            {
                'name': 'isp_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '运营商',
                'validation_rule': 'isp'
            },
            {
                'name': 'firmware_version',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '固件版本'
            },
            {
                'name': 'software_version',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '软件版本'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '备注信息'
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
                'validation_rule': 'ip'
            },
            {
                'name': 'vendor',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '厂商',
                'validation_rule': 'firewall_vendor'
            },
            {
                'name': 'device_model',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '设备型号'
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '序列号'
            },
            {
                'name': 'firmware_version',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '固件版本'
            },
            {
                'name': 'ha_status',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': 'HA状态',
                'validation_rule': 'ha_status'
            },
            {
                'name': 'mgmt_user',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '管理用户'
            },
            {
                'name': 'mgmt_password',
                'type': 'password',
                'required': False,
                'editable': True,
                'verbose_name': '管理密码'
            },
            {
                'name': 'room',
                'type': 'model_ref',
                'required': True,
                'editable': True,
                'verbose_name': '机房',
                'ref_model': 'rooms'
            },
            {
                'name': 'cabinet',
                'type': 'model_ref',
                'required': True,
                'editable': True,
                'verbose_name': '机柜',
                'ref_model': 'cabinets'
            },
            {
                'name': 'cabinet_position',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': 'U位',
                'validation_rule': 'cabinet_position'
            },
            {
                'name': 'device_purpose',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '设备用途'
            },
            {
                'name': 'device_config',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '设备配置'
            },
            {
                'name': 'project_name',
                'type': 'model_ref',
                'required': False,
                'editable': True,
                'verbose_name': '项目名称',
                'ref_model': 'projects'
            },
            {
                'name': 'business',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '所属业务',
                'validation_rule': 'business'
            },
            {
                'name': 'online_time',
                'type': 'datetime',
                'required': False,
                'editable': True,
                'verbose_name': '上线时间'
            },
            {
                'name': 'warranty_expiration',
                'type': 'datetime',
                'required': False,
                'editable': True,
                'verbose_name': '质保到期时间'
            },
            {
                'name': 'device_status',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '设备状态',
                'validation_rule': 'device_status'
            },
            {
                'name': 'province_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '省份',
                'validation_rule': 'province'
            },
            {
                'name': 'city_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '城市',
                'validation_rule': 'city'
            },
            {
                'name': 'isp_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '运营商',
                'validation_rule': 'isp'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '备注信息'
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
                'validation_rule': 'ip'
            },
            {
                'name': 'vendor',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '厂商',
                'validation_rule': 'dwdm_vendor'
            },
            {
                'name': 'device_model',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '设备型号'
            },
            {
                'name': 'serial_number',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '序列号'
            },
            {
                'name': 'wavelength_number',
                'type': 'integer',
                'required': True,
                'editable': True,
                'verbose_name': '波长数量'
            },
            {
                'name': 'transmission_rate',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': '传输速率'
            },
            {
                'name': 'mgmt_user',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '管理用户'
            },
            {
                'name': 'mgmt_password',
                'type': 'password',
                'required': False,
                'editable': True,
                'verbose_name': '管理密码'
            },
            {
                'name': 'room',
                'type': 'model_ref',
                'required': True,
                'editable': True,
                'verbose_name': '机房',
                'ref_model': 'rooms'
            },
            {
                'name': 'cabinet',
                'type': 'model_ref',
                'required': True,
                'editable': True,
                'verbose_name': '机柜',
                'ref_model': 'cabinets'
            },
            {
                'name': 'cabinet_position',
                'type': 'string',
                'required': True,
                'editable': True,
                'verbose_name': 'U位',
                'validation_rule': 'cabinet_position'
            },
            {
                'name': 'device_purpose',
                'type': 'string',
                'required': False,
                'editable': True,
                'verbose_name': '设备用途'
            },
            {
                'name': 'device_config',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '设备配置'
            },
            {
                'name': 'project_name',
                'type': 'model_ref',
                'required': False,
                'editable': True,
                'verbose_name': '项目名称',
                'ref_model': 'projects'
            },
            {
                'name': 'online_time',
                'type': 'datetime',
                'required': False,
                'editable': True,
                'verbose_name': '上线时间'
            },
            {
                'name': 'warranty_expiration',
                'type': 'datetime',
                'required': False,
                'editable': True,
                'verbose_name': '质保到期时间'
            },
            {
                'name': 'device_status',
                'type': 'enum',
                'required': True,
                'editable': True,
                'verbose_name': '设备状态',
                'validation_rule': 'device_status'
            },
            {
                'name': 'province_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '省份',
                'validation_rule': 'province'
            },
            {
                'name': 'city_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '城市',
                'validation_rule': 'city'
            },
            {
                'name': 'isp_name',
                'type': 'enum',
                'required': False,
                'editable': True,
                'verbose_name': '运营商',
                'validation_rule': 'isp'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'required': False,
                'editable': True,
                'verbose_name': '备注信息'
            }
        ],
    },
    'clusters': {
        'verbose_name': '集群',
        'description': '集群资源管理',
        'model_group': 'application',
        'icon': 'clarity:data-cluster-line',
        'fields': [
            {
                'name': 'mgmt_url',
                'type': 'string',
                'verbose_name': '管理页面地址',
                'required': True,
                'editable': True,
                'validation_rule': 'url'
            },
            {
                'name': 'cluster_type',
                'type': 'enum',
                'verbose_name': '集群类型',
                'required': True,
                'editable': True,
                'validation_rule': 'cluster_type'
            },
            {
                'name': 'admin_user',
                'type': 'string',
                'verbose_name': '管理员用户',
                'required': True,
                'editable': True
            },
            {
                'name': 'admin_password',
                'type': 'password',
                'verbose_name': '管理员密码',
                'required': True,
                'editable': True
            },
            {
                'name': 'cluster_version',
                'type': 'string',
                'verbose_name': '集群版本',
                'required': False,
                'editable': True
            },
            {
                'name': 'cluster_vendor',
                'type': 'enum',
                'verbose_name': '集群厂商',
                'required': True,
                'editable': True,
                'validation_rule': 'cluster_vendor'
            },
            {
                'name': 'license_expiration',
                'type': 'datetime',
                'verbose_name': '授权到期时间',
                'required': False,
                'editable': True
            },
            {
                'name': 'running_status',
                'type': 'enum',
                'verbose_name': '运行状态',
                'required': True,
                'editable': True,
                'validation_rule': 'device_status'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
            }
        ]
    },
    'apps': {
        'verbose_name': '应用',
        'description': '',
        'model_group': 'application',
        'icon': 'ep:apple',
        'fields': [
            {
                'name': 'access_url',
                'type': 'string',
                'verbose_name': '访问地址',
                'required': True,
                'editable': True,
                'validation_rule': 'url'
            },
            {
                'name': 'admin_user',
                'type': 'string',
                'verbose_name': '管理员用户',
                'required': True,
                'editable': True
            },
            {
                'name': 'admin_password',
                'type': 'password',
                'verbose_name': '管理员密码',
                'required': True,
                'editable': True
            },
            {
                'name': 'app_version',
                'type': 'string',
                'verbose_name': '应用版本',
                'required': False,
                'editable': True
            },
            {
                'name': 'running_status',
                'type': 'enum',
                'verbose_name': '运行状态',
                'required': True,
                'editable': True,
                'validation_rule': 'device_status'
            },
            {
                'name': 'license_type',
                'type': 'enum',
                'verbose_name': '授权类型',
                'required': False,
                'editable': True,
                'validation_rule': 'license_type'
            },
            {
                'name': 'license_expiration',
                'type': 'datetime',
                'verbose_name': '授权到期时间',
                'required': False,
                'editable': True
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
            }
        ]
    },
    'middleware': {
        'verbose_name': '中间件',
        'description': '中间件资源管理',
        'model_group': 'application',
        'icon': 'clarity:layers-solid',
        'fields': [
            {
                'name': 'host',
                'type': 'string',
                'verbose_name': '主机',
                'required': True,
                'editable': True,
                'ref_model': 'hosts'
            },
            {
                'name': 'service_app',
                'type': 'model_ref',
                'verbose_name': '服务应用',
                'required': True,
                'editable': True,
                'ref_model': 'apps'
            },
            {
                'name': 'middleware_vendor',
                'type': 'string',
                'verbose_name': '中间件厂商',
                'required': True,
                'editable': True,
                'validation_rule': 'middleware_vendor'
            },
            {
                'name': 'version',
                'type': 'string',
                'verbose_name': '版本',
                'required': False,
                'editable': True
            },
            {
                'name': 'port',
                'type': 'integer',
                'verbose_name': '端口号',
                'required': True,
                'editable': True,
                'validation_rule': 'port_range'
            },
            {
                'name': 'running_status',
                'type': 'enum',
                'verbose_name': '运行状态',
                'required': True,
                'editable': True,
                'validation_rule': 'device_status'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
            }
        ]
    },
    'databases': {
        'verbose_name': '数据库',
        'description': '数据库资源管理',
        'model_group': 'application',
        'icon': 'clarity:storage-line',
        'fields': [
            {
                'name': 'ip',
                'type': 'string',
                'verbose_name': 'IP地址',
                'required': True,
                'editable': True,
                'validation_rule': 'ip'
            },
            {
                'name': 'port',
                'type': 'integer',
                'verbose_name': '端口号',
                'required': True,
                'editable': True,
                'validation_rule': 'port_range'
            },
            {
                'name': 'db_name',
                'type': 'string',
                'verbose_name': '数据库名称',
                'required': True,
                'editable': True
            },
            {
                'name': 'admin_user',
                'type': 'string',
                'verbose_name': '管理员用户',
                'required': True,
                'editable': True
            },
            {
                'name': 'admin_password',
                'type': 'password',
                'verbose_name': '管理员密码',
                'required': True,
                'editable': True
            },
            {
                'name': 'db_type',
                'type': 'enum',
                'verbose_name': '数据库类型',
                'required': True,
                'editable': True,
                'validation_rule': 'db_type'
            },
            {
                'name': 'db_vendor',
                'type': 'enum',
                'verbose_name': '数据库厂商',
                'required': True,
                'editable': True,
                'validation_rule': 'db_vendor'
            },
            {
                'name': 'business',
                'type': 'enum',
                'verbose_name': '所属业务',
                'required': True,
                'editable': True,
                'validation_rule': 'business'
            },
            {
                'name': 'version',
                'type': 'string',
                'verbose_name': '版本',
                'required': False,
                'editable': True
            },
            {
                'name': 'purpose',
                'type': 'string',
                'verbose_name': '用途',
                'required': False,
                'editable': True
            },
            {
                'name': 'license_expiration',
                'type': 'datetime',
                'verbose_name': '授权到期时间',
                'required': False,
                'editable': True
            },
            {
                'name': 'running_status',
                'type': 'enum',
                'verbose_name': '运行状态',
                'required': True,
                'editable': True,
                'validation_rule': 'device_status'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
            }
        ]
    },
    'transmission_links': {
        'verbose_name': '传输链路',
        'description': '传输链路管理',
        'model_group': 'others',
        'icon': 'clarity:lightning-solid',
        'fields': [
            {
                'name': 'link_id',
                'type': 'string',
                'verbose_name': '链路编号',
                'required': True,
                'editable': True
            },
            {
                'name': 'product_id',
                'type': 'string',
                'verbose_name': '产品编号',
                'required': True,
                'editable': True
            },
            {
                'name': 'transmission_type',
                'type': 'enum',
                'verbose_name': '传输类型',
                'required': True,
                'editable': True,
                'validation_rule': 'transmission_type'
            },
            {
                'name': 'bandwidth',
                'type': 'string',
                'verbose_name': '传输带宽',
                'required': True,
                'editable': True
            },
            {
                'name': 'start_address',
                'type': 'string',
                'verbose_name': '起点地址',
                'required': True,
                'editable': True
            },
            {
                'name': 'end_address',
                'type': 'string',
                'verbose_name': '终点地址',
                'required': True,
                'editable': True
            },
            {
                'name': 'distance',
                'type': 'float',
                'verbose_name': '传输距离',
                'required': False,
                'editable': True
            },
            {
                'name': 'isp_name',
                'type': 'enum',
                'verbose_name': '运营商',
                'required': False,
                'editable': True,
                'validation_rule': 'isp'
            },
            {
                'name': 'business',
                'type': 'enum',
                'verbose_name': '所属业务',
                'required': True,
                'editable': True,
                'validation_rule': 'business'
            },
            {
                'name': 'rental_fee',
                'type': 'float',
                'verbose_name': '租金',
                'required': False,
                'editable': True
            },
            {
                'name': 'client_name',
                'type': 'string',
                'verbose_name': '客户名称',
                'required': False,
                'editable': True
            },
            {
                'name': 'activation_time',
                'type': 'datetime',
                'verbose_name': '开通时间',
                'required': False,
                'editable': True
            },
            {
                'name': 'expiration_time',
                'type': 'datetime',
                'verbose_name': '到期时间',
                'required': False,
                'editable': True
            },
            {
                'name': 'transmission_status',
                'type': 'enum',
                'verbose_name': '传输状态',
                'required': True,
                'editable': True,
                'validation_rule': 'device_status'
            },
            {
                'name': 'responsible_person',
                'type': 'string',
                'verbose_name': '传输负责人',
                'required': False,
                'editable': True
            },
            {
                'name': 'repair_phone',
                'type': 'string',
                'verbose_name': '报修电话',
                'required': False,
                'editable': True,
                'validation_rule': 'phone'
            },
            {
                'name': 'remarks',
                'type': 'text',
                'verbose_name': '备注信息',
                'required': False,
                'editable': True
            }
        ]
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
        'description': '主机名格式校验'
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
    'project_status': {
        'verbose_name': '项目状态',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"planning\": \"规划中\", \"implementing\": \"实施中\", \"completed\": \"已完成\", \"closed\": \"已关闭\"}",
        'description': '项目状态'
    },
    'cabinet_position': {
        'verbose_name': 'U位',
        'field_type': 'string',
        'type': 'regex',
        'rule': '^[0-9]{1,2} ?[uU]?-[0-9]{1,2} ?[uU]?$',
        'editable': False,
        'description': 'U位校验',
    },
    'project_security_level': {
        'verbose_name': '密级',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"non-secret\": \"非密\", \"a1\": \"A1类\", \"a2\": \"A2类\", \"a3\": \"A3类\"}",
        'description': ''
    },
    'business': {
        'verbose_name': '业务',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"DW\": \"DW\", \"DC\": \"DC\", \"FG\": \"FG\", \"JD\": \"JD\", \"KHZL\": \"KHZL\", \"RD\": \"RD\", \"LBS\": \"LBS\", \"WX\": \"WX\", \"VPDN\": \"VPDN\", \"WTT\": \"WTT\", \"BD\": \"BD\"}",
        'description': ''
    },
    'organization': {
        'verbose_name': '组织',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"GA\": \"GA\", \"AQ\": \"AQ\", \"GAB\": \"GAB\", \"AQB\": \"AQB\", \"GJ\": \"管局\", \"mobile\": \"移动\", \"unicom\": \"联通\", \"telecom\": \"电信\", \"cbn\": \"广电\", \"XTY\": \"XTY\", \"HZ\": \"汇智\", \"other\": \"OTHER\"}",
        'description': ''
    },
    'vm_vendor': {
        'verbose_name': '虚拟化平台厂商',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"vmware\": \"VMware\", \"huawei\": \"华为\", \"aliyun\": \"阿里\", \"tencent\": \"腾讯\", \"inspur\": \"浪潮\", \"sugon\": \"曙光\", \"h3c\": \"新华三\"}",
        'description': '虚拟化平台厂商'
    },
    'switch_type': {
        'verbose_name': '交换机类型',
        'field_type': 'enum',
        'type': 'enum',
        "rule": "{\"gigabit\": \"千兆电口\", \"ten-gigabit\": \"万兆光口\"}",
        'description': '交换机类型'
    },
    'license_type': {
        'verbose_name': '授权类型',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"official\": \"正式\", \"trial\": \"试用\", \"research\": \"课题\", \"test\": \"测试\"}",
        'description': '授权类型'
    },
    'cluster_type': {
        'verbose_name': '集群类型',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"hive\": \"Hive\", \"hbase\": \"HBase\", \"flink\": \"Flink\", \"storm\": \"Storm\", \"clickhouse\": \"ClickHouse\", \"vdfs\": \"VDFS\", \"hdfs\": \"HDFS\", \"mpp\": \"MPP\", \"kafka\": \"Kafka\", \"redis\": \"Redis\", \"allInOne\": \"All-In-One\", \"other\": \"其他\"}",
        'description': '集群类型'
    },
    'cluster_vendor': {
        'verbose_name': '集群厂商',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"teligen\": \"汇智\", \"huawei\": \"华为\", \"inspur\": \"浪潮\", \"h3c\": \"新华三\"}",
        'description': '集群厂商'
    },
    'db_type': {
        'verbose_name': '数据库类型',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"RDBMS\": \"关系型数据库\", \"NoSQL\": \"非关系型数据库\", \"distributed\": \"分布式数据库\", \"in-memory\": \"内存数据库\"}",
        'description': '数据库类型'
    },
    'db_vendor': {
        'verbose_name': '数据库厂商',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"MySQL\": \"MySQL\", \"Oracle\": \"Oracle\", \"Redis\": \"Redis\", \"Mongo\": \"Mongo\", \"SyBase\": \"SyBase\", \"Postgresql\": \"Postgresql\", \"vastbase\": \"海量\", \"DM\": \"达梦\", \"HighGo\": \"翰高\", \"KingBase\": \"金仓\", \"StoreOne\": \"S1\"}",
        'description': '数据库厂商列表'
    },
    'transmission_type': {
        'verbose_name': '传输类型',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"bare_fiber\": \"裸纤\", \"dedicated_line\": \"专线\"}",
        'description': '传输类型'
    },
    'middleware_vendor': {
        'verbose_name': '中间件厂商',
        'field_type': 'enum',
        'type': 'enum',
        'rule': "{\"tomcat\": \"Tomcat\", \"weblogic\": \"WebLogic\", \"kingdee\": \"金蝶\", \"nginx\": \"Nginx\", \"httpd\": \"Httpd\", \"tongweb\": \"东方通\"}",
        'description': '中间件厂商列表'
    }
}
