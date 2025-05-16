import os
import json
import time
import glob
from pathlib import Path
from pprint import pprint
from typing import TypeAlias
from datetime import datetime
from argparse import ArgumentParser

import numpy as np
import pandas as pd
import xarray as xr
import plotly.express as px

import create_geojson
import find_nc_files



def main():
    parser = ArgumentParser(
                    prog='Map It',
                    description='Creates geojsons from netCDF'
    )
    parser.add_argument("target", help="Filename.")
    parser.add_argument("filepath", help="Filename or path. Can be partial path. File is expected to be in data-folder.")
    args = parser.parse_args()
    filename:str = args.filepath
    target:str = args.target
    target = Path("data") / "geojson" / target
    if os.path.exists(target):
        confirmation = input(f"Target path already exists. Overwrite? (yes/no): ").lower()
        if confirmation != "y" and confirmation != "yes":
            print("Aborted.")
            return

    target = target.with_suffix(".json")
    origin = find_nc_files.find_nc_file(filename)
    
    confirmation = input(f"\nWrite geojson\nFrom {str(origin)}\nTo {str(target)}\nyes/no: ").lower()
    if confirmation != "y" and confirmation != "yes":
        print("Aborted.")
        return
    
    create_geojson.from_forecast(origin, target)
    print("Done.")



if __name__ == "__main__":
    main()