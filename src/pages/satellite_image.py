import time
from datetime import datetime

import dash
import plotly
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, Patch, callback

import src.geodata as geodata
from src.geodata import ForecastQuery, AnalysisQuery, GeoJSON


dash.register_page(__name__)


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



@callback(
    Output("graph", "figure"),
    Input("region", "value"),
    prevent_initial_call=True
)
def change_region(region:str):
    print(region)
    start = time.perf_counter()
    geojson = get_geojson(region)
    fig = Patch()
    fig.data[0].geojson = geojson
    end = time.perf_counter()
    print(f"Region change: {end-start:.2f}sec")
    return fig


@callback(
    Output("graph", "figure", allow_duplicate=True),
    Input("color", "value"),
    prevent_initial_call=True
)
def change_color(color:str):
    zones = [(0,"#fcfafa"), (0.19,"#fcfafb"), (0.20,"#c7dff0"), (0.39,"#c7dff1"), (0.4,"#77baed"), (0.59,"#77baee"), (0.6,"#943fa2"), (0.79,"#943fa1"), (0.8,"#4d004a"), (1,"#4d004b")]
    bupu = [(0,"#f7fcfd"), (0.11,"#e0ecf4"), (0.33,"#bfd3e6"), (0.44,"#9ebcda"), (0.55,"#8c96c6"), (0.66,"#8c6bb1"), (0.77,"#88419d"), (0.88,"#810f7c"), (1,"#4d004b")]
    fig = Patch()
    fig.data[0].colorscale = color
    if color == "Gradient":
        fig.data[0].colorscale = bupu
    if color == "Zones":
        fig.data[0].colorscale = zones
    
    return fig



layout = html.Div([
    #html.H4("PM10 particles in air"),
    html.P("Select a region:"),
    dcc.RadioItems(
        id="region",
        options=["North", "West", "East", "South", "Venice"],
        value="Venice",
        inline=True
    ),
    dcc.RadioItems(
        id="color",
        options=["Gradient", "Zones", "Viridis"],
        value="Gradient",
        inline=True
    ),
    dcc.Graph(id="graph", figure=map_figure("PM10", get_geojson("Venice"))),
])

