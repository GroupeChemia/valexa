from enum import Enum

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

CALIBRATION_SHEET_NAME = "Calibration_STD"
VALIDATION_SHEET_NAME = "Validation_STD"


class ColIndex(Enum):
    SERIES = 1
    LEVEL = 2
    CONCENTRATION = 3
    RESPONSE = 4


class XlsxHandler:
    def __init__(self, filename: str):
        self.workbook = openpyxl.load_workbook(filename=filename)
        self.__valid_xlsx()

    def __valid_xlsx(self):
        if CALIBRATION_SHEET_NAME not in self.workbook.sheetnames or \
                VALIDATION_SHEET_NAME not in self.workbook.sheetnames:
            raise ValueError("Bad format of Xlsx file. Use the right template")

    def get_calibration_data(self):
        return self.__get_data(CALIBRATION_SHEET_NAME)

    def get_validation_data(self):
        return self.__get_data(VALIDATION_SHEET_NAME)

    def __get_data(self, sheet_name):
        sheet: Worksheet = self.workbook[sheet_name]
        data = []
        for row in list(sheet.rows)[3:]:
            row_values = (
                row[ColIndex.SERIES.value].value,
                row[ColIndex.LEVEL.value].value,
                row[ColIndex.CONCENTRATION.value].value,
                row[ColIndex.RESPONSE.value].value
            )
            data.append(row_values)

        return data
