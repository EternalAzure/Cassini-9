import time
from datetime import datetime

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, callback, Input, Output, Patch

from src import geodata
from src.geodata import ForecastQuery, AnalysisQuery, GeoJSON
from src import crop_geojson

dash.register_page(__name__)


CITY_CENTERS = {
    "Paris": {"north": 49, "south": 48.65, "west": 2.15, "east": 2.75}, # 2.35 48.85
    "London": {"north": 51.7, "south": 51.3, "west": -0.26, "east": 0.1}, # -0.12 51.50
    "Madrid": {"north": 40.6, "south": 40.24, "west": -3.86, "east": -3.54}, # -3.70 40.40
    "Barcelona": {"north": 41.56, "south": 41.25, "west": 1.99, "east": 2.31}, # 2.15 41.40
    "Rome": {"north": 42.04, "south": 41.74, "west": 12.34, "east": 12.66}, # 12.50 41.90
    "Berlin": {"north": 52.64, "south": 52.35, "west": 13.24, "east": 13.56}, # 13.40 52.50
    "Milan": {"north": 45.60, "south": 45.2, "west": 9.05, "east": 9.35}, # 9.20 45.45
    "Athens": {"north": 38.15, "south": 37.85, "west": 23.55, "east": 23.85}, # 23.70 38.0
    "Lisbon": {"north": 38.9, "south": 38.6, "west": -9.31, "east": -8.94}, # 9.14 38.72
    "Manchester": {"north": 53.65, "south": 53.35, "west": -2.4, "east": -2.09}, # 2.25 53.50
    "Birmingham": {"north": 52.56, "south": 52.44, "west": -2.06, "east": -1.74}, # 1.89 52.48
    "Naples": {"north": 41.06, "south": 40.7, "west": 14.14, "east": 14.46}, # 14.30 40.85
    "Brussels": {"north": 50.95, "south": 50.75, "west": 4.24, "east": 4.51}, # 4.35 50.85
    "Minsk": {"north": 54.05, "south": 53.75, "west": 27.39, "east": 27.71}, # 27.55 53.90
    "Vienna": {"north": 48.35, "south": 48.05, "west": 16.25, "east": 16.56}, # 16.37 48.20
    "Warsaw": {"north": 52.35, "south": 52.05, "west": 20.85, "east": 21.15}, # 21.00 52.23
    "Hamburg": {"north": 53.70, "south": 53.4, "west": 9.85, "east": 10.15}, # 10.0 53.55
    "Budapest": {"north": 47.65, "south": 47.35, "west": 18.9, "east": 19.20}, # 19.05 47.50
    "Bucharest": {"north": 44.55, "south": 44.25, "west": 25.85, "east": 26.26}, # 26.10 44.40
    "Lyon": {"north": 45.85, "south": 45.65, "west": 4.70, "east": 5.0}, # 4.80 45.75
    "Stockholm": {"north": 59.45, "south": 59.2, "west": 17.9, "east": 18.20}, # 18.05 59.35
    "Glasgow": {"north": 55.95, "south": 55.75, "west": -4.4, "east": -4.1}, # 4.25 55.85
    "Marseille": {"north": 43.45, "south": 43.2, "west": 5.2, "east": 5.56}, # 5.37 43.30
    "Munich": {"north": 48.3, "south": 47.95, "west": 11.44, "east": 11.8}, # 11.60 48.15
    "Zurich": {"north": 47.5, "south": 47.25, "west": 8.4, "east": 8.65}, # 8.55 47.35
    "Copenhagen": {"north": 55.85, "south": 55.55, "west": 12.4, "east": 12.7}, # 12.55 55.65
    "Helsinki": {"north": 60.35, "south": 60.15, "west": 24.65, "east": 25.25},
    "Porto": {"north": 41.3, "south": 41, "west": -8.75, "east": -8.45}, # 8.60 41.15
    "Prague": {"north": 50.2, "south": 49.95, "west": 14.3, "east": 14.6}, # 14.43 50.07
    "Venice": {"north": 45.6, "south": 45.35, "west": 12.15, "east": 12.5}
}

