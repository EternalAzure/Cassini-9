import time
import pandas as pd
from datetime import datetime

import plotly
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, Patch

import src.geodata as geodata
from src.geodata import ForecastQuery, AnalysisQuery, GeoJSON


app = Dash(__name__)


def get_geojson(region) -> GeoJSON:
    match region:
        case "Europe":
            geojson_path = f"data/geojson/europe.forecast.geo.json"
        case "North":
            geojson_path = f"data/geojson/north-eu.forecast.geo.json"
        case "West":
            geojson_path = f"data/geojson/west-eu.forecast.geo.json"
        case "East":
            geojson_path = f"data/geojson/east-eu.forecast.geo.json"
        case "South":
            geojson_path = f"data/geojson/south-eu.forecast.geo.json"
        case "Venice":
            geojson_path = f"data/geojson/venize.forecast.geo.json"
        case _:
            geojson_path = f"data/geojson/venice.forecast.geo.json"
    return geodata.get_geojson(geojson_path)


def map_figure(variable, geojson:GeoJSON):
    df:pd.DataFrame = geodata.get_dataframe(ForecastQuery(
        variable=variable,
        time=datetime(2025, 5, 10, 0, 0),
        leadtime=0,
        model=None,
        limits=None
    ))
    locations = df.iloc[:, 0].tolist() # All ids aka every row of first column
    color_max = min(df.iloc[:,1].max(), 30)
    fig = go.Figure(go.Choroplethmap(
        colorscale="Bupu",
        featureidkey="id",
        geojson=geojson,
        locations=locations,
        marker=go.choroplethmap.Marker(opacity=0.3),
        z=df["value"],
        zmin=2,
        zmax=color_max
    ))
    fig.update_layout(
        map_zoom=4,
        map_style="carto-positron",
        map_center=geojson["center"],
        margin={"r":0,"t":25,"l":0,"b":0}, 
        title_text=f"{variable} forecast",
        height=700)
    fig.update_traces(marker_line_width=0)
    return fig




app.layout = html.Div([
    html.H4("PM10 particles in air"),
    dcc.RadioItems(
        id="color",
        options=["Gradient", "Zones", "Viridis"],
        value="Gradient",
        inline=True
    ),
    dcc.Graph(id="graph", figure=map_figure("PM10", get_geojson("Venice"))),
])

app.run(debug=True)