import os
import sys
import yaml
import json
import cdsapi
import hashlib
import pathlib
from zipfile import ZipFile 

import country_codes



def main(dataset:str, request:dict, cdsapirc_file=None):
    data_file = unique_data_filename(request)
    if dataset == "cams-europe-air-quality-forecasts-optimised-at-observation-sites":
        data_file = descriptive_filename_1(request)
    if dataset == "cams-europe-air-quality-forecasts":
        data_file = descriptive_filename_2(request)

    path = pathlib.Path("data") / "netcdf" / dataset
    if not os.path.exists(path): os.mkdir(path)

    path = path / data_file
    if not os.path.exists(path): get_data(dataset, request, path, cdsapirc_file)

    unzip(path)
    os.remove(path)
    print(f"Tiedosto {data_file} on ladattu.")
    

def descriptive_filename_1(request):
    if (len(request["day"]) > 1 or 
        len(request["month"]) > 1 or 
        len(request["year"]) > 1 or
        len(request["leadtime_hour"]) > 1 or
        len(request["country"]) > 1 or
        len(request["variable"]) > 1):
        raise ValueError("Too complex request. Try using unique_data_filename().")

    country = country_codes.country_code(request["country"][0])
    variable = request["variable"][0]
    if variable == "particulate_matter_10um":
        variable = "PM10"
    if variable == "particulate_matter_2.5um":
        variable = "PM2.5"
    year = request["year"][0]
    month = request["month"][0]
    day = request["day"][0]
    time = request["leadtime_hour"][0]
    filename = f"{country}-{variable}-{year}-{month}-{day}-{time}.zip"
    return filename
    

def descriptive_filename_2(request):
    if (len(request["date"]) > 1 or 
        len(request["model"]) > 1 or 
        len(request["level"]) > 1 or
        len(request["type"]) > 1 or
        len(request["time"]) > 1 or
        len(request["variable"]) > 1):
        raise ValueError("Too complex request. Try using unique_data_filename().")

    region = "FI" if "area" in request.keys() else "EU" 
    variable = request["variable"][0]
    datatype = request["type"][0]
    if variable == "particulate_matter_10um":
        variable = "PM10"
    if variable == "particulate_matter_2.5um":
        variable = "PM2.5"
    date = request["date"][0].split("/")[-1]
    time = request["leadtime_hour"][-1]
    filename = f"{region}-{datatype}-{variable}-{date}-{time}.zip"
    return filename


def unique_data_filename(request):
    """Return a data filename containing a hash which depends on the request"""
    hash = hashlib.md5()
    hash.update(json.dumps(request, sort_keys=True).encode())
    return 'data_' + hash.hexdigest() + '.zip'


def get_data(dataset, request, data_file, cdsapirc_file):
    """Download requested data from the ADS"""
  
    # Read the login credentials if provided
    if cdsapirc_file:
        with open(cdsapirc_file, 'r') as f:
            credentials = yaml.safe_load(f)
        kwargs = {'url': credentials['url'],
                  'key': credentials['key'],
                  'verify': credentials['url'].startswith('https://ads.')}
    else:
        kwargs = {}
  
    client = cdsapi.Client(**kwargs)
    client.retrieve(
        dataset,
        request,
        data_file)
    

def unzip(path:pathlib.Path):
    with ZipFile(path) as zObject:
        zObject.extractall(path=path.with_suffix("")) 


if __name__ == "__main__":
    #https://ads.atmosphere.copernicus.eu/datasets
    dataset = "cams-europe-air-quality-forecasts"
    request = {
        "variable": ["particulate_matter_10um"],
        "model": ["ensemble"],
        "level": ["0"],
        "date": ["2025-05-10/2025-05-10"],
        "type": ["forecast"],
        "time": ["00:00"],
        "leadtime_hour": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", 
                          "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"],
        "data_format": "netcdf_zip"
    }
    # The ADS credentials can be passed as an argument if they're not stored in
    # the default location
    cdsapirc_file = sys.argv[1] if len(sys.argv) > 1 else None
    main(dataset, request, cdsapirc_file=cdsapirc_file)