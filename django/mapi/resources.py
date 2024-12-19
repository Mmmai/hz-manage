from import_export import resources
from .models import Portal,Pgroup
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

class PortalResource(resources.ModelResource):
    fieldsList = []
    names = locals()
    for i in Portal._meta.get_fields():
        if i._verbose_name:
            # print(i._verbose_name)
            # Field(attribute=i.name, column_name=i._verbose_name)
            # exec('{} = {}'.format(i.name,Field(attribute=i.name, column_name=i._verbose_name)))
            if i.name == 'group':
                names[i.name] = Field(attribute=i.name, column_name=i._verbose_name, widget=ForeignKeyWidget(Pgroup, 'group'))
            elif i.name in ['id','target'] :
                continue
            else:
                names[i.name] = Field(attribute=i.name, column_name=i._verbose_name)

            fieldsList.append(i.name)
    print(fieldsList)
    class Meta:
        model = Portal
        #导入导出的字段
        # fields = set(fieldsList)
        # export_order = ('name', 'group',)
        # import_id_fields = ['name']
        exclude = ['id','update_time','create_time','target']

