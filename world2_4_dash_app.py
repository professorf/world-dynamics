# SPDX-License-Identifier: MIT
"""
World2 in the browser: an interactive app built on world2_3_modern.py.

Authors: Nick V. Flor (University of New Mexico, nickflor@unm.edu) and
         Claudia (Claude Interactive Assistant), i.e., Claude, an AI model by Anthropic.
License: MIT (see LICENSE). To cite this code, see CITE.md.
Model:   Jay W. Forrester's World2, from World Dynamics (1971; 2nd ed. 1973).

HOW THIS FILE RELATES TO THE OTHERS

The model lives in world2_3_modern.py, the version checked against the book.
This app imports simulate() from there and only draws what it returns, so
there is still one copy of the model, and any change to it happens in that file.

STAGE 1 (this version)

The book's standard run, drawn as the two plots the DYNAMO listing asks for:
its two PLOT cards, which are the book's Figures 4-1 and 4-2. There are no
controls yet, so the page is built once, when the app starts.

Run:  python world2_4_dash_app.py
then open http://127.0.0.1:8050 in a browser. Needs dash (pip install dash).
"""

import plotly.graph_objects as go
from dash import Dash, dcc, html

from world2_3_modern import STANDARD_POLICY, simulate


# ---------------------------------------------------------------------------
# What to plot
#
# The two PLOT cards at the end of source-code.dyn:
#   PLOT P=P(0,8E9)/POLR=2(0,40)/CI=C(0,20E9)/QL=Q(0,2)/NR=N(0,1000E9)
#   PLOT FR=F,MSL=M,QLC=4,QLP=5(0,2)/CIAF=A(.2,.6)
# DYNAMO drew every variable on one shared frame, each on its own scale.
# Here each variable gets its own small chart instead, keeping the book's scale,
# so the shapes can be compared with the book's figures.
# ---------------------------------------------------------------------------

#   (name in the results,                          panel title,                                        divide by, book's scale)
PLOT_1 = [
    ("population",                                 "Population, billions (P)",                         1e9, (0, 8)),
    ("pollution_ratio",                            "Pollution ratio (POLR)",                           1,   (0, 40)),
    ("capital_investment",                         "Capital investment, billions (CI)",                1e9, (0, 20)),
    ("quality_of_life",                            "Quality of life (QL)",                             1,   (0, 2)),
    ("natural_resources",                          "Natural resources, billions (NR)",                 1e9, (0, 1000)),
]
PLOT_2 = [
    ("food_ratio",                                 "Food ratio (FR)",                                  1,   (0, 2)),
    ("material_standard_of_living",                "Material standard of living (MSL)",                1,   (0, 2)),
    ("quality_of_life_from_crowding",              "Quality of life from crowding (QLC)",              1,   (0, 2)),
    ("quality_of_life_from_pollution",             "Quality of life from pollution (QLP)",             1,   (0, 2)),
    ("capital_investment_in_agriculture_fraction", "Agricultural capital fraction (CIAF)",             1,   (.2, .6)),
]

# Colors and type (a validated data-visualization palette)
SURFACE = "#fcfcfb"     # chart background
PAGE = "#f9f9f7"        # page background
INK = "#0b0b0b"         # titles
SECONDARY = "#52514e"   # body text and tick labels
MUTED = "#898781"       # hover line
GRID = "#e1e0d9"        # gridlines
AXIS = "#c3c2b7"        # x-axis line
LINE = "#2a78d6"        # the run
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def panel(run, name, title, divide_by, scale):
    """One variable in its own small chart, on the book's scale."""
    low, high = scale
    values = run[name] / divide_by
    fig = go.Figure(go.Scatter(x=run["year"], y=values, mode="lines",
                               line={"color": LINE, "width": 2},
                               hovertemplate="%{y:.3g}<extra></extra>"))
    fig.update_xaxes(range=[run["year"][0], run["year"][-1]], dtick=50,
                     showline=True, linecolor=AXIS, gridcolor=GRID, zeroline=False,
                     spikethickness=1, spikecolor=MUTED, spikedash="solid", hoverformat=".1f")
    # The book's scale, stretched only if a run goes past it
    fig.update_yaxes(range=[min(low, values.min()), max(high, values.max() * 1.05)],
                     gridcolor=GRID, zeroline=False, nticks=5)
    fig.update_layout(title={"text": title, "x": 0, "xanchor": "left", "y": 0.96,
                             "font": {"size": 13, "color": INK}},
                      height=240, margin={"l": 40, "r": 16, "t": 40, "b": 32},
                      paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, showlegend=False,
                      hovermode="x unified",
                      font={"family": FONT, "size": 12, "color": SECONDARY})
    return fig


def panels(run, plot):
    """A grid of small charts, one per variable on a PLOT card. The grid wraps
    onto more rows when the window is narrow."""
    return html.Div(className="panels", children=[
        dcc.Graph(id=name, figure=panel(run, name, title, divide_by, scale),
                  config={"displayModeBar": False})
        for name, title, divide_by, scale in plot])


def values_table(run, panels, every_years=10):
    """The same numbers as a table, one row every few years."""
    step = round(every_years / (run["year"][1] - run["year"][0]))
    header = html.Tr([html.Th("Year")] + [html.Th(title) for _, title, _, _ in panels])
    rows = [html.Tr([html.Td(f"{run['year'][i]:.0f}")]
                    + [html.Td(f"{run[name][i] / divide_by:.3g}") for name, _, divide_by, _ in panels])
            for i in range(0, len(run["year"]), step)]
    return html.Table([html.Thead(header), html.Tbody(rows)], className="values")


# ---------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------

run = simulate(STANDARD_POLICY)

app = Dash(__name__, title="World2")
app.index_string = app.index_string.replace("</head>", f"""<style>
  body {{ margin: 0; background: {PAGE}; color: {SECONDARY}; font-family: {FONT}; }}
  .page {{ max-width: 1500px; margin: 0 auto; padding: 24px 16px 48px; }}
  h1 {{ color: {INK}; font-size: 24px; margin: 0 0 6px; }}
  h2 {{ color: {INK}; font-size: 16px; margin: 28px 0 8px; }}
  p {{ margin: 0; max-width: 72em; line-height: 1.45; }}
  .panels {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 8px; }}
  details {{ margin-top: 28px; overflow-x: auto; }}
  summary {{ cursor: pointer; color: {INK}; font-weight: 600; }}
  .values {{ border-collapse: collapse; margin-top: 12px; font-size: 13px;
             font-variant-numeric: tabular-nums; }}
  .values th, .values td {{ padding: 4px 10px; text-align: right; border-bottom: 1px solid {GRID}; }}
  .values th {{ color: {INK}; font-weight: 600; vertical-align: bottom; max-width: 9em; }}
</style>
</head>""")

app.layout = html.Div(className="page", children=[
    html.H1("World2: the standard run"),
    html.P("Jay W. Forrester's world model from World Dynamics (1971), computed by "
           "simulate() in world2_3_modern.py. Each panel keeps the scale the book plots "
           "it on, so the curves can be compared with the book's Figures 4-1 and 4-2. "
           "Hover over a panel to read its values."),

    html.H2("First PLOT card (book Figure 4-1)"),
    panels(run, PLOT_1),

    html.H2("Second PLOT card (book Figure 4-2)"),
    panels(run, PLOT_2),

    html.Details([html.Summary("The same values as a table, every 10 years"),
                  values_table(run, PLOT_1 + PLOT_2)]),
])


if __name__ == "__main__":
    # app.run(debug=True) adds Dash's developer tools, and reloads the page
    # whenever you save a change to this file.
    app.run()
