# validators.py
import re
import json
from datetime import datetime
import ipaddress
from .constants import FieldType, ValidationType, DateTimeFormats
import logging
logger = logging.getLogger(__name__)


class FieldValidator:
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^1[3-9]\d{9}$'
    URL_PATTERN = r'^https?://\S+$'
    IPV4_PATTERN = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    IPV6_PATTERN = r'^(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'

    @staticmethod
    def validate_string_common(value, field_config):
        if not isinstance(value, str):
            raise ValueError("Value must be string type")

        if field_config.validation_rule.type == ValidationType.LENGTH:
            try:
                min_len, max_len = map(int, field_config.validation_rule.rule.split(','))
                if not min_len <= len(value) <= max_len:
                    raise ValueError(f"String length must be between {min_len} and {max_len}")
            except ValueError as e:
                raise ValueError(f"Invalid length validation rule: {field_config.validation_rule}")

        if field_config.validation_rule.type == ValidationType.REGEX:
            if not re.match(field_config.validation_rule.rule, value):
                raise ValueError(f"Value does not match pattern: {field_config.validation_rule.rule}")
        return value

    def validate_custom_regex(value, field_config):
        if not re.match(field_config.validation_rule.rule, value):
            raise ValueError(f"Value does not match pattern: {field_config.validation_rule.rule}")
        return value

    @staticmethod
    def validate_string(value, field_config):
        return FieldValidator.validate_string_common(value, field_config)

    @staticmethod
    def validate_text(value, field_config):
        return FieldValidator.validate_string_common(value, field_config)

    @staticmethod
    def validate_integer(value, field_config):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Value must be integer type")

        if not field_config.validation_rule:
            return value
        if field_config.validation_rule.type == ValidationType.RANGE:
            try:
                min_val, max_val = map(int, field_config.validation_rule.rule.split(','))
                if not min_val <= value <= max_val:
                    raise ValueError(f"Value must be between {min_val} and {max_val}")
            except ValueError:
                raise ValueError(f"Invalid range validation rule: {field_config.validation_rule}")
        return value

    @staticmethod
    def validate_float(value, field_config):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Value must be float type")

        if not field_config.validation_rule:
            return value
        if field_config.validation_rule.type == ValidationType.RANGE:
            map_status = False
            try:
                logger.info(f'Validating float value: {value}')
                min_val, max_val = map(float, field_config.validation_rule.rule.split(','))
                map_status = True
                logger.info(f'Range: {min_val} - {max_val}')
                if value < min_val or value > max_val:
                    raise ValueError(f"Value must be between {min_val} and {max_val}")
            except ValueError:
                if map_status:
                    raise ValueError(f"Value {value} must be between {min_val} and {max_val}")
                else:
                    raise ValueError(f"Invalid range validation rule: {field_config.validation_rule}")
        return value

    @staticmethod
    def validate_enum(value, field_config):
        """枚举值校验"""
        try:
            allowed_values = field_config.validation_rule.rule
            if isinstance(allowed_values, str):
                allowed_values = json.loads(allowed_values)

            if value not in allowed_values:
                raise ValueError(f"Value must be one of: {allowed_values}")
            return value

        except (json.JSONDecodeError, AttributeError):
            raise ValueError("Invalid validation rule format: {field_config.validation_rule.rule}")

    @staticmethod
    def validate_cascade_enum(value, field_config):
        """级联枚举值校验"""
        try:
            allowed_values = field_config.validation_rule.rule
            if isinstance(allowed_values, str):
                allowed_values = json.loads(allowed_values)

            if value not in allowed_values:
                raise ValueError(f"Value must be one of: {allowed_values}")
            return value

        except (json.JSONDecodeError, AttributeError):
            raise ValueError("Invalid validation rule format: {field_config.validation_rule.rule}")

    @staticmethod
    def validate_ip(value, field_config):
        """IP地址验证(支持v4和v6)"""
        logger.info(f'Validating IP address: {value}')
        if not re.match(FieldValidator.IPV4_PATTERN, value) and not re.match(FieldValidator.IPV6_PATTERN, value):
            raise ValueError("Invalid IP address format")

        return FieldValidator.validate_custom_regex(value, field_config)
        # return value

    @staticmethod
    def validate_ipv4(value, field_config):
        """IPv4地址验证"""
        if not re.match(FieldValidator.IPV4_PATTERN, value):
            raise ValueError("Invalid IPv4 address format")

        # FieldValidator.validate_custom_regex(value, field_config)
        return value

    @staticmethod
    def validate_ipv6(value, field_config):
        """IPv6地址验证"""
        if not re.match(FieldValidator.IPV6_PATTERN, value):
            raise ValueError("Invalid IPv6 address format")

        # FieldValidator.validate_custom_regex(value, field_config)
        return value

    @staticmethod
    def validate_email(value, field_config):
        if not re.match(FieldValidator.EMAIL_PATTERN, value):
            raise ValueError("Invalid email format")

        FieldValidator.validate_custom_regex(value, field_config)
        return value

    @staticmethod
    def validate_phone(value, field_config):
