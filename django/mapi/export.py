from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Protection, Alignment

class exportHandler:
    @staticmethod
    def get_template(colList):
        wb = Workbook()
        sheet = wb.active
        sheet.title = "sheet1"
        # 样式定义
        header_font = Font(bold=True)
        required_fill = PatternFill(start_color="FFFF0000", end_color="FFFF0000", fill_type="solid")
        center_alignment = Alignment(horizontal='center', vertical='center')
        for i in colList:

            sheet.append(i)
        return wb
    @staticmethod
    def get_portal(colList):
        wb = Workbook()
        sheet = wb.active
        sheet.title = "sheet1"
        # 样式定义
        header_font = Font(bold=True)
        required_fill = PatternFill(start_color="FFFF0000", end_color="FFFF0000", fill_type="solid")
        center_alignment = Alignment(horizontal='center', vertical='center')
        for i in colList:
            sheet.append(i)
        return wb        