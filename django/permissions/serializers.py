from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .models import DataScope, PermissionTarget
from mapi.models import UserInfo, Role, UserGroup


class PermissionTargetInputSerializer(serializers.Serializer):
    """
    用于接收权限目标输入的内部序列化器。
    """
    app_label = serializers.CharField(write_only=True)
    model = serializers.CharField(write_only=True)
    object_ids = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
        write_only=True
    )

    def validate(self, attrs):
        try:
            ContentType.objects.get(app_label=attrs['app_label'], model=attrs['model'])
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(
                f"Invalid target model: {attrs['app_label']}.{attrs['model']}"
            )
        return attrs


class DataScopeSerializer(serializers.ModelSerializer):

    targets = PermissionTargetInputSerializer(many=True, write_only=True, required=False)
    role_name = serializers.CharField(source='role.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_group_name = serializers.CharField(source='user_group.name', read_only=True)

    class Meta:
        model = DataScope
        fields = [
            'id', 'role', 'user', 'user_group', 'app_label', 'scope_type',
            'role_name', 'user_name', 'user_group_name',
            'description', 'targets', 'create_time', 'update_time'
        ]
        read_only_fields = ['id', 'create_time', 'update_time', 'role_name', 'user_name', 'user_group_name']

    def _create_or_update_targets(self, scope, targets_data):
        ct_ids = ContentType.objects.filter(app_label=scope.app_label)
        scope.targets.filter(content_type__in=ct_ids).delete()

        targets_to_create = []
        for target_data in targets_data:
            content_type = ContentType.objects.get(
                app_label=target_data['app_label'],
                model=target_data['model']
            )
            for obj_id in target_data['object_ids']:
                targets_to_create.append(
                    PermissionTarget(
                        scope=scope,
                        content_type=content_type,
                        object_id=obj_id
                    )
                )

        if targets_to_create:
            PermissionTarget.objects.bulk_create(targets_to_create)

    @transaction.atomic
    def create(self, validated_data):
        targets_data = validated_data.pop('targets', [])
        lookup_fields = {}

        if validated_data.get('role'):
            lookup_fields['role'] = validated_data['role']
        elif validated_data.get('user'):
            lookup_fields['user'] = validated_data['user']
        elif validated_data.get('user_group'):
            lookup_fields['user_group'] = validated_data['user_group']

        lookup_fields['app_label'] = validated_data['app_label']

        scope, created = DataScope.objects.update_or_create(defaults=validated_data, **lookup_fields)
        if scope.scope_type == DataScope.ScopeType.FILTER:
            self._create_or_update_targets(scope, targets_data)
        else:
            lookup_fields['app_label'] = None
            DataScope.objects.filter(**lookup_fields).delete()
            ct_ids = ContentType.objects.filter(app_label=scope.app_label)
            scope.targets.filter(content_type__in=ct_ids).delete()
        return scope

    @transaction.atomic
    def update(self, instance, validated_data):
        if instance.role and instance.role.role == 'sysadmin':
            raise serializers.ValidationError("Cannot modify data scope for sysadmin role.")

        scope_type = validated_data.get('scope_type', instance.scope_type)
        app_label = validated_data.get('app_label', instance.app_label)
        targets_data = validated_data.pop('targets', None)
        instance = super().update(instance, validated_data)
        if targets_data is not None and scope_type == DataScope.ScopeType.FILTER:
            self._create_or_update_targets(instance, targets_data)
        elif scope_type != DataScope.ScopeType.FILTER:
            instance.targets.filter(app_label=app_label).delete()
        return instance
