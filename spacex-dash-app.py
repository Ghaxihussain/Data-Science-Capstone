# spaceX_dash_black_is_blue.py
# ---------------------------------------------------------------------
# SpaceX Launch Records Dashboard (Black-is-Blue theme)
# - Modern dark UI with glowing-blue accents
# - Dropdown, Pie chart, RangeSlider and Scatter chart included
# - Clean typography (Poppins), subtle card layout, animated gradient title
# - All callbacks preserved (pie responds to site; scatter responds to site + payload)
# ---------------------------------------------------------------------

import pandas as pd
import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output
import plotly.express as px

# -------------------------------
# Load data + compute payload bounds
# -------------------------------
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = int(spacex_df['Payload Mass (kg)'].max())
min_payload = int(spacex_df['Payload Mass (kg)'].min())

# Clamp nice marks for slider (every ~1200 or dynamic)
step = 1200
marks = {i: str(i) for i in range(0, max_payload + step, step)}

# Accent colors
NEON_BLUE = "#ffffff"
DEEP_BG = "#06070a"        # main page background
CARD_BG = "#0b1220"        # card background
CARD_BORDER = "#0f2940"    # subtle border
TEXT_COLOR = "#dbeefd"     # readable off-white
SUBTEXT = "#ffffff"

# -------------------------------
# Dash app
# -------------------------------
external_stylesheets = [
    # No CSS frameworks required; we load Google Fonts via index_string below
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server  # expose for deployment if needed

# We'll insert a small block of CSS & fonts in the page via a <style> element
page_css = f"""
/* Google font loaded in head (see app.index_string below) */
:root {{
  --neon: {NEON_BLUE};
  --bg: {DEEP_BG};
  --card: {CARD_BG};
  --card-border: {CARD_BORDER};
  --text: {TEXT_COLOR};
  --subtext: {SUBTEXT};
}}

html, body, #root {{
  height: 100%;
  margin: 0;
  background: linear-gradient(180deg, #03040a 0%, #071022 100%);
  font-family: "Poppins", "Inter", "Roboto Condensed", sans-serif;
  color: var(--text);
}}

/* Layout */
.container {{
  max-width: 1200px;
  margin: 28px auto;
  padding: 20px;
}}

/* Card style */
.card {{
  background: var(--card);
  border-radius: 12px;
  padding: 18px;
  margin-bottom: 18px;
  box-shadow: 0 6px 18px rgba(2,8,18,0.8), inset 0 1px 0 rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.03);
}}

.controls {{
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}}

/* Dropdown, slider containers */
.control-item {{
  min-width: 220px;
  flex: 1 1 260px;
}}

/* Title gradient + subtle animation */
.gradient-title {{
  font-size: 34px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 10px;
  background: linear-gradient(90deg, #00bfff, #ffffff, #10e8ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: titleShift 6s linear infinite;
  display: inline-block;
  letter-spacing: -0.5px;
}}
@keyframes titleShift {{
  0% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}

/* Subtitle */
.title-sub {{
  text-align: center;
  color: var(--subtext);
  margin-bottom: 20px;
}}

/* Explanatory text under charts */
.chart-desc {{
  font-size: 13px;
  color: var(--subtext);
  margin-top: 8px;
  margin-bottom: 12px;
}}

/* Footer */
.footer {{
  text-align: center;
  color: var(--subtext);
  padding: 12px 0;
  font-size: 13px;
  margin-top: 20px;
}}

/* Neon focus / hover for interactive elements */
:focus, :hover {{
  outline: none;
}}
.dcc-dropdown .Select-control, .dash-dropdown {{
  border-radius: 8px;
  color: white;
}}
.dash-graph .js-plotly-plot .plotly .main-svg {{
  transition: all 0.25s ease;
}}

/* Make slider handles glow */
.rc-slider-handle, .dash-range-slider .rc-slider-handle {{
  box-shadow: 0 0 8px rgba(0,229,255,0.9);
  border: 2px solid rgba(0,229,255,0.9) !important;
}}
/* --- Fix dropdown visibility --- */
.Select-menu-outer, .Select-menu {{
  background-color: #0b1220 !important;  /* dark dropdown background */
  color: #ffffff !important;             /* white text */
  border: 1px solid #0f2940 !important;
  box-shadow: 0 0 12px rgba(0, 200, 255, 0.3);
}}

.Select-option {{
  background-color: #0b1220 !important;
  color: #ffffff !important;
}}

.Select-option:hover,
.Select-option.is-focused,
.Select-option.is-selected {{
  background-color: #102a44 !important; /* glowing blue-ish highlight */
  color: #00e0ff !important;
}}

.Select-control,
.Select-value-label,
.Select--single > .Select-control .Select-value,
.Select-placeholder {{
  background-color: #0b1220 !important;
  color: #ffffff !important;
}}

/* small responsive tweaks */
@media (max-width: 820px) {{
  .controls {{ flex-direction: column; align-items: stretch; }}
}}
"""

# Insert Google Fonts and page meta into index_string for Poppins
app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>SpaceX — Black-is-Blue Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        {{%favicon%}}
        {{%css%}}
        <style>{page_css}</style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""

# -------------------------------
# Layout
# -------------------------------
app.layout = html.Div(className="container", children=[
    # Title block
    html.Div([
        html.Div("SpaceX Launch Records Dashboard", className="gradient-title"),
        html.Div("Black-is-Blue theme — mission outcomes and payload analysis", className="title-sub"),
    ], className="card", style={"textAlign": "center"}),

    # Controls row: dropdown + payload slider inside a card container
    html.Div(className="card", children=[
        html.Div(className="controls", children=[
            html.Div(className="control-item", children=[
                html.Label("Launch Site", style={"fontSize": 13, "color": SUBTEXT, "marginBottom": 6}),
                dcc.Dropdown(
                    id='site-dropdown',
                    placeholder="SELECT SITE",
                    options=[
                        {'label': 'All Sites', 'value': 'ALL'},
                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'}
                    ],
                    value='ALL',
                    searchable=True,
                    style={
                        'backgroundColor': '#0d1117',   # dropdown background
                        'color': 'black',               # text color
                        'border': '1px solid #00bfff',
                        'borderRadius': '8px',
                        'padding': '5px'
                    }
                )


            ]),
            html.Div(className="control-item", children=[
                html.Label("Payload range (Kg)", style={"fontSize": 13, "color": SUBTEXT, "marginBottom": 6}),
                dcc.RangeSlider(
                    id='slider-payload',
                    min=0,
                    max=max(10000, max_payload),
                    step=100,
                    marks=marks,
                    value=[min_payload, max_payload],
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ]),
        ]),
        html.Div(style={"marginTop": 10, "color": SUBTEXT},
                 children="Tip: use the dropdown to focus on a site, and the slider to zoom into payload ranges.")
    ], style = {"color": "white"}),

    # Pie chart card
    html.Div(className="card", children=[
        html.Div(dcc.Graph(id='success-pie-chart', config={"displayModeBar": False}), className="dash-graph"),
        html.Div("This pie chart shows the distribution of successful launches across sites or success vs failure for a selected site.", className="chart-desc")
    ]),

    # Scatter card
    html.Div(className="card", children=[
        html.Div(dcc.Graph(id='success-payload-scatter-chart', config={"displayModeBar": False}), className="dash-graph"),
        html.Div("Scatter plot showing relationship between payload mass and mission outcome (1 = success). Color = Booster Version Category.", className="chart-desc")
    ]),

    # Footer
    html.Div(className="footer", children=[
        html.Div(f"Dashboard by Your Name — Powered by Dash & Plotly"),
        html.Div("Theme: Black-is-Blue • Interactive controls: dropdown, range slider, hover-tooltips")
    ])
])

# -------------------------------
# Helper: common plot styling for Plotly figures
# -------------------------------
def apply_dark_style(fig, title_text=None):
    """Apply cohesive dark theme and neon blue accents to Plotly figure."""
    # Use plotly_dark as base then override colors
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=DEEP_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_COLOR, family="Poppins, sans-serif"),
        title=dict(text=title_text or fig.layout.title.text if fig.layout.title else None,
                   x=0.02, xanchor='left', y=0.98, yanchor='top', font=dict(size=16)),
        margin=dict(l=40, r=24, t=60, b=40),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(255,255,255,0.04)'),
        hoverlabel=dict(bgcolor="rgba(2,8,20,0.95)", font_size=12, font_family="Poppins")
    )
    # Plot area grid subtle
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.03)', zerolinecolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.03)', zerolinecolor='rgba(255,255,255,0.05)')

    # Try to tint traces with neon if discrete colors are present
    return fig

