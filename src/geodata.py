import os
import json
import glob
import sqlite3
import pandas as pd
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypeAlias, Literal, Optional

import numpy as np
import xarray as xr


GeoJSON: TypeAlias = dict[Literal["type", "center", "features", "limits"]]
GeoJSONlimits: TypeAlias = dict[Literal["north", "south", "west", "east"]]

@dataclass
class ForecastQuery:
    variable: Literal['PM2.5'
                    'PM2.5 Nitrate'
                    'PM2.5 Sulphate'
                    'PM2.5 REC'
                    'PM2.5 TEC'
                    'PM2.5 SIA'
                    'PM2.5 TOM'
                    'PM10'
                    'PM10 Dust'
                    'PM10 Salt'
                    'NH3'
                    'CO'
                    'HCHO'
                    'OCHCHO'
                    'NO2'
                    'VOCs'
                    'O3'
                    'NO + NO2'
                    'SO2'
                    'Alder pollen'
                    'Birch pollen'
                    'Grass pollen'
                    'Mugwort pollen'
                    'Olive pollen'
                    'Ragweed pollen']
    time: datetime
    leadtime: int
    model: Optional[str]
    limits: Optional[GeoJSONlimits]

@dataclass
class AnalysisQuery:
    variable: Literal['PM2.5'
                    'PM2.5 Nitrate'
                    'PM2.5 Sulphate'
                    'PM2.5 REC'
                    'PM2.5 TEC'
                    'PM2.5 SIA'
                    'PM2.5 TOM'
                    'PM10'
                    'PM10 Dust'
                    'PM10 Salt'
                    'NH3'
                    'CO'
                    'HCHO'
                    'OCHCHO'
                    'NO2'
                    'VOCs'
                    'O3'
                    'NO + NO2'
                    'SO2'
                    'Alder pollen'
                    'Birch pollen'
                    'Grass pollen'
                    'Mugwort pollen'
                    'Olive pollen'
                    'Ragweed pollen']
    start_time: datetime
    end_time: datetime



def query_forecast_nc(query:ForecastQuery):
    ds = xr.open_dataset("data/netcdf/cams-europe-air-quality-forecasts/EU-forecast-PM10-2025-05-10-24/ENS_FORECAST.nc", engine="netcdf4", decode_timedelta=False)
    all_values = ds.variables["pm10_conc"][query.leadtime][0].data # lat lon
    all_longitudes = list(map(lambda lon: lon if lon < 180 else lon - 360, ds.variables["longitude"].data.tolist()))
    all_latitudes:list = ds.variables["latitude"].data.tolist()

    values = all_values
    longitude = all_longitudes
    latitude = all_latitudes
    if query.limits:
        # Find longitude index range
        west_limit_idx = min([i for i, lon in enumerate(all_longitudes) if lon > query.limits["west"]])
        east_limit_idx = max([i for i, lon in enumerate(all_longitudes) if lon < query.limits["east"]])

        # Find latitude index range (NOTE: descending order)
        north_limit_idx = min([i for i, lat in enumerate(all_latitudes) if lat < query.limits["north"]])
        south_limit_idx = max([i for i, lat in enumerate(all_latitudes) if lat > query.limits["south"]])

        # Crop the 1D coordinate arrays
        longitude = all_longitudes[west_limit_idx:east_limit_idx + 1]
        latitude = all_latitudes[north_limit_idx:south_limit_idx + 1]

        # Crop the 2D values array using lat (rows) and lon (columns)
        values = all_values[north_limit_idx:south_limit_idx + 1, west_limit_idx:east_limit_idx + 1]

    # Create coordinate matrix
    LON, LAT = np.meshgrid(longitude, latitude)
    matrix_np = np.stack((LON, LAT), axis=-1)
    coordinates = [[[round(lat[0],2), round(lat[1],2)] for lat in lon] for lon in matrix_np.tolist()] 

    values_expanded = values[:, :, np.newaxis] # Make it 3D so we can concatenate it

    # Add values to coordinates
    results = np.concatenate((values_expanded, coordinates), axis=2)

    # Add leadtime to coordinates
    time_array = np.full((len(latitude), len(longitude), 1), query.leadtime)
    results = np.concatenate((results, time_array), axis=2)

    # Reshape results for pd.DataFrame
    flat_result = results.reshape(-1, 4) #2D

    df = pd.DataFrame(flat_result, columns=["value", "lon", "lat", "leadtime"])

    # Create id for plotly
    df['id'] = df.apply(lambda row: f"[{row['lon']}, {row['lat']}]", axis=1)

    # Move id-column to first
    df = df[['id'] + [col for col in df.columns if col != 'id']]
    return df



def query_analysis(query:AnalysisQuery):
    pass


def get_dataframe(query:ForecastQuery|AnalysisQuery):
    if isinstance(query, ForecastQuery):
        hours = query.leadtime +1
        dfs = []
        for _ in range(hours):
            dfs.append(query_forecast_nc(query))
            query.leadtime -= 1
        df = pd.concat(dfs, ignore_index=True)
        df = df.sort_values(by="leadtime", ascending=True)
        return df
    elif isinstance(query, AnalysisQuery):
        return query_analysis(query)
    raise ValueError(f"Query must be instance of either {ForecastQuery.__name__} or {AnalysisQuery.__name__}")


if __name__ == "__main__":
    query = ForecastQuery(
        variable="PM10",
        time=datetime(2025, 5, 10, 0, 0),
        leadtime=4,
        model=None,
        limits={"north": 60, "south": 0, "west": -100, "east": 20}
    )

    df = query_forecast_nc(query)
    #breakpoint()
    print("Miip!")