# Install required libraries (Run this only once)
!pip install dash dash-bootstrap-components plotly pandas

# Import libraries
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output

# Load dataset
df = pd.read_csv("final_hotel_booking.csv")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Theme colors
BACKGROUND_COLOR = "#121212"
PLOT_BACKGROUND_COLOR = "#1E1E1E"
TEXT_COLOR = "white"
TAB_SELECTED_COLOR = "#5A189A"
TAB_UNSELECTED_COLOR = "#888888"
SIDEBAR_BACKGROUND = "#333333"
SIDEBAR_TEXT_COLOR = "#FFFFFF"

# Sidebar filters (Improved with "All" option and better styling)
sidebar = dbc.Card(
    dbc.CardBody([
        html.H4("Filters", className="text-center",
                style={"color": TEXT_COLOR, "marginBottom": "20px", "textAlign": "center",
                       "font-weight": "bold"}),

        html.Label("Hotel Type:", style={"color": TEXT_COLOR, "font-size": "16px", "marginBottom": "5px",
                                         "font-weight": "bold"}),
        dcc.Dropdown(
            id="hotel-dropdown",
            options=[{"label": "All", "value": "All"}] + 
                    [{"label": i, "value": i} for i in df["hotel"].dropna().unique()],
            value="All",
            clearable=False,
            style={"backgroundColor": "#333333", "color": "white", "font-size": "14px",
                   "marginBottom": "15px", "border-radius": "5px", "padding": "5px"},
        ),

        html.Label("Market Segment:", style={"color": TEXT_COLOR, "font-size": "16px", "marginBottom": "5px",
                                             "font-weight": "bold"}),
        dcc.Dropdown(
            id="market-segment-dropdown",
            options=[{"label": "All", "value": "All"}] + 
                    [{"label": i, "value": i} for i in df["market_segment"].dropna().unique()],
            value="All",
            clearable=False,
            style={"backgroundColor": "#333333", "color": "white", "font-size": "14px",
                   "marginBottom": "15px", "border-radius": "5px", "padding": "5px"},
        ),

        html.Label("Arrival Month:", style={"color": TEXT_COLOR, "font-size": "16px", "marginBottom": "5px",
                                            "font-weight": "bold"}),
        dcc.Dropdown(
            id="arrival-month-dropdown",
            options=[{"label": "All", "value": "All"}] + 
                    [{"label": i, "value": i} for i in df["arrival_date_month"].dropna().unique()],
            value="All",
            clearable=False,
            style={"backgroundColor": "#333333", "color": "black", "font-size": "14px",
                   "border-radius": "5px", "padding": "5px"},
        ),
    ]),
    style={
        "width": "270px",  # Wider Sidebar
        "backgroundColor": SIDEBAR_BACKGROUND,
        "padding": "25px",
        "marginRight": "20px",
        "border-radius": "10px",
        "box-shadow": "0px 4px 8px rgba(255, 255, 255, 0.1)"
    },
)


# Tabs
tabs = dbc.Tabs(
    [
        dbc.Tab(label="📅 Booking & Cancellations", tab_id="tab-1", label_style={"color": TEXT_COLOR}),
        dbc.Tab(label="💰 Revenue & Pricing", tab_id="tab-2", label_style={"color": TEXT_COLOR}),
        dbc.Tab(label="🧑‍🤝‍🧑 Customer Segmentation", tab_id="tab-3", label_style={"color": TEXT_COLOR}),
    ],
    id="tabs",
    active_tab="tab-1",
    style={"backgroundColor": PLOT_BACKGROUND_COLOR},
)

# Layout
app.layout = dbc.Container(
    [
        html.H1("🏨 Hotel Data Dashboard", style={"textAlign": "center", "color": TEXT_COLOR}),
        tabs,
        html.Br(),
        dbc.Row(
            [
                dbc.Col(sidebar, width=3),  # Sidebar filters on the left
                dbc.Col(html.Div(id="tab-content"), width=9),
            ],
            style={"backgroundColor": BACKGROUND_COLOR},
        ),
    ],
    fluid=True,
    style={"backgroundColor": BACKGROUND_COLOR, "padding": "20px"},
)

# Callback to update dashboard based on selected tab and filters
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"), 
     Input("hotel-dropdown", "value"),
     Input("market-segment-dropdown", "value"),
     Input("arrival-month-dropdown", "value")],
)
def update_dashboard(selected_tab, selected_hotel, selected_segment, selected_month):
    # Apply filtering logic
    filtered_df = df[
        ((df["hotel"] == selected_hotel) | (selected_hotel == "All")) &
        ((df["market_segment"] == selected_segment) | (selected_segment == "All")) &
        ((df["arrival_date_month"] == selected_month) | (selected_month == "All"))
    ]

    # If no data available, show a message
    if filtered_df.empty:
        return html.H3("🚨 No Data Available for Selected Filters", style={"color": "red", "textAlign": "center"})

    if selected_tab == "tab-1":  # 📅 Booking & Cancellations
        fig1 = px.bar(
            filtered_df.groupby("arrival_date_month").size().reset_index(name="cancellations"),
            x="arrival_date_month",
            y="cancellations",
            title="Cancellations by Month",
        )
        fig1.update_layout(paper_bgcolor=PLOT_BACKGROUND_COLOR, plot_bgcolor=PLOT_BACKGROUND_COLOR, font=dict(color=TEXT_COLOR))

        fig2 = px.pie(
            filtered_df,
            names="market_segment",
            title="Market Segment Distribution",
        )
        fig2.update_layout(paper_bgcolor=PLOT_BACKGROUND_COLOR, plot_bgcolor=PLOT_BACKGROUND_COLOR, font=dict(color=TEXT_COLOR))

        return dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig1), width=6),
                dbc.Col(dcc.Graph(figure=fig2), width=6),
            ]
        )

    elif selected_tab == "tab-2":  # 💰 Revenue & Pricing
        fig1 = px.line(
            filtered_df.groupby("arrival_date_month")["adr"].mean().reset_index(),
            x="arrival_date_month",
            y="adr",
            title="Average Daily Rate (ADR) by Month",
        )
        fig1.update_layout(paper_bgcolor=PLOT_BACKGROUND_COLOR, plot_bgcolor=PLOT_BACKGROUND_COLOR, font=dict(color=TEXT_COLOR))

        return dbc.Row([dbc.Col(dcc.Graph(figure=fig1), width=12)])

    elif selected_tab == "tab-3":  # 🧑‍🤝‍🧑 Customer Segmentation
        fig1 = px.histogram(
            filtered_df,
            x="lead_time",
            title="Lead Time Distribution",
        )
        fig1.update_layout(paper_bgcolor=PLOT_BACKGROUND_COLOR, plot_bgcolor=PLOT_BACKGROUND_COLOR, font=dict(color=TEXT_COLOR))

        fig2 = px.box(
            filtered_df,
            x="market_segment",
            y="adr",
            title="ADR by Market Segment",
        )
        fig2.update_layout(paper_bgcolor=PLOT_BACKGROUND_COLOR, plot_bgcolor=PLOT_BACKGROUND_COLOR, font=dict(color=TEXT_COLOR))

        return dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig1), width=6),
                dbc.Col(dcc.Graph(figure=fig2), width=6),
            ]
        )

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
