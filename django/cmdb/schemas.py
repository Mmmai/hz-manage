from django.http import FileResponse
from drf_spectacular.utils import extend_schema_view, extend_schema, extend_schema_serializer
from drf_spectacular.utils import OpenApiParameter, OpenApiExample, OpenApiResponse, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from textwrap import dedent
from .constants import FieldType, ValidationType
from .serializers import (
    ModelGroupsSerializer,
    ModelsSerializer,
    ModelFieldGroupsSerializer,
    ValidationRulesSerializer,
    ModelFieldsSerializer,
    ModelFieldPreferenceSerializer,
    UniqueConstraintSerializer,
    ModelInstanceSerializer,
    ModelInstanceBasicViewSerializer,
    ModelFieldMetaSerializer,
    ModelInstanceGroupSerializer,
    ModelInstanceGroupRelationSerializer
)


model_groups_schema = extend_schema_view(
    # 标准CRUD方法
    create=extend_schema(
        request=ModelGroupsSerializer,
        responses={201: ModelGroupsSerializer},
        summary='创建模型分组',
        tags=['模型分组管理'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='模型分组名称',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=True,
                default=False,
                description='是否内置模型分组',
            ),
            OpenApiParameter(
                name='editable',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=True,
                default=True,
                description='是否可编辑',
            ),
            OpenApiParameter(
                name='verbose_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='显示名称',
            ),
            OpenApiParameter(
                name='description',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='模型分组描述',
            ),
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            ),
        ],
        examples=[
            OpenApiExample(
                name='创建主机分组示例',
                value={
                    'name': 'host',
                    'built_in': False,
                    'editable': True,
                    'verbose_name': '主机',
                    'description': '主机',
                    'create_user': 'admin',
                    'update_user': 'admin'
                },
            ),
        ]
    ),
    retrieve=extend_schema(
        responses={200: ModelGroupsSerializer},
        summary='获取模型分组详情',
        tags=['模型分组管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='模型分组ID',
            ),
        ],
    ),
    list=extend_schema(
        responses={200: ModelGroupsSerializer(many=True)},
        summary='获取模型分组列表',
        tags=['模型分组管理'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型分组名称模糊查询',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据是否内置模型分组查询',
            ),
            OpenApiParameter(
                name='editable',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据是否可编辑查询',
            ),
            OpenApiParameter(
                name='verbose_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据显示名称模糊查询',
            ),
            OpenApiParameter(
                name='description',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型分组描述模糊查询',
            ),
            OpenApiParameter(
                name='page',
                exclude=True,
            ),
            OpenApiParameter(
                name='page_size',
                exclude=True,
            ),
        ],
    ),
    update=extend_schema(
        summary='更新模型分组',
        tags=['模型分组管理'],
        request=ModelGroupsSerializer,
        responses={200: ModelGroupsSerializer},
    ),
    partial_update=extend_schema(
        summary='部分更新模型分组',
        tags=['模型分组管理'],
        request=ModelGroupsSerializer,
        responses={200: ModelGroupsSerializer},
    ),
    destroy=extend_schema(
        summary='删除模型分组',
        tags=['模型分组管理'],
        request=ModelGroupsSerializer,
        responses={204: None},
    )
)

models_schema = extend_schema_view(
    create=extend_schema(
        request=ModelsSerializer,
        responses={201: ModelsSerializer},
        summary='创建模型',
        description=(
            '创建模型时会自动为该模型创建关联内容:\n'
            '1. 默认字段分组: 基础配置\n'
            '2. 模型实例分组: \n'
            '   - 所有\n'
            '   - 所有/空闲池\n'
            '\n'
            '注意：不提供模型分组ID时会默认分配至【其他】分组'
        ),
        tags=['模型管理'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='模型名称',
            ),
            OpenApiParameter(
                name='model_group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='所属模型分组ID',
            ),
            OpenApiParameter(
                name='verbose_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='显示名称',
            ),
            OpenApiParameter(
                name='description',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='模型描述',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=True,
                default=False,
                description='是否内置模型',
            ),
            OpenApiParameter(
                name='editable',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=True,
                default=True,
                description='是否可编辑',
            ),
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            ),
        ],
        examples=[
            OpenApiExample(
                name='创建主机模型示例',
                value={
                    'name': 'server',
                    'model_group': 'uuid-of-host-group',
                    'verbose_name': '服务器',
                    'description': '服务器模型',
                    'built_in': False,
                    'editable': True,
                    'create_user': 'admin',
                    'update_user': 'admin'
                },
            ),
        ]
    ),
    retrieve=extend_schema(
        summary='获取模型详情',
        tags=['模型管理'],
        description=dedent('''
            # 返回说明

            除了基础模型信息外，还会返回以下统计数据：

            ## 实例统计
            * instance_count: 实例总数

            ## 字段配置
            * field_groups: 字段分组列表
                * id: 分组ID
                * name: 分组名称
                * verbose_name: 显示名称
                * fields: 字段列表
                    * id: 字段ID
                    * name: 字段名称
                    * type: 字段类型
                    * required: 是否必填
                    * order: 排序
        ''').strip(),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='模型ID',
            ),
        ],
        responses={
            200: extend_schema_serializer(
                many=False,
                examples=[
                    OpenApiExample(
                        name='项目模型示例',
                        value={
                            "model": {
                                "id": "cd61bb7e-26b6-4283-9839-9aa93179ad99",
                                "instance_count": 1,
                                "name": "projects",
                                "verbose_name": "项目",
                                "description": "项目管理",
                                "built_in": True,
                                "icon": "octicon:project-roadmap-24",
                                "create_user": "system",
                                "update_user": "system",
                                "model_group": "9830a7eb-f38e-46c8-91c2-6927937db8cc"
                            },
                            "field_groups": [
                                {
                                    "id": "704fb004-7673-458e-81b6-111e4a1110d4",
                                    "name": "basic",
                                    "verbose_name": "基础配置",
                                    "built_in": True,
                                    "fields": [
                                        {
                                            "id": "e97d521b-10fc-4a86-819a-3ba7f24f9a79",
                                            "name": "project_name",
                                            "verbose_name": "项目名称",
                                            "type": "string",
                                            "required": True,
                                            "order": 1
                                        }
                                    ]
                                }
                            ]
                        }
                    )
                ]
            )(inline_serializer(
                name='ModelDetailResponse',
                fields={
                    'model': ModelsSerializer(),
                    'field_groups': serializers.ListField(
                        child=inline_serializer(
                            name='FieldGroupDetail',
                            fields={
                                'id': serializers.UUIDField(),
                                'name': serializers.CharField(),
                                'verbose_name': serializers.CharField(),
                                'built_in': serializers.BooleanField(),
                                'fields': serializers.ListField(
                                    child=inline_serializer(
                                        name='FieldDetail',
                                        fields={
                                            'id': serializers.UUIDField(),
                                            'name': serializers.CharField(),
                                            'verbose_name': serializers.CharField(),
                                            'type': serializers.CharField(),
                                            'required': serializers.BooleanField(),
                                            'order': serializers.IntegerField(),
                                        }
                                    )
                                )
                            }
                        )
                    )
                }
            ))
        }
    ),
    list=extend_schema(
        responses={200: ModelsSerializer(many=True)},
        summary='获取模型列表',
        tags=['模型管理'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型名称模糊查询',
            ),
            OpenApiParameter(
                name='model_group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型分组ID查询',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据是否内置模型查询',
            ),
            OpenApiParameter(
                name='editable',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据是否可编辑查询',
            ),
            OpenApiParameter(
                name='page',
                exclude=True,
            ),
            OpenApiParameter(
                name='page_size',
                exclude=True,
            ),
        ],
    ),
    update=extend_schema(
        summary='更新模型',
        tags=['模型管理'],
        request=ModelsSerializer,
        responses={200: ModelsSerializer},
    ),
    partial_update=extend_schema(
        summary='部分更新模型',
        tags=['模型管理'],
        request=ModelsSerializer,
        responses={200: ModelsSerializer},
    ),
    destroy=extend_schema(
        summary='删除模型',
        tags=['模型管理'],
        responses={204: None},
    )
)

