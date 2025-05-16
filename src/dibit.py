import glob
from pathlib import Path
from pprint import pprint
from argparse import ArgumentParser

import nc_to_db
import find_nc_files



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
    
    nc_to_db.store_to_database(origin, target)



if __name__ == "__main__":
    main()