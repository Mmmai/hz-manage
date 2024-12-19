from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Protection, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
import json
from .constants import FieldMapping, FieldType, ValidationType
from .models import ModelInstance
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
                formula1='FALSE',  # 永远返回False的公式
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
        
        # 创建枚举值工作表
        enum_sheet = wb.create_sheet("枚举类型可选值")
        
        # 记录枚举列的位置
        current_enum_col = 1
        
        # 写入表头
        for col, field in enumerate(fields, 1):
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
