from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import (
    ModelGroups,
    Models, 
    ModelFieldGroups,
    ValidationRules,
    ModelFields, 
    UniqueConstraint,
    ModelInstance, 
    ModelFieldMeta, 
    RelationDefinition, 
    Relations,
)


@receiver(post_save, sender=ModelFields)
def create_field_meta_for_instances(sender, instance, created, **kwargs):
    if created:
        # 获取所有关联的 ModelInstance 实例
        instances = ModelInstance.objects.filter(model=instance.model)

        for model_instance in instances:
            # 检查是否已经存在对应的 ModelFieldMeta 记录
            if not ModelFieldMeta.objects.filter(
                model_instance=model_instance,
                model_fields=instance
            ).exists():
                field_value = instance.default if instance.default is not None else None

                if instance.required and field_value is None:
                    raise ValidationError(f'Required field {instance.name} is missing default value')

                ModelFieldMeta.objects.create(
                    model=instance.model,
                    model_instance=model_instance,
                    model_fields=instance,
                    data=field_value,
                    create_user='system',
                    update_user='system'
                )