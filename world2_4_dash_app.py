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

HOW IT WAS BUILT, IN STAGES

Stage 1 drew the book's standard run as the two plots the DYNAMO listing asks
for (its two PLOT cards, the book's Figures 4-1 and 4-2).

Stage 2 (this version) adds sliders for the seven policy switches, the year
they switch, and the year the run ends. A Dash "callback" connects them: when
a slider moves, the callback reruns simulate() with the new policy and
redraws every chart. Set to the book's values, the sliders reproduce its
experiments (see the text at the top of the page).

Run:  python world2_4_dash_app.py
then open http://127.0.0.1:8050 in a browser. Needs dash (pip install dash).
Check it against the book: python validation/tools/check_dash_app.py
"""

import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

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

#   (name in the results,                          chart title,                            divide by, book's scale)
PLOT_1 = [
    ("population",                                 "Population, billions (P)",             1e9, (0, 8)),
    ("pollution_ratio",                            "Pollution ratio (POLR)",               1,   (0, 40)),
    ("capital_investment",                         "Capital investment, billions (CI)",    1e9, (0, 20)),
    ("quality_of_life",                            "Quality of life (QL)",                 1,   (0, 2)),
    ("natural_resources",                          "Natural resources, billions (NR)",     1e9, (0, 1000)),
]
PLOT_2 = [
    ("food_ratio",                                 "Food ratio (FR)",                      1,   (0, 2)),
    ("material_standard_of_living",                "Material standard of living (MSL)",    1,   (0, 2)),
    ("quality_of_life_from_crowding",              "Quality of life from crowding (QLC)",  1,   (0, 2)),
    ("quality_of_life_from_pollution",             "Quality of life from pollution (QLP)", 1,   (0, 2)),
    ("capital_investment_in_agriculture_fraction", "Agricultural capital fraction (CIAF)", 1,   (.2, .6)),
]


# ---------------------------------------------------------------------------
# What the sliders change
#
# The seven policy switches of world2_3_modern.py (DYNAMO's CLIP cards). Each
# has a value before the switch year and a value after it. In the book's
# standard run the two are equal. A slider sets the value after the switch,
# as a percent of the value before it, so 100% everywhere is the standard run.
# ---------------------------------------------------------------------------

#   (name in the policy,                     slider label,                          DYNAMO card)
POLICY_SLIDERS = [
    ("birth_rate_normal",                    "Birth rate normal",                    "BRN1"),
    ("natural_resource_usage_normal",        "Natural-resource usage normal",        "NRUN1"),
    ("death_rate_normal",                    "Death rate normal",                    "DRN1"),
    ("capital_investment_generation_normal", "Capital-investment generation normal", "CIGN1"),
    ("capital_investment_discard_normal",    "Capital-investment discard normal",    "CIDN1"),
    ("pollution_normal",                     "Pollution normal",                     "POLN1"),
    ("food_coefficient",                     "Food coefficient",                     "FC1"),
]


def policy_from_sliders(percents, switch_year):
    """Turn slider settings into a policy for simulate()."""
    policy = {}
    for (name, _, _), percent in zip(POLICY_SLIDERS, percents):
        before = STANDARD_POLICY[name][0]
        policy[name] = (before, before * (percent / 100), switch_year)
    return policy


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


def values_table(run, panels, every_years=10):
    """The same numbers as a table, one row every few years."""
    step = round(every_years / (run["year"][1] - run["year"][0]))
    header = html.Tr([html.Th("Year")] + [html.Th(title) for _, title, _, _ in panels])
    rows = [html.Tr([html.Td(f"{run['year'][i]:.0f}")]
                    + [html.Td(f"{run[name][i] / divide_by:.3g}") for name, _, divide_by, _ in panels])
            for i in range(0, len(run["year"]), step)]
    return html.Table([html.Thead(header), html.Tbody(rows)], className="values")


def slider(slider_id, label, minimum, maximum, step, value, marks):
    """A labeled slider, with a spot beside the label for the value it sets
    (the callback fills it in, as the DYNAMO card it stands for, e.g. NRUN1 = 0.25)."""
    return html.Div(className="control", children=[
        html.Label([label, " ", html.Span(id=f"{slider_id}-readout", className="readout")],
                   htmlFor=slider_id),
        dcc.Slider(id=slider_id, min=minimum, max=maximum, step=step, value=value,
                   marks=marks, allow_direct_input=False),
    ])


# ---------------------------------------------------------------------------
# The page
#
# The charts start empty. When the page loads, Dash runs the callback below
# once with the sliders' starting values, which fills them with the standard run.
# ---------------------------------------------------------------------------

app = Dash(__name__, title="World2")
app.index_string = app.index_string.replace("</head>", f"""<style>
  body {{ margin: 0; background: {PAGE}; color: {SECONDARY}; font-family: {FONT}; }}
  .page {{ max-width: 1500px; margin: 0 auto; padding: 24px 16px 48px; }}
  h1 {{ color: {INK}; font-size: 24px; margin: 0 0 6px; }}
  h2 {{ color: {INK}; font-size: 16px; margin: 28px 0 8px; }}
  p {{ margin: 0 0 6px; max-width: 72em; line-height: 1.45; }}
  .controls {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
               gap: 16px 24px; }}
  .control {{ display: flex; flex-direction: column; }}   /* sliders line up across a row */
  .control label {{ flex: 1; display: flex; flex-wrap: wrap; align-content: flex-start; gap: 0 12px;
                    color: {INK}; font-size: 13px; margin-bottom: 8px; }}
  .readout {{ margin-left: auto; color: {SECONDARY}; font-variant-numeric: tabular-nums; }}
  /* Dash's own accent color, set to gray so the data is the only thing in color */
  :root {{ --Dash-Fill-Interactive-Strong: {SECONDARY}; }}
  .dash-slider-mark {{ color: {SECONDARY}; }}
  .dash-slider-mark-outside-selection {{ color: {MUTED}; }}
  .panels {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 8px; }}
  details {{ margin-top: 28px; overflow-x: auto; }}
  summary {{ cursor: pointer; color: {INK}; font-weight: 600; }}
  .values {{ border-collapse: collapse; margin-top: 12px; font-size: 13px;
             font-variant-numeric: tabular-nums; }}
  .values th, .values td {{ padding: 4px 10px; text-align: right; border-bottom: 1px solid {GRID}; }}
  .values th {{ color: {INK}; font-weight: 600; vertical-align: bottom; max-width: 9em; }}
