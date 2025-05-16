import time
from datetime import datetime

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, callback, Input, Output, Patch

from src import geodata
from src.geodata import ForecastQuery, AnalysisQuery, GeoJSON
from src import cropit

dash.register_page(__name__)


CITY_CENTERS = {
    "Paris": {"north": 49, "south": 48.65, "west": 2.15, "east": 2.75}, # 2.35 48.85
}

CITY_NAMES = [
    "Paris"
]



@callback(
    Output("city_satellite", "figure"),
    Input("satellite_input", "value"))
def update_satellite_map_region(region:str):
    print(region)
    start = time.perf_counter()
    geojson = get_geojson(region)
    fig = Patch()
    fig.data[0].geojson = geojson
    end = time.perf_counter()
    print(f"Region change: {end-start:.2f}sec")
    return fig


def map_figure():
    variable = "PM10"
    geojson:GeoJSON = get_geojson("Paris")
    df:pd.DataFrame = geodata.get_dataframe(ForecastQuery(
        variable=variable,
        time=datetime(2025, 5, 10, 0, 0),
        leadtime=23,
        model=None,
        limits=geojson["limits"]
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
        margin={"r":0,"t":25,"l":0,"b":30}, 
        title_text=f"{variable} forecast",
        height=700)
    fig.update_traces(marker_line_width=0)
    return fig


def get_geojson(region) -> GeoJSON:
    geojson_path = f"data/geojson/europe.forecast.geo.json"
    return cropit.crop_geojson(CITY_CENTERS[region], geojson_path)






layout = html.Div([
    html.H4('PM10 Air pollution in cities'),
    dcc.Graph(id="city_satellite", figure=map_figure()),
    dcc.RadioItems(
        id="satellite_input",
        options=CITY_NAMES,
        value="Paris",
        inline=True
    )
])