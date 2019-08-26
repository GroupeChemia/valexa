from plotly.subplots import make_subplots
import plotly.graph_objects as go


class ProfilePlotCanvas:

    def __init__(self, profile, width=750, height=800):
        
        self.profile = profile
        self.figure = go.Figure({
            "layout": {
                "width": width,
                "height": height
            }
        })
        self._make_plot()

    def _make_plot(self):
        p = self.profile
        fig = self.figure

        levels_x = [l.calculated_concentration for l in p.levels]

        fig.add_trace(go.Scatter(x=levels_x, y=[l.recovery for l in p.levels],
                            name="Recovery",
                            line=dict(color="purple")))
        fig.add_trace(go.Scatter(x=levels_x, y=[l.rel_tolerance[0] for l in p.levels],
                            name="Min tolerance limit", mode="lines", 
                            line=dict(width=1, color="blue")))
        fig.add_trace(go.Scatter(x=levels_x, y=[l.rel_tolerance[1] for l in p.levels],
                            name="Max tolerance limit" ,mode="lines", 
                            line=dict(width=1, color="green")))
        fig.add_trace(go.Scatter(x=levels_x, y=[p.acceptance_interval[0] for _ in p.levels],
                            name="Acceptance limit", mode="lines", 
                            marker=dict(color="black"),
                            line=dict(dash="dash")))
        fig.add_trace(go.Scatter(x=levels_x, y=[p.acceptance_interval[1] for _ in p.levels],
                            name="Acceptance limit", mode="lines", 
                            showlegend=False,
                            marker=dict(color="black"),
                            line_dash="dash"))

        results_x = [s.concentration for s in p.series]
        results_y = [(s.result / s.concentration) * 100 for s in p.series]

        fig.add_scatter(x=results_x, y=results_y, 
                            name=None, mode="markers",
                            showlegend=False,
                            marker=dict(opacity=0.5, size=2))

        fig.update_layout(
              title_text="Stacked Subplots with Shared X-Axes",
              paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor='rgba(0,0,0,0)',
        )
        fig.update_yaxes(
            title_text="Recovery (%)",
            showline=True, linecolor="black", 
            ticks="inside", tickwidth=1, tickcolor="black", ticklen=4,
        )
        fig.update_xaxes(
            title_text="Concentration",
            position=0.50, 
            showline=True, linecolor="black", 
            ticks="inside", tickwidth=1, tickcolor="black", ticklen=4,
        )

