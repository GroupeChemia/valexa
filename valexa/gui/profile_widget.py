from PyQt5 import QtGui
from PyQt5.QtGui import QPalette

from PyQt5.QtWidgets import QWidget, QTableWidgetItem

from valexa.core.profiles import Profile
from valexa.gui.Ui_profile_widget import Ui_profileWidget
from valexa.ploting.mathplotlib.canvas import ProfilePlotCanvasQTAgg \
                                                        as ProfilePlotCanvas


class ProfileWidget(QWidget, Ui_profileWidget):
    def __init__(self, profile: Profile):
        super().__init__()
        self.profile = profile
        self.setupUi(self)
        self.setBackgroundRole(QPalette.Light)

        plot_canvas = ProfilePlotCanvas(profile=profile)
        self.frame_layout.addWidget(plot_canvas)

        self.name_label.setText(self.profile.model.name)
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
        table.setRowCount(len(self.profile.levels))
        table.setColumnCount(6)
        for (index, l) in enumerate(self.profile.levels):
            table.setItem(index, 0, QTableWidgetItem(f'{l.introduced_concentration:.3f}'))
            table.setItem(index, 1, QTableWidgetItem(f'{l.calculated_concentration:.3f}'))
            table.setItem(index, 2, QTableWidgetItem(f'{l.bias:.3f}'))
            table.setItem(index, 3, QTableWidgetItem(f'{l.relative_bias:.2f}'))
            table.setItem(index, 4, QTableWidgetItem(f'{l.recovery:.1f}'))
            table.setItem(index, 5, QTableWidgetItem(f'[{l.abs_tolerance[0]:.2f},{l.abs_tolerance[1]:.2f}]'))

        table.setHorizontalHeaderLabels(
            ["Concentration", "Calculated concentration", "Absolute bias", "Relative biais (%)", "Recovery (%)", "Tolerance Interval"])
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