model_field_groups_schema = extend_schema_view(
    create=extend_schema(
        request=ModelFieldGroupsSerializer,
        responses={201: ModelFieldGroupsSerializer},
        summary='创建字段分组',
        tags=['字段分组管理'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='字段分组名称',
            ),
            OpenApiParameter(
                name='verbose_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='显示名称',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=True,
                default=False,
                description='是否内置字段分组',
            ),
            OpenApiParameter(
                name='order',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='排序',
            ),
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='所属模型ID',
            ),
        ]
    ),
    retrieve=extend_schema(
        responses={200: ModelFieldGroupsSerializer},
        summary='获取字段分组详情',
        tags=['字段分组管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='字段分组ID',
            ),
        ]
    ),
    list=extend_schema(
        responses={200: ModelFieldGroupsSerializer(many=True)},
        summary='获取字段分组列表',
        tags=['字段分组管理'],
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型ID查询',
            ),
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据字段分组名称模糊查询',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据是否内置字段分组查询',
            ),
            OpenApiParameter(
                name='page',
                exclude=True,
            ),
            OpenApiParameter(
                name='page_size',
                exclude=True,
            ),
        ]
    ),
    update=extend_schema(
        summary='更新字段分组',
        tags=['字段分组管理'],
        request=ModelGroupsSerializer,
        responses={200: ModelGroupsSerializer},
    ),
    partial_update=extend_schema(
        summary='部分更新字段分组',
        tags=['字段分组管理'],
        request=ModelGroupsSerializer,
        responses={200: ModelGroupsSerializer},
    ),
    destroy=extend_schema(
        summary='删除字段分组',
        tags=['字段分组管理'],
        description='删除字段分组时会将字段分组下的字段移动至默认分组',
        responses={204: None},
    )
)

validation_rules_schema = extend_schema_view(
    create=extend_schema(
        request=ValidationRulesSerializer,
        responses={201: ValidationRulesSerializer},
        summary='创建字段校验规则',
        tags=['字段校验规则管理'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='校验规则名称',
            ),
            OpenApiParameter(
                name='verbose_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='显示名称',
            ),
            OpenApiParameter(
                name='field_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='适配的字段类型',
                enum=[v.value for v in FieldType],
            ),
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='验证类型(regex/range/length等)',
                enum=[v.value for v in ValidationType],
            ),
            OpenApiParameter(
                name='rule',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='具体的验证规则',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                default=False,
                description='是否内置规则',
            ),
            OpenApiParameter(
                name='editable',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                default=True,
                description='是否可编辑',
            ),
            OpenApiParameter(
                name='description',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='规则描述',
            ),
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            ),
        ],
        examples=[
            OpenApiExample(
                name='正则校验规则示例',
                value={
                    'name': 'ip_address',
                    'verbose_name': 'IP地址',
                    'field_type': 'string',
                    'type': 'regex',
                    'rule': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                    'built_in': True,
                    'editable': False,
                    'description': 'IPv4地址格式校验',
                    'create_user': 'system',
                    'update_user': 'system'
                },
            ),
        ]
    ),
    retrieve=extend_schema(
        responses={200: ValidationRulesSerializer},
        summary='获取校验规则详情',
        tags=['字段校验规则管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='校验规则ID',
            ),
        ]
    ),
    list=extend_schema(
        responses={200: ValidationRulesSerializer(many=True)},
        summary='获取校验规则列表',
        tags=['字段校验规则管理'],
        parameters=[
            OpenApiParameter(
                name='field_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据字段类型查询',
            ),
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据规则名称模糊查询',
            ),
            OpenApiParameter(
                name='page',
                exclude=True,
            ),
            OpenApiParameter(
                name='page_size',
                exclude=True,
            ),
        ]
    ),
    update=extend_schema(
        request=ValidationRulesSerializer,
        responses={200: ValidationRulesSerializer},
        summary='更新校验规则',
        tags=['字段校验规则管理'],
    ),
    partial_update=extend_schema(
        request=ValidationRulesSerializer,
        responses={200: ValidationRulesSerializer},
        summary='部分更新校验规则',
        tags=['字段校验规则管理'],
    ),
    destroy=extend_schema(
        summary='删除校验规则',
        tags=['字段校验规则管理'],
        responses={204: None},
    )
)


