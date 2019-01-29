from PyQt5 import QtGui
from PyQt5.QtGui import QPalette

from PyQt5.QtWidgets import QWidget, QTableWidgetItem

from valexa.core.profiles import Profile
from valexa.gui.Ui_profile_widget import Ui_profileWidget
from valexa.gui.profile_plot_canvas import ProfilePlotCanvas


class ProfileWidget(QWidget, Ui_profileWidget):
    def __init__(self, profile: Profile):
        super().__init__()
        self.profile = profile
        self.setupUi(self)
        self.setBackgroundRole(QPalette.Light)

        plot_canvas = ProfilePlotCanvas(profile=profile)
        self.frame_layout.addWidget(plot_canvas)

        self.name_label.setText(self.profile.name_of_file + ' ' + self.profile.model.name)
        if self.profile.has_limits:
            self.min_lq_label.setText(f"Min limit of quantification: {self.profile.min_lq:.3f}")
            self.max_lq_label.setText(f"Max limit of quantification: {self.profile.max_lq:.3f}")
            self.ld_label.setText(f"Limit of detection: {self.profile.ld:.3f}")
        else:
            self.min_lq_label.setText(f"Min limit of quantification: N/A")
            self.max_lq_label.setText(f"Max limit of quantification: N/A")
            self.ld_label.setText(f"Limit of detection: N/A")
        self.correction_label.hide()
        if self.profile.model.has_correction:
            self.correction_label.show()
            self.correction_label.setText(f"Correction factor: {self.profile.model.correction_factor}")

        self.create_table()


    def create_table(self):
        table = self.table_widget
        table.setRowCount(len(self.profile.levels)+2)
        table.setColumnCount(8)

        table.setSpan(0, 0, 2, 1)
        table.setSpan(0, 1, 2, 1)
        table.setSpan(0, 2, 1, 2)
        table.setSpan(0, 4, 1, 2)
        table.setSpan(0, 6, 1, 2)

        table.setItem(0, 0, QTableWidgetItem('Concentration'))
        table.setItem(0, 1, QTableWidgetItem('Mesuré'))
        table.setItem(0, 2, QTableWidgetItem('Exactitude'))
        table.setItem(0, 4, QTableWidgetItem('Précision'))
        table.setItem(0, 6, QTableWidgetItem('Justesse'))

        table.setItem(1, 2, QTableWidgetItem('Biais absolue'))
        table.setItem(1, 3, QTableWidgetItem('Biais relatif'))

        table.setItem(1, 4, QTableWidgetItem('Répétablité (%RSD)'))
        table.setItem(1, 5, QTableWidgetItem('Précision intermédaire (%RSD)'))

        table.setItem(1, 6, QTableWidgetItem('Intervales de tolérance'))
        table.setItem(1, 7, QTableWidgetItem('Limite de tolérance relative'))


        for (index, list_item) in enumerate(self.profile.levels):
            table.setItem(index + 2, 0, QTableWidgetItem(f'{list_item.introduced_concentration:.3f}'))
            table.setItem(index + 2, 1, QTableWidgetItem(f'{list_item.calculated_concentration:.3f}'))
            table.setItem(index + 2, 2, QTableWidgetItem(f'{list_item.bias:.3f}'))
            table.setItem(index + 2, 3, QTableWidgetItem(f'{list_item.relative_bias:.2f}'))
            table.setItem(index + 2, 4, QTableWidgetItem(f'{list_item.repeatability_std_pc:.3f}'))
            table.setItem(index + 2, 5, QTableWidgetItem(f'{list_item.inter_series_std_pc:.3f}'))
            #table.setItem(index+1, 4, QTableWidgetItem(f'{list_item.recovery:.1f}'))
            table.setItem(index + 2, 6,
                          QTableWidgetItem(f'[{list_item.abs_tolerance[0]:.2f},{list_item.abs_tolerance[1]:.2f}]'))
            table.setItem(index + 2, 7,
                          QTableWidgetItem(f'[{-100 + list_item.rel_tolerance[0]:.2f},{-100 + list_item.rel_tolerance[1]:.2f}]'))

        #table.setHorizontalHeaderLabels(
        #    ["Concentration", "Calculated concentration", "Absolute bias", "Relative biais (%)", "Recovery (%)", "Tolerance Interval", "Repetability STD", "Inter Rep STD"])
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.horizontalHeader().hide()
