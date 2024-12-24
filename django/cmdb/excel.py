from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Protection, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
import json
from .constants import FieldMapping, FieldType, ValidationType
from .models import ModelInstance, ValidationRules, ModelFields, ModelFieldMeta, Models
from .serializers import ModelInstanceSerializer
from rest_framework import serializers
from .utils import password_handler

import logging
logger = logging.getLogger(__name__)

class ExcelHandler:
    @staticmethod
    def _handle_enum_data(enum_sheet, field, current_enum_col, template_sheet, col_letter, header_font):
        """处理枚举数据"""
        key_col_letter = get_column_letter(current_enum_col)
        val_col_letter = get_column_letter(current_enum_col + 1)
        
        # 设置标题
        enum_sheet.merge_cells(f'{key_col_letter}1:{val_col_letter}1')
        enum_sheet[f'{key_col_letter}1'] = f'{field.name}\r\n{field.verbose_name}'
        enum_sheet[f'{key_col_letter}1'].font = header_font
        enum_sheet[f'{key_col_letter}1'].alignment = Alignment(
            horizontal='center', 
            vertical='center', 
            wrap_text=True
        )
        
        # 设置列标识
        enum_sheet[f'{key_col_letter}2'] = '填写值'
        enum_sheet[f'{val_col_letter}2'] = '对应内容'
        
        # 获取枚举数据
        enum_data = {}
        if field.type == FieldType.MODEL_REF:
            ref_instances = ModelInstance.objects.filter(
                model=field.ref_model
            ).values_list('id', 'name')
            enum_data = {str(id): name for id, name in ref_instances}
        else:
            enum_data = json.loads(field.validation_rule.rule)
        
        # 写入数据
        for i, (key, value) in enumerate(enum_data.items(), 3):
            enum_sheet[f'{key_col_letter}{i}'] = key
            enum_sheet[f'{val_col_letter}{i}'] = value
            
        # 设置列宽和样式
        enum_sheet.column_dimensions[key_col_letter].width = 15
        enum_sheet.column_dimensions[val_col_letter].width = 15
        
        # 设置数据验证
        if len(enum_data) > 0:
            dv = DataValidation(
                type='list',
                formula1=f'=枚举类型可选值!${val_col_letter}$3:${val_col_letter}${len(enum_data)+2}',
                allow_blank=not field.required,
                showErrorMessage=True,
                errorTitle='输入错误',
                error='请从列表中选择一个值'
            )
        else:
            dv = DataValidation(
                type='custom',
                formula1='FALSE',
                allow_blank=not field.required,
                showErrorMessage=True,
                errorTitle='输入错误',
                error='该字段暂无可选值'
            )
        template_sheet.add_data_validation(dv)
        dv.add(f'{col_letter}4:{col_letter}1048576')
        
        return current_enum_col + 2, "枚举值" if field.type != FieldType.MODEL_REF else "关联模型"

    
    @staticmethod
    def generate_template(fields):
        """生成导入模板"""
        wb = Workbook()
        template_sheet = wb.active
        template_sheet.title = "数据模板"
        
        # 样式定义
        header_font = Font(bold=True)
        required_fill = PatternFill(start_color="FFFF0000", end_color="FFFF0000", fill_type="solid")
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 添加name列作为第一列
        name_col_letter = 'A'
        
        # 设置name列标题
        cell = template_sheet[f'{name_col_letter}1']
        cell.value = "name\r\n实例唯一标识"
        cell.font = header_font
        cell.fill = required_fill  # 必填标记
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        
        # 设置name列类型说明
        cell = template_sheet[f'{name_col_letter}2']
        cell.value = "string\r\n字符串"
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        
        # 设置name列约束说明
        cell = template_sheet[f'{name_col_letter}3']
        cell.value = "必填"
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        
        # 设置name列数据验证
        dv = DataValidation(
            type='custom',
            formula1='AND(LEN(A4)>0,COUNTIF(A4:A1048576,A4)=1)',
            showErrorMessage=True,
            errorTitle='输入错误',
            error='实例名称不能为空且不能重复'
        )
        template_sheet.add_data_validation(dv)
        dv.add(f'{name_col_letter}4:{name_col_letter}1048576')
        
        # 设置列宽
        template_sheet.column_dimensions[name_col_letter].width = 15
        
        # 创建枚举值工作表
        enum_sheet = wb.create_sheet("枚举类型可选值")
        
        # 记录枚举列的位置
        current_enum_col = 1
        
        # 写入表头
        for col, field in enumerate(fields, 2):
            logger.info(f'Handling column {col} for field {field.name}')
            col_letter = get_column_letter(col)
            
            # 第一行：字段名称
            cell =  template_sheet[f'{col_letter}1']
            cell.value = f"{field.name}\r\n{field.verbose_name}"
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            # 第二行：字段类型
            cell =  template_sheet[f'{col_letter}2']
            field_verbose_type = FieldMapping.FIELD_TYPES.get(field.type)
            cell.value = f"{field.type}\r\n{field_verbose_type}"
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            # 第三行：字段约束
            constraints = []
            if field.required:
                constraints.append("必填")
            
            logger.info(f'Field name, type and constraints set')
            
            if field.type == FieldType.MODEL_REF or (field.validation_rule and field.validation_rule.type == FieldType.ENUM):
                try:
                    current_enum_col, constraint = ExcelHandler._handle_enum_data(
                        enum_sheet, field, current_enum_col, 
                        template_sheet, col_letter, header_font
                    )
                    constraints.append(constraint)
                except Exception as e:
                    logger.error(f"Error handling enum data: {str(e)}")
            elif field.validation_rule:
                rule = field.validation_rule
                if rule.type == ValidationType.RANGE:
                    constraints.append(f"数值范围: {rule.rule.replace(',', ' ~ ')}")
                elif rule.type == ValidationType.REGEX:
                    constraints.append(f"正则规则: {rule.rule}")
            
            cell =  template_sheet[f'{col_letter}3']
            cell.value = "\r\n".join(constraints)
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            # 设置列宽
            template_sheet.column_dimensions[col_letter].width = 20
            
            # 标记必填字段
            if field.required:
                template_sheet[f'{col_letter}1'].fill = required_fill
                
            # 设置数据格式
            number_format = FieldMapping.TYPE_EXCEL_FORMATS.get(field.type)
            if number_format:
                column = template_sheet.column_dimensions[col_letter]
                column.number_format = number_format
        
        # 冻结前三行
        template_sheet.freeze_panes = 'A4'
        
        # 设置行高
        template_sheet.row_dimensions[1].height = 30
        template_sheet.row_dimensions[2].height = 30
        template_sheet.row_dimensions[3].height = 30
        enum_sheet.row_dimensions[1].height = 30

        
        # 锁定枚举表sheet
        enum_sheet.protection.enable()
        enum_sheet.protection.set_password('123456')
        
        return wb
    
    @staticmethod
    def generate_data_export(fields, instances):
        """生成实例数据导出"""
        wb = Workbook()
        data_sheet = wb.active
        data_sheet.title = "实例数据"
        
        # 复用模板格式设置
        header_font = Font(bold=True)
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 写入标题行
        col = 1
        name_col = get_column_letter(col)
        data_sheet[f'{name_col}1'] = "name"
        data_sheet[f'{name_col}1'].font = header_font
        data_sheet[f'{name_col}1'].alignment = center_alignment
        
        # 写入字段标题
        for field in fields:
            col += 1
            col_letter = get_column_letter(col)
            data_sheet[f'{col_letter}1'] = f'{field.name}\r\n{field.verbose_name}'
            data_sheet[f'{col_letter}1'].font = header_font
            data_sheet[f'{col_letter}1'].alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)            
            data_sheet.column_dimensions[col_letter].width = 20

        
        field_to_col = {
            field.name: get_column_letter(idx + 2)
            for idx, field in enumerate(fields)
        }
        
        # 写入实例数据
        for row, instance in enumerate(instances, 2):
            # 写入name
            data_sheet[f'A{row}'] = instance.name
            
            field_values = {}
            for field_meta in instance.field_values.all():
                value = field_meta.data
                
                # 处理枚举类型
                if (field_meta.model_fields.type == FieldType.ENUM and 
                    field_meta.model_fields.validation_rule and 
                    field_meta.model_fields.validation_rule.type == ValidationType.ENUM):
                    
                    # 从缓存获取枚举字典
                    rule_id = field_meta.model_fields.validation_rule.id
                    enum_dict = ValidationRules.get_enum_dict(rule_id)
                    value = enum_dict.get(value, None)
                # 处理关联模型
                elif field_meta.model_fields.type == FieldType.MODEL_REF:
                    ref_model = field_meta.model_fields.ref_model
                    ref_instance = ModelInstance.objects.filter(
                        model=ref_model, 
                        id=value
                    ).first()
                    value = ref_instance.name if ref_instance else None
                elif field_meta.model_fields.type == FieldType.PASSWORD:
                    value = password_handler.decrypt(value)    
                field_values[field_meta.model_fields.name] = value
                
            
            # 写入字段值
            for field_name, field_value in field_values.items():
                if field_name in field_to_col:
                    col_letter = field_to_col[field_name]
                    data_sheet[f'{col_letter}{row}'] = field_value
                
        
        data_sheet.row_dimensions[1].height = 30
        data_sheet.freeze_panes = 'A2'
        
        return wb
    

    def import_data(self, file_path, model_id):
        """
        从Excel导入实例数据
        """
        # 加载Excel文件
        wb = load_workbook(file_path)
        # determine if the file owns the sheet
        if '数据模板' not in wb.sheetnames:
            raise serializers.ValidationError('Invalid file format')
        elif '枚举类型可选值' not in wb.sheetnames:
            raise serializers.ValidationError('Invalid file format')
        data_sheet = wb['数据模板']
        enum_sheet = wb['枚举类型可选值']

        # 获取字段映射
        field_mapping = {}
        for col in range(2, data_sheet.max_column + 1):
            column_letter = get_column_letter(col)
            field_cell = data_sheet[f'{column_letter}1']
        
            if not field_cell.value:
                continue
                
            # 解析字段名格式：name\nverbose_name
            try:
                field_name = field_cell.value.split('\n')[0].strip()
                if field_name:
                    field_mapping[column_letter] = field_name
            except (AttributeError, IndexError):
                logger.warning(f"Invalid field name format in column {column_letter}")
                continue
        
        # 获取模型
        model = Models.objects.get(id=model_id)
        
        # 处理结果统计
        results = {
            'created': 0,
            'updated': 0,
            'errors': []
        }

        # 处理每行数据
        for row in range(2, data_sheet.max_row + 1):
            try:
                # 获取实例名称
                name = data_sheet['A{row}'].value
                if not name:
                    continue

                # 构建实例数据
                instance_data = {
                    'name': name,
                    'model': model_id,
                    'field_values': []
                }

                # 收集字段值
                for column, field_name in field_mapping.items():
                    value = data_sheet[f'{column}{row}'].value
                    if value is None:
                        continue

                    field = model.modelfields_set.get(name=field_name)
                    
                    # 处理特殊字段类型
                    if field.type == FieldType.PASSWORD:
                        value = password_handler.encrypt(str(value))
                    elif field.type == FieldType.MODEL_REF:
                        ref_instance = ModelInstance.objects.filter(
                            model=field.ref_model,
                            name=value
                        ).first()
                        if ref_instance:
                            value = str(ref_instance.id)
                        else:
                            raise serializers.ValidationError(
                                f'Referenced instance not found: {value}'
                            )
                    elif (field.type == FieldType.ENUM and 
                        field.validation_rule and 
                        field.validation_rule.type == ValidationType.ENUM):
                        enum_dict = ValidationRules.get_enum_dict(field.validation_rule.id)
                        enum_key = None
                        for k, v in enum_dict.items():
                            if v == value:
                                enum_key = k
                                break
                        if enum_key is None:
                            raise serializers.ValidationError(
                                f'Invalid enum value: {value}'
                            )
                        value = enum_key

                    instance_data['field_values'].append({
                        'model_fields': field.id,
                        'data': value
                    })

                # 检查实例是否存在
                instance = ModelInstance.objects.filter(
                    model=model,
                    name=name
                ).first()

                if instance:
                    # 更新实例
                    serializer = ModelInstanceSerializer(
                        instance,
                        data=instance_data,
                        context={'model': model}
                    )
                    results['updated'] += 1
                else:
                    # 创建实例
                    serializer = ModelInstanceSerializer(
                        data=instance_data,
                        context={'model': model}
                    )
                    results['created'] += 1

                serializer.is_valid(raise_exception=True)
                serializer.save()

            except Exception as e:
                results['errors'].append({
                    'row': row,
                    'name': name,
                    'error': str(e)
                })

        return results