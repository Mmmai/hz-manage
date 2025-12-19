import json
from abc import ABC, abstractmethod
from .constants import FieldType
from .utils import password_handler

# import logging
# logger = logging.getLogger(__name__)


class FieldMetaConverter(ABC):
    """字段转换器基类"""
    @abstractmethod
    def to_internal(self, value, **kwargs):
        """转换为内部存储格式"""
        if value is None:
            return None
        return str(value)

    @abstractmethod
    def to_representation(self, value, **kwargs):
        """转换为外部表示格式"""
        return value


class PasswordConverter(FieldMetaConverter):
    """密码字段转换器"""

    def to_internal(self, value, **kwargs):
        if value is None or value == "":
            return ""
        plain = kwargs.get("plain", False)
        if plain:
            # logger.debug(f"Encrypting password to internal format (plain): {value}")
            _value = password_handler.encrypt_to_sm4(value)
            # logger.debug(f"SM4 encrypted password: {_value}")
            _encrypted_value = password_handler.encrypt(_value)
            # logger.debug(f"Fernet encrypted password: {_encrypted_value}")
            return _encrypted_value
        # logger.debug(f"Encrypting password to internal format (non-plain): {value}")
        _encrypted_value = password_handler.encrypt(value)
        # logger.debug(f"Fernet encrypted password: {_encrypted_value}")
        return _encrypted_value

    def to_representation(self, value, **kwargs):
        if value is None or value == "":
            return ""
        plain = kwargs.get("plain", False)
        masked = kwargs.get("masked", False)
        if plain:
            # logger.debug(f"Decrypting password to representation format (plain): {value}")
            _decrypted_value = password_handler.decrypt_to_plain(value)
            # logger.debug(f"Decrypted password (plain): {_decrypted_value}")
            return _decrypted_value if not masked else "******"
        # logger.debug(f"Decrypting password to representation format (non-plain): {value}")
        _decrypted_value = password_handler.decrypt(value)
        # logger.debug(f"Decrypted password (non-plain): {_decrypted_value}")
        return _decrypted_value if not masked else password_handler.encrypt_to_sm4("******")


class EnumConverter(FieldMetaConverter):
    """枚举字段转换器"""

    def to_internal(self, value, **kwargs):
        if value is None:
            return None
        enum_dict = kwargs.get("enum_dict", {})

        from_excel = kwargs.get("from_excel", False)
        if from_excel:
            if str(value) in enum_dict.keys():
                return str(value)
            else:
                # Excel 导入时，将label映射为value
                reversed_enum_dict = {v: k for k, v in enum_dict.items()}
                if str(value) in reversed_enum_dict.keys():
                    return reversed_enum_dict[str(value)]

            raise ValueError(f"Invalid enum label: {value}")

        # 非Excel导入时，直接验证value
        if value in enum_dict.keys():
            return value
        raise ValueError(f"Invalid enum value: {value}")

    def to_representation(self, value, **kwargs):
        enum_dict = kwargs.get("enum_dict", {})
        return {
            "value": value,
            "label": enum_dict.get(value, "")
        }


class ModelRefConverter(FieldMetaConverter):
    """模型引用字段转换器"""

    def to_internal(self, value, **kwargs):
        if value is None:
            return None

        instance_map = kwargs.get("instance_map", {})

        # Excel 导入时，将instance_name映射为实例ID
        from_excel = kwargs.get("from_excel", False)
        if from_excel:
            reversed_instance_map = {v: k for k, v in instance_map.items()}
            if str(value) in instance_map.keys():
                return str(value)
            if str(value) in reversed_instance_map.keys():
                return reversed_instance_map[str(value)]
            raise ValueError(f"Invalid reference instance name: {value}")

        # 非Excel导入时，直接验证实例ID
        if str(value) in instance_map.keys():
            return value
        raise ValueError(f"Invalid reference instance id: {value}")

    def to_representation(self, value, **kwargs):
        instance_map = kwargs.get("instance_map", {})
        return {
            "id": value,
            "instance_name": instance_map.get(str(value), "")
        }


class BooleanConverter(FieldMetaConverter):
    """布尔字段转换器"""

    def to_internal(self, value, **kwargs):
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            val_lower = value.lower()
            if val_lower in ['true', '1', 'yes']:
                return True
            elif val_lower in ['false', '0', 'no']:
                return False
        if isinstance(value, int):
            return bool(value)
        raise ValueError(f"Invalid boolean value: {value}")

    def to_representation(self, value, **kwargs):
        if value is None:
            return None
        return bool(value)


class IntegerConverter(FieldMetaConverter):
    """整数字段转换器"""

    def to_internal(self, value, **kwargs):
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid integer value: {value}")

    def to_representation(self, value, **kwargs):
        if value is None:
            return None
        return int(value)


class FloatConverter(FieldMetaConverter):
    """浮点字段转换器"""

    def to_internal(self, value, **kwargs):
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid float value: {value}")

    def to_representation(self, value, **kwargs):
        if value is None:
            return None
        return float(value)


class JsonConverter(FieldMetaConverter):
    """JSON字段转换器"""

    def to_internal(self, value, **kwargs):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                json.loads(value)
                return value
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON string: {value}")
        elif isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return value

    def to_representation(self, value, **kwargs):
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            raise ValueError(f"Invalid JSON value: {value}")


class StringConverter(FieldMetaConverter):
    """字符串字段转换器"""

    def to_internal(self, value, **kwargs):
        return super().to_internal(value, **kwargs)

    def to_representation(self, value, **kwargs):
        return super().to_representation(value, **kwargs)


class ConverterFactory:
    """转换器工厂类"""

    _converters_cache = {}

    @classmethod
    def get_converter(cls, field_type):
        """获取转换器实例"""
        if field_type not in cls._converters_cache:
            converter_class = cls._get_converter_class(field_type)
            cls._converters_cache[field_type] = converter_class()
        return cls._converters_cache[field_type]

    @staticmethod
    def _get_converter_class(field_type):
        converters = {
            FieldType.PASSWORD: PasswordConverter,
            FieldType.ENUM: EnumConverter,
            FieldType.MODEL_REF: ModelRefConverter,
            FieldType.BOOLEAN: BooleanConverter,
            FieldType.INTEGER: IntegerConverter,
            FieldType.FLOAT: FloatConverter,
            FieldType.JSON: JsonConverter,
            FieldType.STRING: StringConverter
        }
        return converters.get(field_type, StringConverter)
