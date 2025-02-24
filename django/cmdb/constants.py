from enum import Enum


class FieldType(str, Enum):
    STRING = 'string'
    TEXT = 'text'
    BOOLEAN = 'boolean'
    ENUM = 'enum'
    # CASCADE_ENUM = 'cascade_enum'
    JSON = 'json'
    INTEGER = 'integer'
    FLOAT = 'float'
    PASSWORD = 'password'
    DATE = 'date'
    DATETIME = 'datetime'
    MODEL_REF = 'model_ref'


class ValidationType(str, Enum):
    REGEX = 'regex'
    RANGE = 'range'
    LENGTH = 'length'
    ENUM = 'enum'
    # CASCADE_ENUM = 'cascade_enum'
    IP = 'ip'
    IPV4 = 'ipv4'
    IPV6 = 'ipv6'
    EMAIL = 'email'
    PHONE = 'phone'
    URL = 'url'
    DATE = 'date'
    DATETIME = 'datetime'
    TIMESTAMP = 'timestamp'
    JSON = 'json'
    BOOLEAN = 'boolean'
    PASSWORD = 'password'
    MODEL_REF = 'model_ref'


class DateTimeFormats:
    DATE_FORMATS = [
        '%Y%m%d',             # YYYYmmdd
        '%Y-%m-%d',           # YYYY-mm-dd
        '%Y/%m/%d',           # YYYY/mm/dd
        '%d%m%Y',             # ddmmyyyy
        '%d/%m/%Y',           # dd/mm/yyyy
        '%d-%m-%Y',           # dd-mm-yyyy
    ]

    DATETIME_FORMATS = [
        '%Y%m%d%H%M%S',       # YYYYmmddHHMMSS
        '%Y%m%d %H%M%S',      # YYYYmmdd HHMMSS
        '%Y-%m-%d %H:%M:%S',  # YYYY-mm-dd HH:MM:SS
        '%Y/%m/%d %H:%M:%S',  # YYYY/mm/dd HH:MM:SS
        '%d%m%Y%H%M%S',       # ddmmyyyyHHMMSS
        '%d/%m/%Y %H:%M:%S',  # dd/mm/yyyy HH:MM:SS
        '%d-%m-%Y %H:%M:%S',  # dd-mm-yyyy HH:MM:SS
        '%Y-%m-%dT%H:%M:%S',  # YYYY-mm-ddTHH:MM:SS
        '%Y/%m/%dT%H:%M:%S',  # YYYY/mm/ddTHH:MM:SS
    ]


limit_field_names = ['page', 'page_size', 'model', 'instance_name', 'model_instance_group', 'cache_key',]


class FieldMapping:
    # 字段类型对应的可用验证类型
    FIELD_TYPES = {
        FieldType.STRING: '字符串',
        FieldType.TEXT: '文本',
        FieldType.BOOLEAN: '布尔值',
        FieldType.ENUM: '枚举',
        # FieldType.CASCADE_ENUM: '级联枚举',
        FieldType.JSON: 'JSON',
        FieldType.INTEGER: '整数',
        FieldType.FLOAT: '浮点数',
        FieldType.PASSWORD: '密码',
        FieldType.MODEL_REF: '模型引用',
        FieldType.DATE: '日期',
        FieldType.DATETIME: '日期时间',
    }
    TYPE_EXCEL_FORMATS = {
        FieldType.STRING: '@',
        FieldType.TEXT: '@',
        FieldType.BOOLEAN: 'General',
        FieldType.ENUM: '@',
        # FieldType.CASCADE_ENUM: '@',
        FieldType.JSON: '@',
        FieldType.INTEGER: '0',
        FieldType.FLOAT: '0.00',
        FieldType.PASSWORD: '@',
        FieldType.MODEL_REF: '@',
        FieldType.DATE: 'yyyy-mm-dd',
        FieldType.DATETIME: 'yyyy-mm-dd hh:mm:ss',
    }
    TYPE_VALIDATIONS = {
        FieldType.STRING: [
            {
                'type': ValidationType.REGEX,
                'description': '正则表达式',
                'example': '^[A-Za-z0-9]+$'
            },
            {
                'type': ValidationType.LENGTH,
                'description': '长度限制',
                'example': '5,20'
            },
            {
                'type': ValidationType.URL,
                'description': 'URL格式',
                'example': 'https://example.com'
            },
            {
                'type': ValidationType.EMAIL,
                'description': '邮箱格式',
                'example': 'example@domain.com'
            },
            {
                'type': ValidationType.PHONE,
                'description': '电话号码',
                'example': '13800138000'
            },
            {
                'type': ValidationType.IP,
                'description': 'IP地址',
                'example': '192.168.1.1'
            },
            {
                'type': ValidationType.IPV4,
                'description': 'IPv4地址',
                'example': '192.168.1.1'
            },
            {
                'type': ValidationType.IPV6,
                'description': 'IPv6地址',
                'example': '2001:0db8:85a3:0000:0000:8a2e:0370:7334'
            },
        ],
        FieldType.TEXT: [
            {
                'type': ValidationType.LENGTH,
                'description': '长度限制',
                'example': '5,20'
            },
            {
                'type': ValidationType.REGEX,
                'description': '正则表达式',
                'example': '^[A-Za-z0-9]+$'
            }
        ],
        FieldType.BOOLEAN: [
            {
                'type': ValidationType.BOOLEAN,
                'description': '布尔值',
                'example': 'true/false, 0/1'
            }
        ],
        FieldType.INTEGER: [
            {
                'type': ValidationType.RANGE,
                'description': '数值范围',
                'example': '0,100'
            }
        ],
        FieldType.FLOAT: [
            {
                'type': ValidationType.RANGE,
                'description': '数值范围',
                'example': '0.0,1.0'
            }
        ],
        FieldType.DATE: [
            {
                'type': ValidationType.DATE,
                'description': '日期格式',
                'example': '2024-03-21'
            }
        ],
        FieldType.DATETIME: [
            {
                'type': ValidationType.DATETIME,
                'description': '日期时间格式',
                'example': '2024-03-21 15:30:00'
            }
        ],
        FieldType.JSON: [
            {
                'type': ValidationType.JSON,
                'description': 'JSON格式',
                'example': '{"key": "value"}'
            }
        ],
        FieldType.ENUM: [
            {
                'type': ValidationType.ENUM,
                'description': '枚举值',
                'example': ''
            }
        ],
        # FieldType.CASCADE_ENUM: [
        #     {
        #         'type': ValidationType.CASCADE_ENUM,
        #         'description': '级联枚举值',
        #         'example': ''
        #     }
        # ],
        FieldType.PASSWORD: [
            {
                'type': ValidationType.PASSWORD,
                'description': '密码规则',
            }
        ],
        FieldType.MODEL_REF: [
            {
                'type': ValidationType.MODEL_REF,
                'description': '模型关联',
            }
        ]
    }
