Get-Content .\air_quality.schema | sqlite3 .\AirQuality.db
py .\initdb.py