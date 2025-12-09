import uuid as uuid_module


class UUIDFormatter:
    """
    UUID 格式化工具类
    统一处理 UUID 的格式转换，兼容 Django ORM 行为
    """

    @staticmethod
    def normalize(value) -> str:
        """
        标准化 UUID 为不带连字符的格式（用于数据库查询）
        与 Django ORM 对 MySQL 的处理方式一致

        Args:
            value: UUID 对象、字符串或 None

        Returns:
            不带连字符的 32 位小写字符串，或空字符串
        """
        if value is None:
            return ''
        if isinstance(value, uuid_module.UUID):
            return value.hex.lower()
        if isinstance(value, str):
            return value.replace('-', '').lower()
        if isinstance(value, bytes):
            # 处理 MySQL 返回的 binary 类型
            return value.hex().lower()
        return str(value).replace('-', '').lower()

    @staticmethod
    def to_standard(value) -> str:
        """
        转换为标准 UUID 格式（带连字符，用于 API 响应）
        格式：8-4-4-4-12

        Args:
            value: UUID 对象、字符串、bytes 或 None

        Returns:
            标准格式的 UUID 字符串
        """
        if value is None:
            return ''

        # 处理 UUID 对象
        if isinstance(value, uuid_module.UUID):
            return str(value)

        # 处理 bytes（MySQL binary 类型）
        if isinstance(value, bytes):
            clean = value.hex().lower()
        elif isinstance(value, str):
            clean = value.replace('-', '').lower()
        else:
            clean = str(value).replace('-', '').lower()

        # 格式化为 8-4-4-4-12
        if len(clean) == 32:
            return f'{clean[:8]}-{clean[8:12]}-{clean[12:16]}-{clean[16:20]}-{clean[20:]}'

        return str(value)

    @staticmethod
    def to_uuid(value) -> uuid_module.UUID:
        """
        转换为 UUID 对象

        Args:
            value: UUID 对象、字符串、bytes 或 None

        Returns:
            UUID 对象，或 None
        """
        if value is None:
            return None
        if isinstance(value, uuid_module.UUID):
            return value
        if isinstance(value, bytes):
            return uuid_module.UUID(bytes=value)
        if isinstance(value, str):
            clean = value.replace('-', '')
            if len(clean) == 32:
                return uuid_module.UUID(clean)
        return None

    @classmethod
    def convert_row(cls, row: dict, uuid_fields: list = None) -> dict:
        """
        转换查询结果行中的 UUID 字段为标准格式

        Args:
            row: 查询结果字典
            uuid_fields: UUID 字段名列表，默认检测常见字段

        Returns:
            转换后的字典
        """
        if uuid_fields is None:
            # 默认处理常见的 UUID 字段
            uuid_fields = ['id', 'model_id', 'model_instance_id', 'model_fields_id',
                           'instance_id', 'group_id', 'parent_id', 'ref_model_id']

        result = dict(row)
        for field in uuid_fields:
            if field in result and result[field] is not None:
                result[field] = cls.to_standard(result[field])

        return result

    @classmethod
    def convert_rows(cls, rows: list, uuid_fields: list = None) -> list:
        """
        批量转换查询结果中的 UUID 字段

        Args:
            rows: 查询结果列表
            uuid_fields: UUID 字段名列表

        Returns:
            转换后的列表
        """
        return [cls.convert_row(row, uuid_fields) for row in rows]


# 便捷别名
uuid_normalize = UUIDFormatter.normalize
uuid_standard = UUIDFormatter.to_standard