CITY_REGIONS = {
    "Paris": {"north": 54, "south": 44, "west": -4, "east": 8}, # 2.35 48.85
    "London": {"north": 60, "south": 47, "west": -7, "east": 7}, # -0.12 51.50
    "Madrid": {"north": 40.6, "south": 40.24, "west": -3.86, "east": -3.54}, # -3.70 40.40
    "Barcelona": {"north": 41.56, "south": 41.25, "west": 1.99, "east": 2.31}, # 2.15 41.40
    "Rome": {"north": 42.04, "south": 41.74, "west": 12.34, "east": 12.66}, # 12.50 41.90
    "Berlin": {"north": 52.64, "south": 52.35, "west": 13.24, "east": 13.56}, # 13.40 52.50
    "Milan": {"north": 45.60, "south": 45.2, "west": 9.05, "east": 9.35}, # 9.20 45.45
    "Athens": {"north": 38.15, "south": 37.85, "west": 23.55, "east": 23.85}, # 23.70 38.0
    "Lisbon": {"north": 38.9, "south": 38.6, "west": -9.31, "east": -8.94}, # 9.14 38.72
    "Manchester": {"north": 53.65, "south": 53.35, "west": -2.4, "east": -2.09}, # 2.25 53.50
    "Birmingham": {"north": 52.56, "south": 52.44, "west": -2.06, "east": -1.74}, # 1.89 52.48
    "Naples": {"north": 41.06, "south": 40.7, "west": 14.14, "east": 14.46}, # 14.30 40.85
    "Brussels": {"north": 50.95, "south": 50.75, "west": 4.24, "east": 4.51}, # 4.35 50.85
    "Minsk": {"north": 54.05, "south": 53.75, "west": 27.39, "east": 27.71}, # 27.55 53.90
    "Vienna": {"north": 48.35, "south": 48.05, "west": 16.25, "east": 16.56}, # 16.37 48.20
    "Warsaw": {"north": 52.35, "south": 52.05, "west": 20.85, "east": 21.15}, # 21.00 52.23
    "Hamburg": {"north": 53.70, "south": 53.4, "west": 9.85, "east": 10.15}, # 10.0 53.55
    "Budapest": {"north": 47.65, "south": 47.35, "west": 18.9, "east": 19.20}, # 19.05 47.50
    "Bucharest": {"north": 44.55, "south": 44.25, "west": 25.85, "east": 26.26}, # 26.10 44.40
    "Lyon": {"north": 45.85, "south": 45.65, "west": 4.70, "east": 5.0}, # 4.80 45.75
    "Stockholm": {"north": 59.45, "south": 59.2, "west": 17.9, "east": 18.20}, # 18.05 59.35
    "Glasgow": {"north": 55.95, "south": 55.75, "west": -4.4, "east": -4.1}, # 4.25 55.85
    "Marseille": {"north": 43.45, "south": 43.2, "west": 5.2, "east": 5.56}, # 5.37 43.30
    "Munich": {"north": 48.3, "south": 47.95, "west": 11.44, "east": 11.8}, # 11.60 48.15
    "Zurich": {"north": 47.5, "south": 47.25, "west": 8.4, "east": 8.65}, # 8.55 47.35
    "Copenhagen": {"north": 55.85, "south": 55.55, "west": 12.4, "east": 12.7}, # 12.55 55.65
    "Helsinki": {"north": 60.35, "south": 60.15, "west": 24.65, "east": 25.25},
    "Porto": {"north": 41.3, "south": 41, "west": -8.75, "east": -8.45}, # 8.60 41.15
    "Prague": {"north": 50.2, "south": 49.95, "west": 14.3, "east": 14.6}, # 14.43 50.07
    "Venice": {"north": 45.6, "south": 45.35, "west": 12.15, "east": 12.5},
    "Europe": {"north": 180, "south": 0, "west": -180, "east": 180},
}

CITY_NAMES = [
    "Europe",
    "Paris",
    "London",
    "Madrid",
    "Barcelona",
    "Rome",
    "Berlin",
    "Milan",
    "Athens",
    "Lisbon",
    "Manchester",
    "Birmingham",
    "Naples",
    "Brussels",
    "Minsk",
    "Vienna",
    "Warsaw",
    "Hamburg",
    "Budapest",
    "Bucharest",
    "Lyon",
    "Stockholm",
    "Glasgow",
    "Marseille",
    "Munich",
    "Zurich",
    "Copenhagen",
    "Helsinki",
    "Porto",
    "Prague",
    "Venice"
]

@callback(
    Output("city_line_chart", "figure"),
    Input("checklist", "value"))
def update_line_chart_cities(cities:list[str]):
    if not cities: return None
    
    results:list[pd.DataFrame] = []
    for city in cities:
        df = geodata.get_dataframe(geodata.ForecastQuery(
            "PM10",
            time=datetime(2025, 5, 10, 0, 0),
            leadtimes=23,
            model=None,
            limits=CITY_CENTERS[city]
        ))
        sf = df.groupby("leadtime")["value"].mean()
        city_df = pd.DataFrame({'leadtime':sf.index, 'value':sf.values})
        city_df["city"] = [city for i in range(len(city_df))]
        results.append(city_df)

    df = pd.concat(results)
    fig = px.line(df,
    x="leadtime", y="value", color="city")
    return fig


@callback(
    Output("city_satellite", "figure"),
    Input("satellite_input", "value"),
    prevent_initial_call=True)
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
    geojson:GeoJSON = get_geojson("Europe") # Jos koko eurooppaa ei laita alussa, kaikkia maita ei näy
    df:pd.DataFrame = geodata.get_dataframe(ForecastQuery(
        variable=variable,
        time=datetime(2025, 5, 10, 0, 0),
        leadtimes=0,
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
        #map_center={"lon":20, "lat":50},
        map_style="carto-positron",
        margin={"r":0,"t":25,"l":0,"b":30}, 
        title_text=f"{variable} forecast",
        height=700
    )
    fig.update_geos(
        center=dict(lon=10, lat=50),
        lataxis_range=[-30,72], lonaxis_range=[-25, 45],
        #projection_rotation=dict(lon=30, lat=30, roll=30),
    )
    fig.update_traces(marker_line_width=0)
    return fig


def get_geojson(region) -> GeoJSON:
    geojson_path = f"data/geojson/europe.forecast.geo.json"
    return crop_geojson.crop_geojson(CITY_REGIONS[region], geojson_path)



layout = html.Div([
    html.H4('PM10 Air pollution in cities'),
    dcc.Graph(id="city_line_chart"),
    dcc.Checklist(
        id="checklist",
        options=CITY_NAMES,
        value=["Paris"],
        inline=True
    ),
    dcc.Graph(id="city_satellite", figure=map_figure()),
    dcc.RadioItems(
        id="satellite_input",
        options=CITY_NAMES,
        value="Paris",
        inline=True
    ),
    html.P("")
])