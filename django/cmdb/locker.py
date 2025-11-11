from django.db import connection
from .models import ModelInstance, ModelFieldMeta

def lock_model_instance_for_update(object_id, nowait=False):
    db_engine = connection.settings_dict['ENGINE']

    # 适配未来可能使用的其他数据库
    if 'postgresql' in db_engine:
        instance = ModelInstance.objects.select_for_update(of=('self',), nowait=nowait).get(pk=object_id)
        list(ModelFieldMeta.objects.filter(model_instance_id=object_id).select_for_update(nowait=nowait))
        return instance

    # MySQL
    instance = ModelInstance.objects.select_for_update(nowait=nowait).get(pk=object_id)
    list(ModelFieldMeta.objects.filter(model_instance_id=object_id).select_for_update(nowait=nowait))
    return instance