model_fields_schema = extend_schema_view(
    create=extend_schema(
        request=ModelFieldsSerializer,
        responses={201: ModelFieldsSerializer},
        summary='创建字段',
        tags=['字段管理'],
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='字段名称',
            ),
            OpenApiParameter(
                name='verbose_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='显示名称',
            ),
            OpenApiParameter(
                name='field_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='字段类型',
                enum=[v.value for v in FieldType],
            ),
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='所属模型ID',
            ),
            OpenApiParameter(
                name='field_group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='所属字段分组ID',
            ),
            OpenApiParameter(
                name='validation_rule',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='校验规则ID',
            ),
            OpenApiParameter(
                name='required',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=True,
                default=False,
                description='是否必填',
            ),
            OpenApiParameter(
                name='editable',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=True,
                default=True,
                description='是否可编辑',
            ),
            OpenApiParameter(
                name='order',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='排序',
            ),
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            ),
        ],
        examples=[
            OpenApiExample(
                name='创建主机名称字段示例',
                value={
                    'name': 'hostname',
                    'verbose_name': '主机名',
                    'field_type': 'string',
                    'model': 'uuid-of-host-model',
                    'field_group': 'uuid-of-basic-group',
                    'validation_rule': 'uuid-of-hostname-rule',
                    'required': True,
                    'editable': True,
                    'create_user': 'admin',
                    'update_user': 'admin'
                },
            ),
        ]
    ),
    retrieve=extend_schema(
        responses={200: ModelFieldsSerializer},
        summary='获取字段详情',
        tags=['字段管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='字段ID',
            ),
        ]
    ),
    list=extend_schema(
        responses={200: ModelFieldsSerializer(many=True)},
        summary='获取字段列表',
        tags=['字段管理'],
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型ID查询',
            ),
            OpenApiParameter(
                name='field_group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据字段分组ID查询',
            ),
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据字段名称模糊查询',
            ),
            OpenApiParameter(
                name='field_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据字段类型查询',
                enum=[v.value for v in FieldType],
            ),
            OpenApiParameter(
                name='page',
                exclude=True,
            ),
            OpenApiParameter(
                name='page_size',
                exclude=True,
            ),
        ]
    ),
    update=extend_schema(
        request=ModelFieldsSerializer,
        responses={200: ModelFieldsSerializer},
        summary='更新字段',
        tags=['字段管理'],
    ),
    partial_update=extend_schema(
        request=ModelFieldsSerializer,
        responses={200: ModelFieldsSerializer},
        summary='部分更新字段',
        tags=['字段管理'],
    ),
    destroy=extend_schema(
        summary='删除字段',
        tags=['字段管理'],
        responses={204: None},
    ),
    metadata=extend_schema(
        summary='获取字段配置选项',
        tags=['字段管理'],
        description='获取字段类型和校验规则选项, OPTIONS接口平替',
        responses={
            200: {
                "name": "Model Fields Options",
                "description": "Options for type and validation rules of model fields",
                "renders": [
                    "application/json",
                    "text/html"
                ],
                "parses": [
                    "application/json",
                    "application/x-www-form-urlencoded",
                    "multipart/form-data"
                ],
                "field_types": {
                    "string": "字符串",
                    "text": "文本",
                    "boolean": "布尔值",
                    "enum": "枚举",
                    "json": "JSON",
                    "integer": "整数",
                    "float": "浮点数",
                    "password": "密码",
                    "model_ref": "模型引用",
                    "date": "日期",
                    "datetime": "日期时间"
                },
                "field_validations": {
                    "string": [
                        {
                            "type": "regex",
                            "description": "正则表达式",
                            "example": "^[A-Za-z0-9]+$"
                        },
                        {
                            "type": "length",
                            "description": "长度限制",
                            "example": "5,20"
                        },
                        {
                            "type": "url",
                            "description": "URL格式",
                            "example": "https://example.com"
                        },
                        {
                            "type": "email",
                            "description": "邮箱格式",
                            "example": "example@domain.com"
                        },
                        {
                            "type": "phone",
                            "description": "电话号码",
                            "example": "13800138000"
                        },
                        {
                            "type": "ip",
                            "description": "IP地址",
                            "example": "192.168.1.1"
                        },
                        {
                            "type": "ipv4",
                            "description": "IPv4地址",
                            "example": "192.168.1.1"
                        },
                        {
                            "type": "ipv6",
                            "description": "IPv6地址",
                            "example": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
                        }
                    ],
                    "text": [
                        {
                            "type": "length",
                            "description": "长度限制",
                            "example": "5,20"
                        },
                        {
                            "type": "regex",
                            "description": "正则表达式",
                            "example": "^[A-Za-z0-9]+$"
                        }
                    ],
                    "boolean": [
                        {
                            "type": "boolean",
                            "description": "布尔值",
                            "example": "true/false, 0/1"
                        }
                    ],
                    "integer": [
                        {
                            "type": "range",
                            "description": "数值范围",
                            "example": "0,100"
                        }
                    ],
                    "float": [
                        {
                            "type": "range",
                            "description": "数值范围",
                            "example": "0.0,1.0"
                        }
                    ],
                    "date": [
                        {
                            "type": "date",
                            "description": "日期格式",
                            "example": "2024-03-21"
                        }
                    ],
                    "datetime": [
                        {
                            "type": "datetime",
                            "description": "日期时间格式",
                            "example": "2024-03-21 15:30:00"
                        }
                    ],
                    "json": [
                        {
                            "type": "json",
                            "description": "JSON格式",
                            "example": "{\"key\": \"value\"}"
                        }
                    ],
                    "enum": [
                        {
                            "type": "enum",
                            "description": "枚举值",
                            "example": ""
                        }
                    ],
                    "password": [
                        {
                            "type": "password",
                            "description": "密码规则"
                        }
                    ],
                    "model_ref": [
                        {
                            "type": "model_ref",
                            "description": "模型关联"
                        }
                    ]
                },
                "limit_fields": [
                    "page",
                    "page_size",
                    "model",
                    "instance_name",
                    "model_instance_group",
                    "cache_key"
                ]
            },
        }
    )
)