# -------------------------------
# Callbacks
# -------------------------------
# PIE CHART callback: updates when a site is selected
@callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value")
)
def update_pie(entered_site):
    """
    If 'ALL' selected -> show successes per launch site.
    If specific site selected -> show success vs failure counts for that site.
    """
    if entered_site == 'ALL':
        # Count successful launches (class==1) grouped by Launch Site
        df = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='success_count')
        fig = px.pie(df, values='success_count', names='Launch Site',
                     title='Successful Launches by Site',
                     color_discrete_sequence=px.colors.sequential.Blues)
        fig.update_traces(textposition='inside', textinfo='percent+label', hole=0.35)
        fig = apply_dark_style(fig, title_text="Successful Launches by Site (All Sites)")
    else:
        # For a single site show success vs failure counts
        df = spacex_df[spacex_df['Launch Site'] == entered_site].groupby('class').size().reset_index(name='count')
        # Map class 1/0 to labels
        df['outcome'] = df['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(df, values='count', names='outcome',
                     title=f'Success vs Failure — {entered_site}',
                     color_discrete_sequence=["#00E5FF", "#16324a"])
        fig.update_traces(textposition='inside', textinfo='percent+label', hole=0.4)
        fig = apply_dark_style(fig, title_text=f"Success vs Failure — {entered_site}")

    # Slightly enlarge hover labels and add neon slice border
    fig.update_traces(marker=dict(line=dict(color='rgba(0,0,0,0.4)', width=1)))
    return fig

