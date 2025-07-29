import pytest
import numpy as np

import synthatdelays as satd
from synthatdelays.Classes import (
    Options_Class,
    Flight_Class,
    Aircraft_Class,
    Airport_Class,
    Results_Class,
)


def test_Options_empty():
    Options = satd.Options_Class()

    with pytest.raises(ValueError):
        Options._check()


def test_Options_numAircraft():
    # Test with invalid numAircraft type
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.numAircraft = "not an integer"
    with pytest.raises(ValueError, match="The number of aircraft is not an integer"):
        Options._check()

    # Test with non-positive numAircraft
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.numAircraft = 0
    with pytest.raises(ValueError, match="The number of aircraft must be positive"):
        Options._check()

    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.numAircraft = -1
    with pytest.raises(ValueError, match="The number of aircraft must be positive"):
        Options._check()


def test_Options_routes():
    # Test with invalid routes type
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.routes = "not a list"
    with pytest.raises(ValueError, match="Routes are not a list"):
        Options._check()

    # Test with mismatched routes length
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.routes = [[0, 1], [1, 2]]  # Only 2 routes for 8 aircraft
    with pytest.raises(
        ValueError,
        match="The number of aircraft .* must be equal to the number of routes",
    ):
        Options._check()


def test_Options_numAirports():
    # Test with invalid numAirports type
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.numAirports = "not an integer"
    with pytest.raises(ValueError, match="The number of airports is not an integer"):
        Options._check()

    # Test with non-positive numAirports
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.numAirports = 0
    with pytest.raises(ValueError, match="The number of airports must be positive"):
        Options._check()

    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.numAirports = -1
    with pytest.raises(ValueError, match="The number of airports must be positive"):
        Options._check()


def test_Options_timeBetweenAirports():
    # Test with invalid timeBetweenAirports type
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.timeBetweenAirports = "not an array"
    with pytest.raises(
        ValueError, match="The time between airports is not a Numpy array"
    ):
        Options._check()

    # Test with wrong dimensions
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.timeBetweenAirports = np.random.uniform(1.0, 2.0, (4,))  # 1D array
    with pytest.raises(
        ValueError, match="The time between airports is not a 2-d Numpy array"
    ):
        Options._check()

    # Test with wrong size
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.timeBetweenAirports = np.random.uniform(1.0, 2.0, (3, 3))  # Wrong size
    with pytest.raises(
        ValueError, match="The time between airports has a wrong number of elements"
    ):
        Options._check()

    # Test with negative values
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.timeBetweenAirports = np.random.uniform(
        -2.0, -1.0, (4, 4)
    )  # Negative values
    with pytest.raises(
        ValueError, match="The time between airports cannot be negative"
    ):
        Options._check()


def test_Options_airportCapacity():
    # Test with invalid airportCapacity type
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.airportCapacity = "not an array"
    with pytest.raises(ValueError, match="The airport capacity is not a Numpy array"):
        Options._check()

    # Test with wrong dimensions
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.airportCapacity = np.random.uniform(1.0, 2.0, (4, 4))  # 2D array
    with pytest.raises(
        ValueError, match="The airport capacity is not a 1-d Numpy array"
    ):
        Options._check()

    # Test with wrong size
    Options = satd.Scenario_RandomConnectivity(4, 8, 0.5)
    Options.airportCapacity = np.random.uniform(1.0, 2.0, (3,))  # Wrong size
    with pytest.raises(
        ValueError, match="The airport capacity has a wrong number of elements"
    ):
        Options._check()


def test_Flight_Class():
    # Test creation and methods
    flight = Flight_Class(1, 10.0, 2.0, 0, 1)
    assert flight.ac == 1
    assert flight.schedDepTime == 10.0
    assert flight.schedArrTime == 12.0
    assert flight.schedDuration == 2.0
    assert flight.origAirp == 0
    assert flight.destAirp == 1

    # Test GetDelay method
    flight.realArrTime = 13.0
    assert flight.GetDelay() == 1.0

    # Test uniqueID generation
    assert flight.uniqueID == "1-10.000000-12.000000-0-1"


def test_Aircraft_Class():
    # Test creation and default values
    aircraft = Aircraft_Class()
    assert aircraft.status == 0
    assert aircraft.airport == 0
    assert aircraft.readyAt == 0.0
    assert aircraft.arrivingAt == 0.0
    assert aircraft.executedFlights == []


def test_Airport_Class():
    # Test creation and default values
    airport = Airport_Class()
    assert airport.lastOp == -10.0
    assert airport.capacity == 0.0
    assert airport.executedFlights == []


def test_Results_Class():
    # Test creation and default values
    results = Results_Class()
    assert results.avgArrivalDelay == 0
    assert results.avgDepartureDelay == 0
    assert results.numArrivalFlights == 0.0
    assert results.numDepartureFlights == 0.0
    assert results.totalArrivalDelay == 0.0
    assert results.totalDepartureDelay == 0.0