model_field_preference_schema = extend_schema_view(
    create=extend_schema(
        request=ModelFieldPreferenceSerializer,
        responses={201: ModelFieldPreferenceSerializer},
        summary='创建字段展示配置',
        tags=['字段展示管理'],
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='模型ID',
            ),
            OpenApiParameter(
                name='fields_preferred',
                type={'type': 'array', 'items': {'type': 'string'}},
                location=OpenApiParameter.QUERY,
                required=True,
                description='字段ID',
            ),
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            )
        ],
        examples=[
            OpenApiExample(
                name='创建主机名称字段展示配置示例',
                value={
                    'model': 'uuid-of-host-model',
                    'fields_preferred': ['uuid-of-hostname-field'],
                    'create_user': 'admin',
                    'update_suer': 'admin'
                },
            ),
        ]
    ),
    retrieve=extend_schema(
        responses={200: ModelFieldPreferenceSerializer},
        summary='获取字段展示配置详情',
        tags=['字段展示管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='字段展示ID',
            ),
        ]
    ),
    list=extend_schema(
        responses={200: ModelFieldPreferenceSerializer(many=True)},
        summary='获取字段展示配置列表',
        tags=['字段展示管理'],
        parameters=[
            OpenApiParameter(
                name='field',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据字段ID查询',
            ),
            OpenApiParameter(
                name='user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据用户查询',
            ),
            OpenApiParameter(
                name='page',
                exclude=True,
            ),
            OpenApiParameter(
                name='page_size',
                exclude=True,
            ),
        ]
    ),
    update=extend_schema(
        request=ModelFieldPreferenceSerializer,
        responses={200: ModelFieldPreferenceSerializer},
        summary='更新字段展示配置',
        tags=['字段展示管理'],
    ),
    partial_update=extend_schema(
        request=ModelFieldPreferenceSerializer,
        responses={200: ModelFieldPreferenceSerializer},
        summary='部分更新字段展示配置',
        tags=['字段展示管理'],
    ),
    destroy=extend_schema(
        summary='删除字段展示配置',
        tags=['字段展示管理'],
        responses={204: None},
    )
)

unique_constraint_schema = extend_schema_view(
    create=extend_schema(
        request=UniqueConstraintSerializer,
        responses={201: UniqueConstraintSerializer},
        summary='创建唯一约束',
        tags=['实例唯一性约束管理'],
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='模型ID',
            ),
            OpenApiParameter(
                name='fields',
                type={'type': 'array', 'items': {'type': 'string'}},
                location=OpenApiParameter.QUERY,
                required=True,
                description='字段ID',
            ),
            OpenApiParameter(
                name='validate_null',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=True,
                default=False,
                description='是否验证空值, 设置为false时将忽略空值重复, 否则将对重复的空值进行校验',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=True,
                default=False,
                description='是否内置唯一约束',
            ),
            OpenApiParameter(
                name='description',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='唯一约束描述',
            ),
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            )
        ],
        examples=[
            OpenApiExample(
                name='创建主机名称唯一约束示例',
                value={
                    'model': 'uuid-of-host-model',
                    'fields': ['uuid-of-hostname-field'],
                    'validate_null': False,
                    'built_in': False,
                    'description': '主机名称唯一约束',
                    'create_user': 'admin',
                    'update_user': 'admin'
                },
            ),
        ]
    ),
    retrieve=extend_schema(
        responses={200: UniqueConstraintSerializer},
        summary='获取唯一约束详情',
        tags=['实例唯一性约束管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='唯一约束ID',
            ),
        ]
    ),
    list=extend_schema(
        responses={200: UniqueConstraintSerializer(many=True)},
        summary='获取唯一约束列表',
        tags=['实例唯一性约束管理'],
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型ID查询',
            ),
            OpenApiParameter(
                name='page',
                exclude=True,
            ),
            OpenApiParameter(
                name='page_size',
                exclude=True,
            ),
        ]
    ),
    update=extend_schema(
        request=UniqueConstraintSerializer,
        responses={200: UniqueConstraintSerializer},
        summary='更新唯一约束',
        tags=['实例唯一性约束管理'],
    ),
    partial_update=extend_schema(
        request=UniqueConstraintSerializer,
        responses={200: UniqueConstraintSerializer},
        summary='部分更新唯一约束',
        tags=['实例唯一性约束管理'],
    ),
    destroy=extend_schema(
        summary='删除唯一约束',
        tags=['实例唯一性约束管理'],
        responses={204: None},
    )
)

file_response = {
    200: OpenApiResponse(
        response={
            'type': 'string',
            'format': 'binary'
        }
    )
}


class ImportStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=['processing', 'completed', 'failed'],
        help_text='导入状态: processing-处理中, completed-完成, failed-失败'
    )
    total = serializers.IntegerField(
        help_text='总记录数'
    )
    progress = serializers.IntegerField(
        help_text='当前进度'
    )
    created = serializers.IntegerField(
        help_text='创建成功数量'
    )
    updated = serializers.IntegerField(
        help_text='更新成功数量'
    )
    skipped = serializers.IntegerField(
        help_text='跳过数量'
    )
    failed = serializers.IntegerField(
        help_text='失败数量'
    )
    errors = serializers.ListField(
        child=serializers.CharField(),
        help_text='错误信息列表'
    )
    error_file_key = serializers.CharField(
        allow_null=True,
        help_text='错误记录文件的标识'
    )


MODEL_INSTANCE_COMMON_PARAMETERS = [
    OpenApiParameter(
        name='model',
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.QUERY,
        required=True,
        description='模型ID',
    ),
    OpenApiParameter(
        name='instance_name',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=True,
        description='实例名称',
    ),
    OpenApiParameter(
        name='fields',
        type={
            'type': 'object',
            'additionalProperties': {'type': 'string'}
        },
        location=OpenApiParameter.QUERY,
        required=True,
        description='字段键值对',
        examples=[
            OpenApiExample(
                name='field_example',
                value={
                    "field_name1": "value1",
                    "field_name2": "value2"
                }
            )
        ],
    ),
    OpenApiParameter(
        name='instance_group',
        type={
            'type': 'array',
            'items': {'type': 'string'}
        },
        location=OpenApiParameter.QUERY,
        required=False,
        description='实例分组ID列表'
    ),
    OpenApiParameter(
        name='update_user',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=True,
        description='更新用户',
    )
]

