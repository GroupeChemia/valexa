import json

from matplotlib.figure import Figure
from mpld3.mpld3renderer import MPLD3Renderer
from mpld3.mplexporter import Exporter

from plotly.utils import PlotlyJSONEncoder

def fig_to_dict(fig: Figure, **kwargs) -> dict:
    """Output json-serializable dictionary representation of the figure

    **kwargs :
        Additional keyword arguments passed to mplexporter.Exporter
    """
    renderer = MPLD3Renderer()
    Exporter(renderer, close_mpl=False, **kwargs).run(fig)
    fig, figure_dict, extra_css, extra_js = renderer.finished_figures[0]
    return figure_dict

    
def fig_to_json(fig: Figure, encoder=PlotlyJSONEncoder) -> str:
    """Converts a matplotlib Figure to a Json string"""

    return json.dumps(fig_to_dict(fig), cls=encoder)
    