# SCATTER callback: updates when site or payload range change
@callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id="site-dropdown", component_property="value"),
    Input(component_id="slider-payload", component_property="value")
)
def update_scatter(entered_site, selected_payload):
    """
    Scatter: payload vs class (mission outcome)
    Filters by selected site (if not 'ALL') and payload range.
    Color-coded by Booster Version Category.
    """
    low, high = selected_payload
    # Filter by payload range first
    dff = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                    (spacex_df['Payload Mass (kg)'] <= high)]

    # If a specific site is selected, filter by it
    if entered_site != 'ALL':
        dff = dff[dff['Launch Site'] == entered_site]

    # Build scatter
    fig = px.scatter(
        dff,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title="Payload vs Mission Outcome by Booster Version",

        symbol="class",
        height=520
    )

    # Tweak appearance: use blue-ish color palette when possible
    # If many categories exist, let Plotly choose, otherwise force blue palette
    try:
        fig.update_traces(marker=dict(size=10, line=dict(width=0.6, color='rgba(0,0,0,0.4)')))
    except Exception:
        pass

    # Y-axis: treat class as categorical-like but keep numeric ticks 0/1
    fig.update_yaxes(dtick=1, tickmode='linear', tick0=0, title_text="Mission Outcome (0 = Failure, 1 = Success)")

    fig = apply_dark_style(fig, title_text=("Payload vs Mission Outcome" + (f" — {entered_site}" if entered_site != 'ALL' else "")))

    # Add subtle horizontal lines for success / failure separation
    fig.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.06)")

    return fig

# -------------------------------
# Run server
# -------------------------------
if __name__ == '__main__':
    # Debug True includes hot reload and helpful tracebacks during dev
    app.run(debug=True, port=8050)