model_instance_schema = extend_schema_view(
    create=extend_schema(
        request=ModelInstanceSerializer,
        responses={201: ModelInstanceSerializer},
        summary='创建模型实例',
        tags=['实例管理'],
        parameters=[
            *MODEL_INSTANCE_COMMON_PARAMETERS,
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
        ],
        examples=[
            OpenApiExample(
                name='创建主机实例示例',
                value={
                    "model": "b4981050-c484-4cde-a8f4-1cecab2411a9",
                    "instance_name": "123",
                    "create_user": "admin",
                    "update_user": "admin",
                    "instance_group": [
                        {
                            "group_id": "7f580aed-695a-424f-8b59-86544738ad74",
                            "group_path": "所有/空闲池"
                        }
                    ],
                    "fields": {
                        'field_name1': 'value1',
                        'field_name2': 'value2'
                    }
                }
            )
        ]
    ),
    retrieve=extend_schema(
        responses={200: ModelInstanceSerializer},
        summary='获取模型实例详情',
        tags=['实例管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='实例ID',
            ),
        ],
        examples=[
            OpenApiExample(
                name='示例返回数据',
                value={
                    "id": "43b1888b-7ca2-4f35-8aff-2aa72bfe4a3c",
                    "model": "b4981050-c484-4cde-a8f4-1cecab2411a9",
                    "instance_name": "123",
                    "create_time": "2025-01-17T19:28:01.256923",
                    "update_time": "2025-01-17T19:28:01.256947",
                    "create_user": "admin",
                    "update_user": "admin",
                    "instance_group": [
                        {
                            "group_id": "7f580aed-695a-424f-8b59-86544738ad74",
                            "group_path": "所有/空闲池"
                        }
                    ],
                    "fields": {
                        'field_name1': 'value1',
                        'field_name2': 'value2'
                    }
                },
            ),
        ]
    ),
    list=extend_schema(
        responses={200: ModelInstanceSerializer(many=True)},
        summary='获取模型实例列表',
        tags=['实例管理'],
        description=(
            '## 字段查询说明\n'
            '支持直接使用字段名作为查询参数，例如：\n'
            '`/api/v1/cmdb/model_instance/?field1=value1&field2=value2`\n'

            '### 查询语法\n'
            '- 精确查询：field1=value1\n'
            '- 模糊查询：field1=like:value1\n'
            '- 包含查询：field1=in:value1,value2\n'
            '- 正则匹配：field1=regex:pattern\n'
            '- 空值查询：field1=null\n'
            '- 取反查询：field1=not:value1\n'

            '### 示例\n'
            '- 精确匹配主机名：/api/v1/cmdb/model_instance/?hostname=web-01\n'
            '- 模糊查询IP：/api/v1/cmdb/model_instance/?ip=like:192.168\n'
            '- 查询多个状态：/api/v1/cmdb/model_instance/?status=in:active,pending\n'
            '- 排除某个值：/api/v1/cmdb/model_instance/?owner=not:system\n'
        ),
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型ID查询',
            ),
            OpenApiParameter(
                name='model_instance_group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据实例分组ID查询',
            ),
            OpenApiParameter(
                name='instance_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据实例名称模糊查询',
            ),
            OpenApiParameter(
                name='field_query',
                type=OpenApiTypes.OBJECT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据字段查询',
                examples=[
                    OpenApiExample(
                        name='字段查询示例',
                        value={
                            "hostname": "web-01",
                            "ip": "like:192.168",
                            "status": "in:active,pending",
                            "owner": "not:system"
                        }
                    )
                ]
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='页码',
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='每页数量',
            ),
        ],
        examples=[
            OpenApiExample(
                name='查询示例',
                value={
                    "count": 2,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": "7348e02a-1f30-4c19-a0dc-441ab6a1e00b",
                            "model": "cd61bb7e-26b6-4283-9839-9aa93179ad99",
                            "instance_name": "2",
                            "create_time": "2025-01-17T19:23:22.015984",
                            "update_time": "2025-01-17T19:23:22.016039",
                            "create_user": "admin",
                            "update_user": "admin",
                            "instance_group": [
                                {
                                    "group_id": "4a2b3d90-b672-4b77-8a4f-f59d20340ec9",
                                    "group_path": "所有/空闲池"
                                }
                            ],
                            "fields": {
                                "remarks": None,
                                "project_name": "2",
                                "manager": "2",
                                "status": {
                                    "value": "planning",
                                    "label": "规划中"
                                },
                                "project_code": "2"
                            }
                        },
                        {
                            "id": "eda5655d-8755-46e6-ba11-4f130004345e",
                            "model": "cd61bb7e-26b6-4283-9839-9aa93179ad99",
                            "instance_name": "1",
                            "create_time": "2025-01-17T19:22:01.020694",
                            "update_time": "2025-01-17T19:22:01.021029",
                            "create_user": "admin",
                            "update_user": "admin",
                            "instance_group": [
                                {
                                    "group_id": "4a2b3d90-b672-4b77-8a4f-f59d20340ec9",
                                    "group_path": "所有/空闲池"
                                }
                            ],
                            "fields": {
                                "remarks": None,
                                "manager": "1",
                                "status": {
                                    "value": "planning",
                                    "label": "规划中"
                                },
                                "project_name": "1",
                                "project_code": "1"
                            }
                        },
                    ]
                }
            )
        ]
    ),
    update=extend_schema(
        request=ModelInstanceSerializer,
        responses={200: ModelInstanceSerializer},
        summary='更新模型实例',
        tags=['实例管理'],
        parameters=MODEL_INSTANCE_COMMON_PARAMETERS,
    ),
    partial_update=extend_schema(
        request=ModelInstanceSerializer,
        responses={200: ModelInstanceSerializer},
        summary='部分更新模型实例',
        tags=['实例管理'],
        parameters=MODEL_INSTANCE_COMMON_PARAMETERS,
    ),
    destroy=extend_schema(
        summary='删除模型实例',
        tags=['实例管理'],
        responses={204: None},
    ),
    bulk_update_fields=extend_schema(
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='BulkUpdateFieldsResult',
                    fields={
                        'status': serializers.CharField(
                            help_text='更新结果'
                        ),
                        'updated_instances_count': serializers.IntegerField(
                            help_text='更新实例数量'
                        ),
                    },
                ),
                description='更新结果',
                examples=[
                    OpenApiExample(
                        name='更新结果示例',
                        value={
                            'status': 'success',
                            'updated_instances_count': 2
                        }
                    )
                ]
            )
        },
        summary='批量更新模型实例字段',
        tags=['实例管理'],
        parameters=[
            OpenApiParameter(
                name='instances',
                type={
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                location=OpenApiParameter.QUERY,
                required=True,
                description='实例ID列表',
            ),
            OpenApiParameter(
                name='fields',
                type={
                    'type': 'object',
                    'additionalProperties': {'type': 'string'}
                },
                location=OpenApiParameter.QUERY,
                required=True,
                description='字段键值对',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            )
        ]
    ),
    bulk_delete=extend_schema(
        responses={204: None},
        summary='批量删除模型实例',
        tags=['实例管理'],
        parameters=[
            OpenApiParameter(
                name='instances',
                type={
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                location=OpenApiParameter.QUERY,
                required=True,
                description='实例ID列表',
            ),
        ],
        examples=[
            OpenApiExample(
                name='批量删除示例',
                value={
                    'instances': ['7348e02a-1f30-4c19-a0dc-441ab6a1e00b']
                }
            )
        ]
    ),
    export_data=extend_schema(
        responses=file_response,
        summary='导出模型实例数据',
        tags=['实例管理'],
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='模型ID',
            ),
            OpenApiParameter(
                name='instances',
                type={
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                location=OpenApiParameter.QUERY,
                required=False,
                description='导出实例ID列表, 不填默认导出全部',
            ),
            OpenApiParameter(
                name='fields',
                type={
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                location=OpenApiParameter.QUERY,
                required=False,
                description='导出字段列表, 不填默认导出全部',
            ),
        ],
        examples=[
            OpenApiExample(
                name='导出某个模型下全部实例',
                value={
                    'model': 'b4981050-c484-4cde-a8f4-1cecab2411a9'
                }
            ),
            OpenApiExample(
                name='导出某个模型下指定实例的指定字段',
                value={
                    'model': 'b4981050-c484-4cde-a8f4-1cecab2411a9',
                    'instances': ['7348e02a-1f30-4c19-a0dc-441ab6a1e00b'],
                    'fields': ['field_name1', 'field_name2']
                }
            )
        ]
    ),
    export_template=extend_schema(
        responses=file_response,
        summary='导出模型实例模板',
        tags=['实例管理'],
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='模型ID',
            ),
        ],
        examples=[
            OpenApiExample(
                name='导出模板示例',
                value={
                    'model': 'b4981050-c484-4cde-a8f4-1cecab2411a9'
                }
            )
        ]
    ),
    import_data=extend_schema(
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='ImportResult',
                    fields={
                        'cache_key': serializers.CharField(
                            help_text='任务ID'
                        )
                    },
                ),
                description='导入任务ID',
                examples=[
                    OpenApiExample(
                        name='导入任务ID示例',
                        value={
                            'cache_key': 'import_task_cd61bb7e-26b6-4283-9839-9aa93179ad99'
                        }
                    )
                ]
            )
        },
        summary='导入模型实例数据',
        tags=['实例管理'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'model': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': '模型ID'
                    },
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': '导入的Excel文件(.xlsx)'
                    }
                },
                'required': ['model', 'file']
            }
        },
        parameters=[
            OpenApiParameter(
                name='model',
                exclude=True,
            ),
            OpenApiParameter(
                name='model_instance_group',
                exclude=True,
            ),
            OpenApiParameter(
                name='instance_name',
                exclude=True,
            ),
            OpenApiParameter(
                name='page',
                exclude=True,
            ),
            OpenApiParameter(
                name='page_size',
                exclude=True,
            ),
        ]
    ),
    import_status=extend_schema(
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='ImportStatus',
                    fields={
                        'status': serializers.ChoiceField(
                            choices=['pending', 'processing', 'completed', 'failed'],
                            help_text='处理状态'
                        ),
                        'total': serializers.IntegerField(help_text='总记录数'),
                        'progress': serializers.IntegerField(help_text='当前进度'),
                        'created': serializers.IntegerField(help_text='创建数量'),
                        'updated': serializers.IntegerField(help_text='更新数量'),
                        'skipped': serializers.IntegerField(help_text='跳过数量'),
                        'failed': serializers.IntegerField(help_text='失败数量'),
                        'errors': serializers.ListField(
                            child=serializers.CharField(),
                            help_text='错误信息'
                        ),
                        'error_file_key': serializers.CharField(
                            allow_null=True,
                            help_text='错误文件标识'
                        )
                    }
                ),
                description='导入任务状态',
                examples=[
                    OpenApiExample(
                        name='进行中',
                        value={
                            'status': 'processing',
                            'total': 100,
                            'progress': 50,
                            'created': 30,
                            'updated': 15,
                            'skipped': 5,
                            'failed': 0,
                            'errors': [],
                            'error_file_key': None
                        }
                    ),
                ]
            )
        },
        summary='获取导入状态',
        tags=['实例管理'],
        parameters=[
            OpenApiParameter(
                name='cache_key',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='任务ID',
            ),
        ]
    ),
    download_error_records=extend_schema(
        responses=file_response,
        summary='下载导入错误记录',
        tags=['实例管理'],
        parameters=[
            OpenApiParameter(
                name='cache_key',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='错误记录文件ID',
            ),
        ],
        examples=[
            OpenApiExample(
                name='下载错误记录示例',
                value={
                    'cache_key': 'import_error_cd61bb7e-26b6-4283-9839-9aa93179ad99'
                }
            )
        ]
    )
)

