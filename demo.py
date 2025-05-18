import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

from src import geodata
from src.geodata import ForecastMultiQuery, GeoJSON
from src import crop_geojson
from src.pollution import accumulation, Coordinate

# Region & data config
CITY_REGIONS = {
    "Paris": {"north": 54, "south": 44, "west": -4, "east": 8}
}

TIME_SPAN = 13

def get_geojson(region) -> GeoJSON:
    geojson_path = "data/geojson/europe.forecast.geo.json"
    return crop_geojson.crop_geojson(CITY_REGIONS[region], geojson_path)

def get_data(leadtime: int, geojson: GeoJSON):
    df = geodata.get_dataframe(ForecastMultiQuery(
        variable="PM10",
        time=datetime(2025, 5, 10, 0, 0),
        leadtimes=[leadtime],
        model=None,
        limits=geojson["limits"]
    ))
    return df

# Initialize app and data
app = dash.Dash(__name__)
geojson = get_geojson("Paris")
locations = get_data(0, geojson).iloc[:, 0].tolist()
df = geodata.get_dataframe(ForecastMultiQuery(
    variable="PM10",
    time=datetime(2025, 5, 10, 0, 0),
    leadtimes=[_ for _ in range(TIME_SPAN+1)],
    model=None,
    limits=geojson["limits"]
))
accumulative_exposure = [accumulation(
    df, Coordinate(lon=2.35, lat=48.85), 
    datetime(2025, 5, 10, 0, 0), datetime(2025, 5, 10, 1, 0) + timedelta(hours=i),
    air_intake_cubics_per_minute=1)
    for i in range(0, TIME_SPAN)
]


# Helper to build map figure
def create_map_figure(leadtime):
    df = get_data(leadtime, geojson)
    fig = go.Figure(go.Choroplethmap(
        geojson=geojson,
        featureidkey="id",
        locations=locations,
        z=df["value"],
        colorscale="Bupu",
        marker=dict(opacity=0.4, line_width=0),
        zmin=2,
        zmax=20
    ))
    fig.update_layout(
        map_center=dict(lon=2, lat=49),
        map_zoom=5,
        margin=dict(l=0, r=0, t=20, b=0),
    )
    return fig

# Helper to build scatter plot
def create_chart_figure(leadtime):
    df = get_data(leadtime, geojson)
    fig = go.Figure(go.Scatter(
        x=[i for i in range(14)],
        y=accumulative_exposure[:leadtime],
        mode="lines+markers",
        name="PM10"
    ))
    fig.update_layout(
        yaxis_title="PM10",
        xaxis_title="Location",
        margin=dict(l=40, r=10, t=20, b=40)
    )
    return fig

# App layout
app.layout = html.Div([
    html.H3("Air Quality Forecast: Paris (PM10)"),
    
    html.Div([
        dcc.Graph(id="map", figure=create_map_figure(0))
    ], style={"display": "inline-block", "width": "48%", "verticalAlign": "top"}),

    html.Div([
        dcc.Graph(id="chart", figure=create_chart_figure(0))
    ], style={"display": "inline-block", "width": "48%", "verticalAlign": "top"}),

    html.Div([
        dcc.Slider(
            id="leadtime-slider",
            min=0,
            max=13,
            step=1,
            value=0,
            marks={i: str(i) for i in range(TIME_SPAN)},
            tooltip={"always_visible": True}
        )
    ], style={"padding": "40px 10px 10px 10px"})
])

# Callback to update both plots
@app.callback(
    Output("map", "figure"),
    Output("chart", "figure"),
    Input("leadtime-slider", "value")
)
def update_figures(leadtime):
    return create_map_figure(leadtime), create_chart_figure(leadtime)

# Run app
if __name__ == "__main__":
    app.run(debug=True)
