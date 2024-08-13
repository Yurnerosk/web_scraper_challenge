from RPA.Excel.Files import Files
from datetime import datetime
from typing import Tuple
import os

class ExcelManager:

    excel = Files()

    def write_in_excel_file(self, data: Tuple):
        # Verify if input data is empty
        if not data:
            raise ValueError('The input data variable is empty')
        # Create File name and Path
        output_folder = os.path.join('.', 'output')
        name = 'Output' + datetime.today().strftime('_%Y-%m-%d_%H-%M-%S') + '.xlsx'
        filename = os.path.join(output_folder, name)
        # Create Excel file and store data
        wb = self.excel.create_workbook(filename, sheet_name=f'Fresh News')
        self.excel.append_rows_to_worksheet(data, header=True)
        wb.save()