model_ref_schema = extend_schema_view(
    retrieve=extend_schema(
        responses={200: ModelInstanceBasicViewSerializer},
        summary='获取模型关联详情',
        tags=['模型引用管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='关联ID',
            ),
        ]
    ),
    list=extend_schema(
        responses={200: ModelInstanceBasicViewSerializer(many=True)},
        summary='获取模型关联列表',
        tags=['模型引用管理'],
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型ID查询',
            ),
            OpenApiParameter(
                name='instance_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据实例名称模糊查询',
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='页码',
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='每页数量',
            ),
        ],
        examples=[
            OpenApiExample(
                name='查询示例',
                value={
                    'model': 'b4981050-c484-4cde-a8f4-1cecab2411a9'
                }
            )
        ]
    )
)

MODEL_FIELD_META_COMMON_PARAMETERS = [
    OpenApiParameter(
        name='model',
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.QUERY,
        required=True,
        description='模型ID',
    ),
    OpenApiParameter(
        name='model_instance',
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.QUERY,
        required=True,
        description='实例ID',
    ),
    OpenApiParameter(
        name='model_fields',
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.QUERY,
        required=True,
        description='字段ID',
    ),
    OpenApiParameter(
        name='data',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=True,
        description='元数据值',
    ),
    OpenApiParameter(
        name='update_user',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=True,
        description='更新用户',
    )
]

