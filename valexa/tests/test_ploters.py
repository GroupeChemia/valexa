import json
import os

import pytest

from plotly.utils import PlotlyJSONEncoder

from valexa.core.xlsx import XlsxHandler
from valexa.ploting.ploters import PloterData
import valexa.ploting.plotly.canvas as plotly_canvas
import valexa.ploting.mathplotlib.canvas as mpl_canvas
from valexa.ploting.mathplotlib.utils import fig_to_dict
from valexa.ploting.utils import profile_to_dict


@pytest.fixture(scope="module")
def filename():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, "data/test.xlsx")


class TestPloterData:
    @pytest.fixture(scope="class")
    def filehandler(self):
        return XlsxHandler

    @pytest.fixture(scope="class")
    def alternate_filehandler(self):
        class Handler(XlsxHandler):
            attr = "attr"

        return Handler
    
    @pytest.fixture(scope="class")
    def ploter_kwargs(self, alternate_filehandler):
        return {
            "tolerance_limit": 30,
            "handler": alternate_filehandler,
        }

    def test_load_data(self, filename):
        p = PloterData(filename)
        assert len(p.profiles) > 0

    def test_ploter_kwargs(self, filename, ploter_kwargs):
        p = PloterData(filename, **ploter_kwargs)
        assert p.tolerance_limit == ploter_kwargs["tolerance_limit"]
        assert p.handler == ploter_kwargs["handler"]
        assert len(p.profiles) > 0


@pytest.fixture(scope="module")
def ploter_data(filename):
    return PloterData(filename)

@pytest.fixture(scope="module")
def profile(ploter_data):
    return ploter_data.profiles[0]


class TestProfilePlotCanvas:
    def test_plotly_canvas(self, profile):
        canvas = plotly_canvas.ProfilePlotCanvas(profile)
        assert canvas.figure
        assert len(canvas.figure["data"]) == 6

    def test_mpl_canvas(self, profile):
        canvas = mpl_canvas.ProfilePlotCanvas(profile)
        assert canvas.figure
        assert canvas.axes
        
    def test_mpl_qtagg_canvas(self, profile):
        canvas = mpl_canvas.ProfilePlotCanvasQTAgg(profile)
        assert canvas.figure
        assert canvas.axes


class TestPlotingUtils:
    def test_profile_to_dict(self, profile):
        d = profile_to_dict(profile)
        for key, value in d.items():
            attr = getattr(profile, key, False)
            assert attr

    def test_serialize_mpl_figure(self, profile):
        mpl_figure = mpl_canvas.ProfilePlotCanvas(profile).figure
        string = json.dumps(
            fig_to_dict(mpl_figure), cls=PlotlyJSONEncoder
        )
        assert isinstance(string, str)
        assert len(string) > 0

    def test_PlotlyJSONEncoder(self, profile):
        plotly_figure = plotly_canvas.ProfilePlotCanvas(profile).figure
        string = json.dumps(
            plotly_figure, cls=PlotlyJSONEncoder
        )
        assert isinstance(string, str)
        assert len(string) > 0
