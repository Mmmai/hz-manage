import contextlib
from django.contrib import admin
from .models import (
    ModelGroups,
    Models,
    ModelFieldGroups,
    ValidationRules,
    ModelFields,
    ModelFieldOrder,
    ModelFieldPreference,
    UniqueConstraint,
    ModelInstance,
    ModelFieldMeta,
    ModelInstanceGroup,
    ModelInstanceGroupRelation,
    RelationDefinition,
    Relations
)
from django.apps import apps

# Register models
admin.site.register(ModelGroups)
admin.site.register(Models)
admin.site.register(ModelFieldGroups) 
admin.site.register(ValidationRules)
admin.site.register(ModelFields)
admin.site.register(ModelFieldOrder)
admin.site.register(ModelFieldPreference)
admin.site.register(UniqueConstraint)
admin.site.register(ModelInstance)
admin.site.register(ModelFieldMeta)
admin.site.register(ModelInstanceGroup)
admin.site.register(ModelInstanceGroupRelation)
admin.site.register(RelationDefinition)
admin.site.register(Relations)

# Register your models here.
models = apps.get_app_config('cmdb').get_models()
for model in models:
    with contextlib.suppress(Exception):
        admin.site.register(model)