model_field_meta_schema = extend_schema_view(
    create=extend_schema(
        request=ModelFieldMetaSerializer,
        responses={201: ModelFieldMetaSerializer},
        summary='创建字段元数据',
        tags=['字段元数据管理'],
        parameters=[
            *MODEL_FIELD_META_COMMON_PARAMETERS,
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
        ],
        examples=[
            OpenApiExample(
                name='创建主机名称字段元数据示例',
                value={
                    "model": "b4981050-c484-4cde-a8f4-1cecab2411a9",
                    "model_instance": "7348e02a-1f30-4c19-a0dc-441ab6a1e00b",
                    "model_fields": "b4981050-c484-4cde-a8f4-1cecab2411a9",
                    "data": "value1",
                    "create_user": "admin",
                    "update_user": "admin"
                },
            ),
        ]
    ),
    retrieve=extend_schema(
        responses={200: ModelFieldMetaSerializer},
        summary='获取字段元数据详情',
        tags=['字段元数据管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='字段元数据ID',
            ),
        ]
    ),
    list=extend_schema(
        responses={200: ModelFieldMetaSerializer(many=True)},
        summary='获取字段元数据列表',
        tags=['字段元数据管理'],
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型ID查询',
            ),
            OpenApiParameter(
                name='model_instance',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据实例ID查询',
            ),
            OpenApiParameter(
                name='model_fields',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据字段ID查询',
            ),
            OpenApiParameter(
                name='data',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据元数据值查询',
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='页码',
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='每页数量',
            ),
        ]
    ),
    update=extend_schema(
        request=ModelFieldMetaSerializer,
        responses={200: ModelFieldMetaSerializer},
        summary='更新字段元数据',
        tags=['字段元数据管理'],
    ),
    partial_update=extend_schema(
        request=ModelFieldMetaSerializer,
        responses={200: ModelFieldMetaSerializer},
        summary='部分更新字段元数据',
        tags=['字段元数据管理'],
    ),
    destroy=extend_schema(
        summary='删除字段元数据',
        tags=['字段元数据管理'],
        responses={204: None},
    )
)

group_tree_node = inline_serializer(
    name='节点分组树',
    fields={
        'id': serializers.CharField(help_text='分组ID'),
        'label': serializers.CharField(help_text='分组名称'),
        'level': serializers.IntegerField(help_text='分组层级'),
        'built_in': serializers.BooleanField(help_text='是否内置'),
        'instance_count': serializers.IntegerField(help_text='实例数量'),
        'children': serializers.ListField(
            child=serializers.DictField(),
            help_text='子分组列表'
        )
    }
)

model_groups = inline_serializer(
    name='模型分组信息',
    fields={
        'model_name': serializers.CharField(help_text='模型标识'),
        'model_verbose_name': serializers.CharField(help_text='模型显示名称'),
        'groups': serializers.ListField(
            child=group_tree_node,
            help_text='分组树'
        )
    }
)


class ModelInstanceGroupsListResponseSerializer(serializers.Serializer):
    __root__ = serializers.DictField(
        child=model_groups,
        help_text="按模型ID分组的实例分组树，每个键为模型ID，对应的值为该模型的分组信息"
    )


