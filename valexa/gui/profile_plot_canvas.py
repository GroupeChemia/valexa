import mpl_toolkits.axisartist as AA
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import io

class ProfilePlotCanvas(FigureCanvas):

    def __init__(self, profile, parent=None, width=15, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = AA.Subplot(fig, 111)
        fig.add_subplot(self.axes)

        super().__init__(fig)

        self.setParent(parent)

        super().setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        super().updateGeometry()

        profile.make_plot(self.axes)

        profile.image_data = io.BytesIO()
        fig.savefig(profile.image_data, format='png')


