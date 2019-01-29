from enum import Enum

import openpyxl
from openpyxl.worksheet import Worksheet
from openpyxl import Workbook
from os import path
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image
import io
import urllib, base64

CALIBRATION_SHEET_NAME = "Calibration_STD"
VALIDATION_SHEET_NAME = "Validation_STD"


class ColIndex(Enum):
    SERIES = 1
    LEVEL = 2
    CONCENTRATION = 3
    RESPONSE = 4


class XlsxHandler:
    def __init__(self, filename: str):
        print(filename)
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

class XlsxWriter:

    def __init__(self, profile_to_use):
        self.profile = profile_to_use

    def write_profile(self, file_name):
        workbook_file_name = file_name + '.xlsx'
        if not self.__valid_if_file_exist(workbook_file_name):
            working_workbook = Workbook()
            working_workbook.save(workbook_file_name)

        working_workbook = openpyxl.load_workbook(workbook_file_name)

        if not self.profile.model.name  in working_workbook.sheetnames:
            working_workbook.create_sheet(self.profile.model.name)

        working_sheet = working_workbook[self.profile.model.name]
        working_sheet['A1'] = self.profile.name_of_file
        working_sheet['A2'] = 'Limit of Quantification'
        working_sheet['B2'] = self.profile.min_lq
        working_sheet.add_image(Image('Linear fig.png'), 'A3')

        working_workbook.save(workbook_file_name)



    def __valid_if_file_exist(self, file_name):
        return path.exists(file_name)

class HtmlWriter:

    def __init__(self, profile_to_use):
        self.profile = profile_to_use

    def write_profile(self, file_name):

        if not self.__valid_if_file_exist(file_name):
            file = open(file_name, 'w')
            file.write('''<!DOCTYPE html>     
                <html>
                <head>
                <style>
                    table, th, td {
                        border: 1px solid black;
                        border-collapse: collapse;
                    }
                </style>
                </head>
                <body>''')
            file.close()

        file = open(file_name, 'a')

        file.write(f'''<table style="border: 1px solid black">
              <tr style="border: 1px solid black">
                <th>File name</th>
                <th colspan="7">{self.profile.name_of_file}</th>
              </tr>
              <tr style="border: 1px solid black">
                <td>Modèle</td>
                <td colspan="3">{self.profile.model.name}</td>
                <td>beta</td>
                <td>{self.profile.tolerance_limit}</td>
                <td>t</td>
                <td>{self.profile.acceptance_limit}</td>
              </tr>
              <tr style="border: 1px solid black">
                <td>LOQ Min</td>
                <td colspan="3">{self.profile.min_lq}</td>
                <td>LOQ Max</td>
                <td colspan="3">{self.profile.max_lq}</td>
              </tr>
              <tr style="border: 1px solid black">
                <td>LOD</td>
                <td colspan="3">{self.profile.ld}</td>
                <td>Corr. Factor.</td>
                <td>{self.profile.model.correction_factor}</td>
                <td>Recovery</td>
                <td>{1/self.profile.model.correction_factor*100}</td>
              </tr>
              <tr style="border: 1px solid black">
                <td colspan="8"></td>
              </tr>
              <tr style="border: 1px solid black">
                <td rowspan="2">Concentration</td>
                <td rowspan="2">Mesuré</td>
                <td colspan="2">Exactitude</td>
                <td colspan="2">Précision</td>
                <td colspan="2">Justesse</td>
              </tr>
              <tr style="border: 1px solid black">
                <td>Biais absolue</td>
                <td>Biais relatif</td>
                <td>Répétabilité (%%RSD)</td>
                <td>Intermédiaire (%%RSD)</td>
                <td>Limite de tolérance</td>
                <td>Limite relative</td>
              </tr>''')

        for list_item in self.profile.levels:
              file.write(f'''<tr style="border: 1px solid black"> 
                <td>{list_item.introduced_concentration:.3f}</td>
                <td>{list_item.calculated_concentration:.3f}</td>
                <td>{list_item.bias:.3f}</td>
                <td>{list_item.relative_bias:.2f}</td>
                <td>{list_item.repeatability_std_pc:.3f}</td>
                <td>{list_item.inter_series_std_pc:.3f}</td>
                <td>[{list_item.abs_tolerance[0]:.2f},{list_item.abs_tolerance[1]:.2f}]</td>
                <td>[{-100 + list_item.rel_tolerance[0]:.2f},{-100 + list_item.rel_tolerance[1]:.2f}]</td>
              </tr>''')

        self.profile.image_data.seek(0)

        image_string = base64.b64encode(self.profile.image_data.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(image_string)
        file.write(f'''<tr style="border: 1px solid black">
                        <td colspan="8"></td>
                      </tr>
                      <tr style="border: 1px solid black">
                        <td colspan="8">'<img src = "{uri}"/>'</td>
                      </tr>
                    </table>
                    <br>''')
        file.close()

    def __valid_if_file_exist(self, file_name):
        return path.exists(file_name)