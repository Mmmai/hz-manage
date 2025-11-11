import json
import logging
from django.db import transaction
from .constants import FieldType
from .utils import password_handler
from .models import ModelFields, ModelFieldMeta
from .serializers import ModelInstanceSerializer

logger = logging.getLogger(__name__)

def restore_model_instance(instance, snapshot, field_details=None, request_user=None):
    
    # ModelFields = instance.model.fields.model
    # ModelFieldMeta = instance.field_values.model
    # logger.info(f'ModelFields: {ModelFields}, ModelFieldMeta: {ModelFieldMeta}')
    update_data = {}
    
    instance_name_history = snapshot.get('instance_name')
    using_template_history = snapshot.get('using_template')
    if instance_name_history and isinstance(instance_name_history, list):
        update_data['instance_name'] = instance_name_history[0]
    if using_template_history and isinstance(using_template_history, list):
        update_data['using_template'] = using_template_history[0]
    
    model = instance.model
    
    fields_dict = {}
    
    if field_details:
        for field_detail in field_details:
            field = ModelFields.objects.filter(model=model, name=field_detail.name).first()
            if not field:
                continue
            field_type = field.type
            if field_type == FieldType.ENUM:
                old_value = json.loads(old_value)
                key = old_value.get('key') if isinstance(old_value, dict) else None
                fields_dict[field_detail.name] = key
            elif field_type == FieldType.MODEL_REF:
                old_value = json.loads(old_value)
                instance_id = old_value.get('id') if isinstance(old_value, dict) else None
                fields_dict[field_detail.name] = instance_id
            elif field_type == FieldType.PASSWORD:
                encrypted_value = password_handler.encrypt(old_value)
                fields_dict[field_detail.name] = encrypted_value
            else:
                fields_dict[field_detail.name] = field_detail.old_value
            
            fields_dict[field_detail.name] = field_detail.old_value
    
    update_data['fields'] = fields_dict
    
    ser = ModelInstanceSerializer(
        instance, 
        data=update_data, 
        context={'request_user': request_user}, 
        partial=True
    )
    
    ser.is_valid(raise_exception=True)
    ser.save(update_user=request_user)

    #         old_value = field_detail.old_value
            
    #         if field_detail.old_value == field_detail.new_value:
    #             continue
            
    #         field_meta = ModelFieldMeta.objects.filter(
    #             model_instance=instance, 
    #             model_fields=field
    #         ).select_related('model_fields')

    #         if field_meta:
    #             field_meta.delete()
                

                    
    # instance.save(update_fields=['instance_name', 'using_template', 'update_time', 'update_user'])