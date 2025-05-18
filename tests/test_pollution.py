import pytest
import pandas as pd
from datetime import datetime

from src.pollution import accumulation, Coordinate


data = pd.DataFrame([[1, 20.25, 60.25, 0], [1, 20.25, 60.25, 1], [1, 20.25, 60.25, 2], [1, 20.25, 60.25, 3]], columns=["value", "lon", "lat", "leadtime"])
location = Coordinate(20.24, 60.26)


def test_allowed_arguments():
    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 1, 0)

    # Test we get any result with allowed inputs
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_litres_per_minute=1000)
    assert result
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result
    
    with pytest.raises(ValueError) as e_info:
        accumulation(data, location, exposure_start, exposure_end, air_intake_litres_per_minute=1000, air_intake_cubics_per_minute=1)

    exposure_end = datetime(2025, 5, 10, 0, 0)
    exposure_start = datetime(2025, 5, 10, 1, 0)
    with pytest.raises(ValueError) as e_info:
        accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
  

def test_results_are_same_for_cubic_and_litre():
    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 1, 0)
    litre_result = accumulation(data, location, exposure_start, exposure_end, air_intake_litres_per_minute=1000)
    cubic_result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert litre_result == cubic_result

    litre_result = accumulation(data, location, exposure_start, exposure_end, air_intake_litres_per_minute=2000)
    cubic_result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=2)
    assert litre_result == cubic_result


def test_linear_accumulation_intake():
    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 1, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=0)
    assert result == 0

    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 60

    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=2)
    assert result == 120

    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=3)
    assert result == 180


def test_linear_accumulation_time():
    exposure_start = datetime(2025, 5, 10, 0, 0)

    exposure_end = datetime(2025, 5, 10, 0, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 0

    exposure_end = datetime(2025, 5, 10, 1, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 60


def test_time():
    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 0, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 0

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 0, 30)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 30

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 1, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 60

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 1, 30)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 90

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 2, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 120

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 2, 30)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 150

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 3, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 180


def test_irregular_times():
    exposure_start = datetime(2025, 5, 10, 0, 7)
    exposure_end = datetime(2025, 5, 10, 0, 8)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 1

    exposure_start = datetime(2025, 5, 10, 0, 59)
    exposure_end = datetime(2025, 5, 10, 1, 1)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 2

    exposure_start = datetime(2025, 5, 10, 0, 30)
    exposure_end = datetime(2025, 5, 10, 0, 30)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 0

    exposure_start = datetime(2025, 5, 10, 1, 1)
    exposure_end = datetime(2025, 5, 10, 2, 1)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 60

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 2, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 120

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 2, 30)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 150

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 3, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 180


def test_location():
    data = pd.DataFrame([[1, 0.0, 1.0, 0], [2, 1.0, 1.0, 0], 
                         [3, 0.0, 0.0, 0], [4, 1.0, 0.0, 0],
                         [1, 0.0, 1.0, 1], [2, 1.0, 1.0, 1], 
                         [3, 0.0, 0.0, 1], [4, 1.0, 0.0, 1]], 
                         columns=["value", "lon", "lat", "leadtime"]
    )
    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 1, 0)
    location1 = Coordinate(0.0, 1.0)
    location2 = Coordinate(1.0, 1.0)
    location3 = Coordinate(0.0, 0.0)
    location4 = Coordinate(1.0, 0.0)

    result = accumulation(data, location1, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 60

    result = accumulation(data, location2, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 120

    result = accumulation(data, location3, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 180

    result = accumulation(data, location4, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 240


def test_dataset_time_span():
    data = pd.DataFrame(
        [[1, 0.0, 0.0, 1], [1, 0.0, 0.0, 2], [1, 0.0, 0.0, 3]], 
        columns=["value", "lon", "lat", "leadtime"]
    )
    location = Coordinate(0.0, 0.0)

    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 0, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 0
    
    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 1, 0)
    with pytest.raises(ValueError) as e_info:
        accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    
    exposure_start = datetime(2025, 5, 10, 3, 0)
    exposure_end = datetime(2025, 5, 10, 3, 59)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 59
    
    exposure_start = datetime(2025, 5, 10, 3, 0)
    exposure_end = datetime(2025, 5, 10, 4, 0)
    with pytest.raises(ValueError) as e_info:
        accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
   

def test_order():
    data = pd.DataFrame(
        [[0, 0.0, 0.0, 0], [1, 0.0, 0.0, 1], [0, 0.0, 0.0, 2]], 
        columns=["value", "lon", "lat", "leadtime"]
    )
    location = Coordinate(0.0, 0.0)
    
    exposure_start = datetime(2025, 5, 10, 0, 0)
    exposure_end = datetime(2025, 5, 10, 1, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 0
    
    exposure_start = datetime(2025, 5, 10, 1, 0)
    exposure_end = datetime(2025, 5, 10, 2, 0)
    result = accumulation(data, location, exposure_start, exposure_end, air_intake_cubics_per_minute=1)
    assert result == 60