<<<<<<< HEAD
        print(FieldValidator.PHONE_PATTERN)
        print(value)
        if value == None:
            return value
=======

>>>>>>> hz-manager/cmdb
        if not re.match(FieldValidator.PHONE_PATTERN, value):
            raise ValueError("Invalid phone number format")

        FieldValidator.validate_custom_regex(value, field_config)
        return value

    @staticmethod
    def validate_url(value, field_config):
        if not re.match(FieldValidator.URL_PATTERN, value):
            raise ValueError("Invalid URL format")

        FieldValidator.validate_custom_regex(value, field_config)
        return value

    @staticmethod
    def validate_date(value, field_config):
        if not isinstance(value, str):
            raise ValueError("日期值必须是字符串类型")

        # 尝试解析为日期或日期时间格式
        for fmt in DateTimeFormats.DATE_FORMATS + DateTimeFormats.DATETIME_FORMATS:
            try:
                parsed_datetime = datetime.strptime(value, fmt)
                value = parsed_datetime.date()  # 提取日期部分
                return value
            except ValueError:
                continue
        raise ValueError(f"无效的日期格式，支持的格式有：{DateTimeFormats.DATE_FORMATS}")

    @staticmethod
    def validate_datetime(value, field_config):
        if not isinstance(value, str):
            raise ValueError("日期时间值必须是字符串类型")

        for fmt in DateTimeFormats.DATETIME_FORMATS:
            try:
                parsed_datetime = datetime.strptime(value, fmt)
                return parsed_datetime
            except ValueError:
                continue
        raise ValueError(f"无效的日期时间格式，支持的格式有：{DateTimeFormats.DATETIME_FORMATS}")

    @staticmethod
    def validate_timestamp(value, field_config):
        if not isinstance(value, (int, float)):
            raise ValueError("Timestamp value must be integer or float type")

        try:
            return datetime.fromtimestamp(value)
        except ValueError:
            raise ValueError("Invalid timestamp value")

    @staticmethod
    def validate_json(value, field_config=None):
        try:
            if isinstance(value, str):
                value_new = json.loads(value)
                if not isinstance(value_new, (dict, list)):
                    raise ValueError("Invalid JSON format: must be an object or array")
                return value_new
            elif isinstance(value, (dict, list)):
                return value
            raise ValueError
        except ValueError:
            raise ValueError("Invalid JSON format")

    @staticmethod
    def validate_boolean(value, field_config=None):
        if isinstance(value, bool):
            return value
        if value in ('true', '1', 1, 'True', 'TRUE', True):
            return True
        if value in ('false', '0', 0, 'False', 'FALSE', False):
            return False
        raise ValueError("Invalid boolean value")

    @classmethod
    def validate(cls, value, field_config):
        """验证入口"""
        logger.info(f'Accepting value: {value} for field: {field_config.name}')
        # 特殊类型字段跳过验证
        if field_config.type in [FieldType.PASSWORD, FieldType.MODEL_REF]:
            return value

        if not value and value != 0:
            if field_config.default:
                return field_config.default
            if field_config.required and not hasattr(field_config, 'create_field_flag'):
                # 排除对创建字段的default验证流程中的required验证
                raise ValueError(f"Field {field_config.name} is required")
            return value

        # 无验证规则
        if not field_config.type:
            raise ValueError(f"Field type is required for field: {field_config.name}")

        if not field_config.validation_rule and field_config.type in (FieldType.STRING, FieldType.TEXT):
            # 字符串和文本类型如果没有验证规则则直接返回
            logger.info(f'No validation rule for field: {field_config.name}')
            return value
        elif not field_config.validation_rule and field_config.type in FieldType:
            # 没有验证规则的其他类型字段使用基础校验规则对值进行校验
            logger.info(f'No validation rule for field: {field_config.name}')
            validator = getattr(cls, f'validate_{field_config.type}', None)
        elif field_config.type in (FieldType.INTEGER, FieldType.FLOAT, FieldType.BOOLEAN, FieldType.DATE, FieldType.DATETIME):
            # 整数和浮点数类型优先使用对应校验类型进行验证，此后如果有自定义验证规则再使用自定义规则二次验证
            logger.info(f'Using base validation for field: {field_config.name}')
            validator = getattr(cls, f'validate_{field_config.type}', None)
            logger.info(f'Validator method: {validator}')
        elif field_config.validation_rule and field_config.validation_rule.type == ValidationType.REGEX:
            # 使用自定义正则表达式校验
            logger.info(f'Using custom regex validation for field: {field_config.name}')
            validator = getattr(cls, 'validate_custom_regex', None)
        else:
            # 优先使用对应校验类型进行验证，此后如果有自定义验证规则再使用自定义规则二次验证
            logger.info(f'Using custom validation for field: {field_config.name}')
            validator = getattr(cls, f'validate_{field_config.validation_rule.type}', None)
            logger.info('Looking for validator method: %s', f'validate_{field_config.validation_rule.type}')
        logger.info(f'Validator method: {validator}')
        if validator:
            value = validator(value, field_config)
        return value