</style>
</head>""")

PERCENT_MARKS = {0: "0%", 50: "50%", 100: "100%", 150: "150%", 200: "200%"}

app.layout = html.Div(className="page", children=[
    html.H1("World2"),
    html.P("Jay W. Forrester's world model from World Dynamics (1971), computed by "
           "simulate() in world2_3_modern.py. Each slider sets one of the model's seven "
           "policy switches from the switch year on, as a percent of its value in the "
           "book's standard run. At 100% everywhere, this is the standard run."),
    html.P("To reproduce the book's experiments: natural-resource usage at 25% is the "
           "pollution crisis (Figures 4-5 to 4-8). Natural-resource usage at 0% and "
           "pollution at 10%, run to 2300, is the crowding run (Figures 4-9 and 4-10)."),

    html.H2("Policies from the switch year on"),
    html.Div(className="controls", children=[
        slider(name, label, 0, 200, 5, 100, PERCENT_MARKS)
        for name, label, _ in POLICY_SLIDERS
    ] + [
        slider("switch-year", "Switch year", 1900, 2100, 5, 1970,
               {year: str(year) for year in range(1900, 2101, 50)}),
        slider("end-year", "Run to", 2100, 2300, 100, 2100,
               {year: str(year) for year in (2100, 2200, 2300)}),
    ]),

    html.H2("First PLOT card (book Figure 4-1)"),
    html.Div(className="panels", children=[
        dcc.Graph(id=name, config={"displayModeBar": False}) for name, *_ in PLOT_1]),

    html.H2("Second PLOT card (book Figure 4-2)"),
    html.Div(className="panels", children=[
        dcc.Graph(id=name, config={"displayModeBar": False}) for name, *_ in PLOT_2]),

    html.Details([html.Summary("The same values as a table, every 10 years"),
                  html.Div(id="values")]),
])


# ---------------------------------------------------------------------------
# The callback: sliders in, charts out
#
# Dash calls rerun() whenever a slider is released, with every slider's
# current value, and puts what it returns into the outputs, in order.
# ---------------------------------------------------------------------------

@app.callback(
    [Output(name, "figure") for name, *_ in PLOT_1 + PLOT_2]
    + [Output(f"{name}-readout", "children") for name, *_ in POLICY_SLIDERS]
    + [Output("switch-year-readout", "children"), Output("end-year-readout", "children")]
    + [Output("values", "children")],
    [Input(name, "value") for name, *_ in POLICY_SLIDERS]
    + [Input("switch-year", "value"), Input("end-year", "value")],
)
def rerun(*slider_values):
    *percents, switch_year, end_year = slider_values
    policy = policy_from_sliders(percents, switch_year)
    run = simulate(policy, end_year=end_year)

    figures = [panel(run, *plot) for plot in PLOT_1 + PLOT_2]
    readouts = [f"{card} = {policy[name][1]:.4g}" for name, _, card in POLICY_SLIDERS]
    return (figures + readouts + [str(switch_year), str(end_year)]
            + [values_table(run, PLOT_1 + PLOT_2)])


if __name__ == "__main__":
    # app.run(debug=True) adds Dash's developer tools, and reloads the page
    # whenever you save a change to this file.
    app.run()
