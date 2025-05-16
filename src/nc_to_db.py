import json
import time
import hashlib
import sqlite3
from pprint import pprint
from typing import TypeAlias
from argparse import ArgumentParser
from datetime import datetime, timedelta

import numpy as np
import xarray as xr

import find_nc_files


def hash_data_entry(entry:dict) -> str:
    """Return a data filename containing a hash which depends on the request"""
    hash = hashlib.md5()
    hash.update(json.dumps(entry, sort_keys=True).encode())
    return hash.hexdigest()


def _get_data_set(path:str) -> xr.Dataset:
    ds = xr.open_dataset(path, engine="netcdf4")
    return ds


def get_points(ds:xr.Dataset) -> list[tuple[float, float]]:
    """Creates new coordinates to make squares around original points."""
    longitudes = ds.variables["longitude"].data.tolist()
    latitudes = ds.variables["latitude"].data.tolist()
    coordinates = np.array(np.meshgrid(longitudes, latitudes)).T.reshape(-1, 2)

    points = []
    for point in coordinates:
        lon, lat = point
        lon = float(lon)
        lat = float(lat)
        points.append((lon, lat))

    return points


GeoJSON: TypeAlias = dict
Measurements: TypeAlias = list[list]
def _get_geodata(ds:xr.Dataset, variable_name:str, db_connection_string:str) -> GeoJSON:
    date:str = ds.FORECAST.split()[1].split("+")[0] # '20250510'
    forecast_datetime = datetime.strptime(date, "%Y%m%d")
    with sqlite3.connect(db_connection_string) as conn:
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        start_time = time.perf_counter()
        idx = 0
        data_points = len(ds.time) * len(ds.level) * len(ds.latitude) * len(ds.longitude)
        for leadtime_idx, ltime in enumerate(ds.time):
            print("leadtime: " + str(leadtime_idx))
            for level_idx, _ in enumerate(ds.level):
                for lat_idx, lat in enumerate(ds.latitude):
                    for lon_idx, lon in enumerate(ds.longitude):
                        idx += 1
                        print(f"{idx}/{data_points} {time.perf_counter()-start_time:.3f}sec", end="\r")

                        variable_name = "PM10"
                        unit_name = "μg/m3"
                        value = float(ds.variables["pm10_conc"][leadtime_idx][level_idx][lat_idx][lon_idx].data)
                        lon = round(float(lon), 2)
                        lat = round(float(lat), 2)
                        forecast_time = forecast_datetime.strftime("%Y/%m/%d %H:%M")
                        leadtime = forecast_datetime + timedelta(microseconds=int(ltime)/1000)
                        leadtime = leadtime.strftime("%Y/%m/%d %H:%M")
                        model = "ENSEMBLE"
                        hash = hash_data_entry({
                            "variable_name":variable_name, 
                            "unit_name":unit_name, 
                            "value":value, 
                            "lon":lon, 
                            "lat":lat, 
                            "time":forecast_time, 
                            "leadtime":leadtime, 
                            "model":model
                        }) # NOTE Makes sure every entry is unique
                        
                        sql = """INSERT INTO forecasts 
                        (variable_name, unit_name, value, lon, lat, datetime, leadtime, model, hash) 
                        VALUES 
                        (:variable_name, :unit_name, :value, :lon, :lat, :time, :leadtime, :model, :hash)"""
                        try:
                            cursor.execute(
                                sql, 
                                {
                                    "variable_name":variable_name, 
                                    "unit_name":unit_name, 
                                    "value":value, 
                                    "lon":lon, 
                                    "lat":lat, 
                                    "time":forecast_time, 
                                    "leadtime":leadtime, 
                                    "model":model, 
                                    "hash": hash
                                }
                            )
                            conn.commit()
                        except sqlite3.IntegrityError as err:
                            if str(err) != 'UNIQUE constraint failed: forecasts.hash':
                                raise # hash estää meitä lisäämästä kahta samanlaista riviä

        print(f"{idx}/{data_points} {time.perf_counter()-start_time:.3f}sec")


def store_to_database(origin:str, db_connection_string:str):
    print("Reading dataset...")
    filepath = find_nc_files.find_nc_file(origin)
    dataset:xr.Dataset = _get_data_set(filepath)

    print("Saving to db...")
    _get_geodata(dataset, "pm10_conc", db_connection_string)

    print("Done.")
    


def main():
    parser = ArgumentParser(
                    prog='Map It',
                    description='Creates geojsons from netCDF'
    )
    parser.add_argument("filepath", help="Filename or path. Can be partial path. File is expected to be in data-folder.")
    args = parser.parse_args()
    filename:str = args.filepath

    target = "AirQuality.db"
    origin = find_nc_files.find_nc_file(filename)
    
    store_to_database(origin, target)



if __name__ == "__main__":
    main()