from import_export import resources
from .models import Portal,Pgroup
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

class PortalResource(resources.ModelResource):
    # 自定义字段用于处理多对多关系
    groups_names = Field(attribute='groups', column_name='分组')
    
    class Meta:
        model = Portal
        exclude = ['id','update_time','create_time','target']
        fields = ('name', 'url', 'status', 'username', 'password', 
                 'describe', 'sharing_type', 'groups_names')
    
    def dehydrate_groups_names(self, portal):
        # 将多对多关系转换为分组名称的逗号分隔字符串
        return ', '.join([group.group for group in portal.groups.all()])
    
    def save_m2m(self, instance, row, **kwargs):
        # 保存多对多关系
        if 'groups_names' in row:
            group_names = [name.strip() for name in row['groups_names'].split(',') if name.strip()]
            groups = []
            for group_name in group_names:
                # 查找或创建分组（这里简化处理，实际项目中可能需要更复杂的逻辑）
                group, created = Pgroup.objects.get_or_create(
                    group=group_name,
                    defaults={
                        'sharing_type': 'public',  # 默认为公共分组
                        'owner': instance.owner  # 所有者默认为门户创建者
                    }
                )
                groups.append(group)
            instance.groups.set(groups)
        return instance
