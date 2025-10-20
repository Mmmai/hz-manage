from weakref import proxy
from django_filters import rest_framework as filters
from .models import *


class ModelGroupsFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    verbose_name = filters.CharFilter(field_name='verbose_name', lookup_expr='icontains')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    built_in = filters.BooleanFilter(field_name='built_in')
    editable = filters.BooleanFilter(field_name='editable')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ModelGroups
        fields = [
            'name',
            'verbose_name',
            'description',
            'built_in',
            'editable',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ModelsFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    verbose_name = filters.CharFilter(field_name='verbose_name', lookup_expr='icontains')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    model_group = filters.UUIDFilter(field_name='model_group')
    built_in = filters.BooleanFilter(field_name='built_in')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = Models
        fields = [
            'name',
            'verbose_name',
            'description',
            'model_group',
            'built_in',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ModelFieldGroupsFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    verbose_name = filters.CharFilter(field_name='verbose_name', lookup_expr='icontains')
    model = filters.UUIDFilter(field_name='model')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    built_in = filters.BooleanFilter(field_name='built_in')
    editable = filters.BooleanFilter(field_name='editable')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ModelFieldGroups
        fields = [
            'name',
            'verbose_name',
            'model',
            'description',
            'built_in',
            'editable',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ValidationRulesFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    verbose_name = filters.CharFilter(field_name='verbose_name', lookup_expr='icontains')
    field_type = filters.CharFilter(field_name='field_type', lookup_expr='icontains')
    type = filters.CharFilter(field_name='type', lookup_expr='icontains')
    built_in = filters.BooleanFilter(field_name='built_in')
    editable = filters.BooleanFilter(field_name='editable')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ValidationRules
        fields = [
            'name',
            'verbose_name',
            'field_type',
            'type',
            'built_in',
            'editable',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ModelFieldsFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    type = filters.CharFilter(field_name='type', lookup_expr='exact')
    unit = filters.CharFilter(field_name='unit', lookup_expr='icontains')
    model = filters.UUIDFilter(field_name='model')
    model_field_group = filters.UUIDFilter(field_name='model_field_group')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    order = filters.NumberFilter(field_name='order')
    required = filters.BooleanFilter(field_name='required')
    editable = filters.BooleanFilter(field_name='editable')
    built_in = filters.BooleanFilter(field_name='built_in')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ModelFields
        fields = [
            'name',
            'type',
            'unit',
            'model',
            'model_field_group',
            'description',
            'order',
            'required',
            'editable',
            'built_in',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ModelFieldPreferenceFilter(filters.FilterSet):
    model = filters.UUIDFilter(field_name='model')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ModelFieldPreference
        fields = [
            'model',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class UniqueConstraintFilter(filters.FilterSet):
    model = filters.UUIDFilter(field_name='model')
    fields = filters.UUIDFilter(field_name='fields')
    built_in = filters.BooleanFilter(field_name='built_in')
    validate_null = filters.BooleanFilter(field_name='validate_null')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = UniqueConstraint
        fields = [
            'model',
            'fields',
            'built_in',
            'validate_null',
            'create_time_after',
            'create_time_before',
        ]


class ModelInstanceFilter(filters.FilterSet):
    model = filters.UUIDFilter(field_name='model')
    instance_name = filters.CharFilter(field_name='instance_name', lookup_expr='icontains')
    model_instance_group = filters.UUIDFilter(method='filter_model_instance_group')
    input_type = filters.CharFilter(field_name='input_type', lookup_expr='icontains')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    def filter_model_instance_group(self, queryset, name, value):

        def get_all_child_groups(group):
            """递归获取所有子分组ID"""
            group_ids = [group.id]
            children = ModelInstanceGroup.objects.filter(parent=group)
            for child in children:
                group_ids.extend(get_all_child_groups(child))
            return group_ids

        if value:
            try:
                group = ModelInstanceGroup.objects.get(id=value)
                all_groups = get_all_child_groups(group)
                instance_ids = ModelInstanceGroupRelation.objects.filter(
                    group__in=all_groups
                ).values_list('instance_id', flat=True)
                return queryset.filter(id__in=instance_ids)
            except ModelInstanceGroup.DoesNotExist:
                return queryset.none()
        return queryset

    class Meta:
        model = ModelInstance
        fields = [
            'model',
            'instance_name',
            'model_instance_group',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ModelInstanceBasicFilter(filters.FilterSet):
    model = filters.UUIDFilter(field_name='model')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ModelInstance
        fields = [
            'model',
            'name',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ModelFieldMetaFilter(filters.FilterSet):
    model = filters.UUIDFilter(field_name='model')
    field = filters.UUIDFilter(field_name='field')
    key = filters.CharFilter(field_name='key', lookup_expr='exact')
    value = filters.CharFilter(field_name='value', lookup_expr='exact')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ModelFieldMeta
        fields = [
            'model',
            'field',
            'key',
            'value',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ModelInstanceGroupFilter(filters.FilterSet):
    label = filters.CharFilter(field_name='label', lookup_expr='icontains')
    model = filters.UUIDFilter(field_name='model')
    parent = filters.UUIDFilter(field_name='parent')
    level = filters.NumberFilter(field_name='level')
    order = filters.NumberFilter(field_name='order')
    path = filters.CharFilter(field_name='path', lookup_expr='icontains')
    built_in = filters.BooleanFilter(field_name='built_in')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ModelInstanceGroup
        fields = [
            'label',
            'model',
            'parent',
            'level',
            'order',
            'path',
            'built_in',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ModelInstanceGroupRelationFilter(filters.FilterSet):
    instance = filters.UUIDFilter(field_name='instance')
    group = filters.UUIDFilter(field_name='group')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ModelInstanceGroupRelation
        fields = [
            'instance',
            'group',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class RelationDefinitionFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    type = filters.CharFilter(field_name='type', lookup_expr='exact')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = RelationDefinition
        fields = [
            'name',
            'type',
            'description',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class RelationsFilter(filters.FilterSet):
    source_instance = filters.UUIDFilter(field_name='source_instance')
    target_instance = filters.UUIDFilter(field_name='target_instance')
    relation = filters.UUIDFilter(field_name='relation')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = Relations
        fields = [
            'source_instance',
            'target_instance',
            'relation',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ZabbixSyncHostFilter(filters.FilterSet):
    ip = filters.CharFilter(field_name='ip', lookup_expr='icontains')
    host_id = filters.CharFilter(field_name='hostid', lookup_expr='exact')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    agent_installed = filters.BooleanFilter(field_name='agent_installed')
    installation_error = filters.CharFilter(field_name='installation_error', lookup_expr='icontains')
    interface_available = filters.NumberFilter(field_name='interface_available')
    interface_available__in = filters.BaseCSVFilter(field_name='interface_available', lookup_expr='in')
    create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = ZabbixSyncHost
        fields = [
            'ip',
            'host_id',
            'name',
            'agent_installed',
            'interface_available',
            'interface_available__in',
            'create_time_after',
            'create_time_before',
            'update_time_after',
            'update_time_before',
        ]


class ZabbixProxyFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    ip = filters.CharFilter(field_name='ip', lookup_expr='icontains')
    port = filters.NumberFilter(field_name='port', lookup_expr='exact')
    proxy_id = filters.CharFilter(field_name='proxyid', lookup_expr='exact')

    class Meta:
        model = ZabbixProxy
        fields = [
            'name',
            'ip',
            'port',
            'proxy_id'
        ]


class ProxyAssignRuleFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    type = filters.CharFilter(field_name='type', lookup_expr='exact')
    rule = filters.CharFilter(field_name='rule', lookup_expr='icontains')
    proxy = filters.UUIDFilter(field_name='proxy')
    active = filters.BooleanFilter(field_name='active')

    class Meta:
        model = ProxyAssignRule
        fields = [
            'name',
            'type',
            'rule',
            'proxy',
            'active'
        ]
