import time
from pprint import pprint
from datetime import datetime
from typing import TypeAlias, Literal

import pandas as pd
import plotly.express as px

import src.geodata as geodata
from src.geodata import ForecastQuery, AnalysisQuery, GeoJSON



def get_figure(df, geojson, locations, color, variable):
    color_max = min(df.iloc[:,1].max(), 40)
    fig = px.choropleth_map(df, geojson=geojson, locations=locations, color=color,
                            color_continuous_scale="Viridis",
                            range_color=(2, color_max), # NOTE Partikkeleiden raja-arvot väritystä varten
                            map_style="carto-positron",
                            zoom=3, center = {"lon":10, "lat":55},
                            opacity=0.3,
                            labels={'value':'µg/m3'},
                            title=variable,
                            width=900,
                            height=700
                            #animation_frame="leadtime"
                            )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(marker_line_width=0)
    return fig


def main():
    print("Getting geojson...")
    start = time.perf_counter()
    #geojson_path = "data/geojson/west-eu.forecast.geo.json"
    geojson_path = "data/geojson/europe.forecast.geo.json"
    geojson:GeoJSON = geodata.get_geojson(geojson_path)
    end = time.perf_counter()
    print(f"{end-start:.2f}sec")

    print("Getting data...")
    variable="PM10"
    start = time.perf_counter()
    df:pd.DataFrame = geodata.get_dataframe(ForecastQuery(
        variable=variable,
        time=datetime(2025, 5, 10, 0, 0),
        leadtime=0,
        model=None,
        limits=None
    ))
    end = time.perf_counter()
    print(f"{end-start:.2f}sec")

    print("Getting figure...")
    start = time.perf_counter()
    locations = df.iloc[:, 0].tolist() # All ids aka every row of first column
    color='value'
    fig = get_figure(df, geojson, locations, color, variable)
    end = time.perf_counter()
    print(f"{end-start:.2f}sec")

    print("Showing map...")
    start = time.perf_counter()
    fig.show()
    end = time.perf_counter()
    print(f"{end-start:.2f}sec")



if __name__ == "__main__":
    main()