model_instance_group_schema = extend_schema_view(
    create=extend_schema(
        request=ModelInstanceGroupSerializer,
        responses={201: ModelInstanceGroupSerializer},
        summary='创建实例分组',
        tags=['实例分组管理'],
        parameters=[
            OpenApiParameter(
                name='label',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='分组名称',
            ),
            OpenApiParameter(
                name='parent',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='父分组ID',
            ),
            OpenApiParameter(
                name='level',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='分组层级, 未提供时将自动计算',
            ),
            OpenApiParameter(
                name='path',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='分组完整路径, 未提供时将自动计算',
            ),
            OpenApiParameter(
                name='order',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='排序值, 未提供时分组默认创建在最后',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='是否内置分组',
                default=False
            ),
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            )
        ],
        examples=[
            OpenApiExample(
                name='创建实例分组示例',
                value={
                    'label': '故障机',
                    'parent': '7f580aed-695a-424f-8b59-86544738ad74',
                    'level': 2,
                    'path': '所有/故障机',
                    'order': 1,
                    'create_user': 'admin',
                    'update_user': 'admin'
                },
            ),
        ]
    ),
    list=extend_schema(
        responses={
            200: OpenApiResponse(
                response=ModelInstanceGroupsListResponseSerializer,
                description='按模型ID分组的实例分组树',
                examples=[
                    OpenApiExample(
                        name='分组树示例',
                        value={
                            "03cc7110-1ddd-4636-a5ff-bbbc9d53096b": {
                                "model_name": "hosts",
                                "model_verbose_name": "主机",
                                "groups": [
                                    {
                                        "id": "c4622037-2d1f-4510-835f-a35f421436c9",
                                        "label": "所有",
                                        "instance_count": 0,
                                        "built_in": True,
                                        "level": 1,
                                        "children": [
                                            {
                                                "id": "a00948e8-851f-4786-b4f5-61916c139a8c",
                                                "label": "空闲池",
                                                "instance_count": 0,
                                                "built_in": True,
                                                "level": 2,
                                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            },
                            "cd61bb7e-26b6-4283-9839-9aa93179ad99": {
                                "model_name": "projects",
                                "model_verbose_name": "项目",
                                "groups": [
                                    {
                                        "id": "b5e66b61-d29b-4088-a041-eda5270a9e92",
                                        "label": "所有",
                                        "instance_count": 3,
                                        "built_in": True,
                                        "level": 1,
                                        "children": [
                                            {
                                                "id": "4a2b3d90-b672-4b77-8a4f-f59d20340ec9",
                                                "label": "空闲池",
                                                "instance_count": 3,
                                                "built_in": True,
                                                "level": 2,
                                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    ),
                    OpenApiExample(
                        name='指定模型的分组树',
                        value={
                            "id": "c4622037-2d1f-4510-835f-a35f421436c9",
                            "label": "所有",
                            "instance_count": 0,
                            "built_in": True,
                            "level": 1,
                            "children": [
                                {
                                    "id": "a00948e8-851f-4786-b4f5-61916c139a8c",
                                    "label": "空闲池",
                                    "instance_count": 0,
                                    "built_in": True,
                                    "level": 2,
                                    "children": []
                                }
                            ]
                        }
                    )
                ]
            )
        },
        summary='获取实例分组树',
        tags=['实例分组管理'],
        description='<font color="red">**Responses示例**</font>中最外层的列表标识[]应该去除, 暂时没有找到处理的方案',
        parameters=[
            OpenApiParameter(
                name='model',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据模型ID过滤分组'
            ),
            OpenApiParameter(name='built_in', exclude=True),
            OpenApiParameter(name='label', exclude=True),
            OpenApiParameter(name='level', exclude=True),
            OpenApiParameter(name='page', exclude=True),
            OpenApiParameter(name='page_size', exclude=True),
            OpenApiParameter(name='level', exclude=True),
            OpenApiParameter(name='parent', exclude=True),
            OpenApiParameter(name='path', exclude=True),
            OpenApiParameter(name='order', exclude=True),
        ]
    ),
    retrieve=extend_schema(
        responses={
            200: OpenApiResponse(
                response=group_tree_node,
                description='实例分组详情',
                examples=[
                    OpenApiExample(
                        name='分组详情示例',
                        value={
                            "id": "b5e66b61-d29b-4088-a041-eda5270a9e92",
                            "label": "所有",
                            "instance_count": 3,
                            "built_in": True,
                            "level": 1,
                            "children": [
                                {
                                    "id": "4a2b3d90-b672-4b77-8a4f-f59d20340ec9",
                                    "label": "空闲池",
                                    "instance_count": 3,
                                    "built_in": True,
                                    "level": 2,
                                    "children": []
                                }
                            ]
                        }
                    )
                ]
            )
        },
        summary='获取实例分组详情',
        tags=['实例分组管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='分组ID',
            ),
        ]
    ),
    update=extend_schema(
        request=ModelInstanceGroupSerializer,
        responses={200: ModelInstanceGroupSerializer},
        summary='更新实例分组',
        tags=['实例分组管理'],
        parameters=[
            OpenApiParameter(
                name='label',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='分组名称',
            ),
            OpenApiParameter(
                name='parent',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='父分组ID',
            ),
            OpenApiParameter(
                name='level',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='分组层级',
            ),
            OpenApiParameter(
                name='path',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='分组完整路径',
            ),
            OpenApiParameter(
                name='order',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='排序值',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='是否内置分组',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            )
        ]
    ),
    partial_update=extend_schema(
        request=ModelInstanceGroupSerializer,
        responses={200: ModelInstanceGroupSerializer},
        summary='部分更新实例分组',
        tags=['实例分组管理'],
        parameters=[
            OpenApiParameter(
                name='label',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='分组名称',
            ),
            OpenApiParameter(
                name='parent',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='父分组ID',
            ),
            OpenApiParameter(
                name='level',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='分组层级',
            ),
            OpenApiParameter(
                name='path',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='分组完整路径',
            ),
            OpenApiParameter(
                name='order',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='排序值',
            ),
            OpenApiParameter(
                name='built_in',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='是否内置分组',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            )
        ]
    ),
    destroy=extend_schema(
        summary='删除实例分组',
        tags=['实例分组管理'],
        responses={204: None},
    ),
    add_instances=extend_schema(
        responses={200: OpenApiResponse(description='添加实例到分组')},
        summary='添加实例到分组',
        tags=['实例分组管理'],
        description='## <font color="red">**弃用**</font>',
        parameters=[
            OpenApiParameter(
                name='group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='分组ID',
            ),
            OpenApiParameter(
                name='instances',
                type={
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                location=OpenApiParameter.QUERY,
                required=True,
                description='实例ID列表',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            )
        ]
    ),
    remove_instances=extend_schema(
        responses={200: OpenApiResponse(description='从分组移除实例')},
        summary='从分组移除实例',
        tags=['实例分组管理'],
        description='## <font color="red">**弃用**</font>',
        parameters=[
            OpenApiParameter(
                name='group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='分组ID',
            ),
            OpenApiParameter(
                name='instances',
                type={
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                location=OpenApiParameter.QUERY,
                required=True,
                description='实例ID列表',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            )
        ]
    ),
    search_instances=extend_schema(
        responses={200: ModelInstanceBasicViewSerializer(many=True)},
        summary='搜索分组下的实例',
        tags=['实例分组管理'],
        description='## <font color="red">**弃用**</font>',
        parameters=[
            OpenApiParameter(
                name='group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='分组ID',
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='页码',
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='每页数量',
            ),
        ]
    ),
)


model_instance_group_relation_schema = extend_schema_view(
    create=extend_schema(
        responses={200: ModelInstanceGroupRelationSerializer},
        summary='创建实例与分组的关联',
        tags=['实例分组关联管理'],
        parameters=[
            OpenApiParameter(
                name='instance',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='实例ID',
            ),
            OpenApiParameter(
                name='group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='分组ID',
            ),
            OpenApiParameter(
                name='create_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='创建用户',
            ),
            OpenApiParameter(
                name='update_user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='更新用户',
            )
        ]
    ),
    retrieve=extend_schema(
        responses={200: ModelInstanceGroupRelationSerializer},
        summary='获取实例与分组的关联',
        tags=['实例分组关联管理'],
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                required=True,
                description='关联ID',
            ),
        ]
    ),
    list=extend_schema(
        responses={200: ModelInstanceGroupRelationSerializer(many=True)},
        summary='获取实例与分组的关联列表',
        tags=['实例分组关联管理'],
        parameters=[
            OpenApiParameter(
                name='instance',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据实例ID查询',
            ),
            OpenApiParameter(
                name='group',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=False,
                description='根据分组ID查询',
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='页码',
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='每页数量',
            ),
        ]
    ),
    create_relations=extend_schema(
        responses={200: ModelInstanceGroupRelationSerializer(many=True)},
        summary='批量创建实例与分组的关联',
        tags=['实例分组关联管理'],
        parameters=[
            OpenApiParameter(
                name='instances',
                type={
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                location=OpenApiParameter.QUERY,
                required=True,
                description='实例ID列表',
            ),
            OpenApiParameter(
                name='groups',
                type={
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                location=OpenApiParameter.QUERY,
                required=True,
                description='分组ID列表',
            ),
            OpenApiParameter('group', exclude=True),
            OpenApiParameter('instance', exclude=True),
            OpenApiParameter('page', exclude=True),
            OpenApiParameter('page_size', exclude=True),
        ]
    ),
)


class PasswordManageResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()


password_response = {
    200: OpenApiResponse(
        response=PasswordManageResponseSerializer,
        description='返回操作结果'
    )
}

password_manage_schema = extend_schema_view(
    re_encrypt=extend_schema(
        responses=password_response,
        summary='重新加密密码',
        tags=['密码及密钥管理'],
        description='当密钥更新时, 调用此接口对密码字段重新加密, 并重载新密钥'
    ),
    reset_passwords=extend_schema(
        responses=password_response,
        summary='重置密码',
        tags=['密码及密钥管理'],
        description='# <font color="red">将所有密码字段全部置空, 仅用于调试, 请勿执行</font>'
    )
)
