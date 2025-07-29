import pytest
import numpy as np

import synthatdelays as satd


def test_LinkPassengers():
    Options = satd.Scenario_RandomConnectivity(5, 10, 0.5)
    Options.paxLinks = [[0, 1, 2]]
    Options.paxLinksBtmLimit = 0.0
    Options.paxLinksTopLimit = 2.0
    Options.paxLinksProbability = 1.0

    scheduledFlights = []

    fl = satd.Flight_Class(0, 12.0, 1.0, 0, 1)
    fl.schedArrTime = fl.schedDepTime + fl.schedDuration
    scheduledFlights.append(fl)

    fl = satd.Flight_Class(0, 14.0, 1.0, 1, 2)
    scheduledFlights.append(fl)

    scheduledFlights = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    assert scheduledFlights[1].dependence is not None

    fl = satd.Flight_Class(0, 17.0, 1.0, 1, 2)
    scheduledFlights[1] = fl

    scheduledFlights = satd.PaxLinking.LinkPassengers(Options, scheduledFlights)
    assert scheduledFlights[1].dependence is None


def test_CheckForDependence():
    targetFlight = satd.Flight_Class(0, 12.0, 1.5, 0, 1)
    targetFlight.dependence = None
    assert satd.PaxLinking.CheckForDependence(targetFlight, []) == True

    depFlight = satd.Flight_Class(1, 12.0, 1.5, 1, 0)
    targetFlight.dependence = depFlight.uniqueID
    assert satd.PaxLinking.CheckForDependence(targetFlight, []) == False

    depFlight.realArrTime = 11.5
    assert satd.PaxLinking.CheckForDependence(targetFlight, [depFlight]) == True
