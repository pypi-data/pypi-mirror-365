# -*- coding: utf-8 -*-
"""
Synth AT Delays

A library with a minimal model of operations between airports,
designed to synthetise realistic time series of delays and operations

Please refer to: https://gitlab.com/MZanin/synth-at-delays
for information, tutorials, and other goodies!
"""

import numpy as np


class Options_Class:
    """
    Class encoding all the options for running a simulation.
    """

    def __init__(self):
        self.numAircraft = 0  # count
        self.numAirports = 0  # count
        self.timeBetweenAirports = 0  # hours
        self.airportCapacity = 0  # operations per hour
        self.turnAroundTime = 0  # hours
        self.bufferTime = 0  # hours
        self.routes = []

        self.enRouteDelay = None
        self.enRouteDelay_params = None

        self.airportDelay = None
        self.airportDelay_params = None

        self.paxLinks = None
        self.paxLinksProbability = None  # probability [0-1]
        self.paxLinksBtmLimit = None  # hours
        self.paxLinksTopLimit = None  # hours

        self.nightDuration = 0.0  # hours
        self.simTime = 0  # days

        self.analysisWindow = 60.0  # minutes

        self.verbose = False
        self.rng = np.random.default_rng()

    def set_seed(self, seed=None):
        """Set the random seed for reproducible results.

        Parameters
        ----------
        seed : int, optional
            The random seed to use. If None, a random seed will be used.

        Returns
        -------
        self
            Returns self for method chaining.
        """
        self.rng = np.random.default_rng(seed)
        return self

    def _check(self):
        if type(self.numAircraft) is not int:
            raise ValueError("The number of aircraft is not an integer")
        if self.numAircraft <= 0:
            raise ValueError("The number of aircraft must be positive")

        if type(self.routes) is not list:
            raise ValueError("Routes are not a list")
        if len(self.routes) != self.numAircraft:
            raise ValueError(
                "The number of aircraft (%d) must be equal to the number of routes (%d)"
                % (self.numAircraft, len(self.routes))
            )

        if type(self.numAirports) is not int:
            raise ValueError("The number of airports is not an integer")
        if self.numAirports <= 0:
            raise ValueError("The number of airports must be positive")

        if type(self.timeBetweenAirports) is not np.ndarray:
            raise ValueError("The time between airports is not a Numpy array")
        if self.timeBetweenAirports.ndim != 2:
            raise ValueError(
                "The time between airports is not a 2-d Numpy array, %d dimensions found"
                % self.timeBetweenAirports.ndim
            )
        if np.size(self.timeBetweenAirports) != self.numAirports**2:
            raise ValueError(
                "The time between airports has a wrong number of elements - "
                + " %d found, %d expected"
                % (np.size(self.timeBetweenAirports), self.numAirports**2)
            )
        if np.sum(self.timeBetweenAirports < 0.0) > 0:
            raise ValueError("The time between airports cannot be negative")

        if type(self.airportCapacity) is not np.ndarray:
            raise ValueError("The airport capacity is not a Numpy array")
        if self.airportCapacity.ndim != 1:
            raise ValueError(
                "The airport capacity is not a 1-d Numpy array, %d dimensions found"
                % self.airportCapacity.ndim
            )
        if np.size(self.airportCapacity) != self.numAirports:
            raise ValueError(
                "The airport capacity has a wrong number of elements - "
                + " %d found, %d expected"
                % (np.size(self.airportCapacity), self.numAirports)
            )


class Flight_Class:
    """
    Class encoding information about individual flights.
    """

    def __init__(self, ac, schedDepTime, schedDuration, origAirp, destAirp):
        self.ac = ac  # aircraft index
        self.schedDepTime = schedDepTime  # hours
        self.schedArrTime = schedDepTime + schedDuration  # hours
        self.schedDuration = schedDuration  # hours
        self.origAirp = origAirp  # origin airport index
        self.destAirp = destAirp  # destination airport index
        self.realDepTime = 0.0  # hours
        self.realArrTime = 0.0  # hours
        self.dependence = None
        self.uniqueID = "%d-%f-%f-%d-%d" % (
            ac,
            self.schedDepTime,
            self.schedArrTime,
            origAirp,
            destAirp,
        )

    def GetDelay(self) -> float:
        return self.realArrTime - self.schedArrTime


class Aircraft_Class:
    """
    Class encoding the information about each aircraft.
    """

    def __init__(self):
        self.status = 0  # status code (0=idle, 1=airborne, 2=turnaround)
        self.airport = 0  # current airport index
        self.readyAt = 0.0  # hours
        self.arrivingAt = 0.0  # hours

        self.executedFlights = []


class Airport_Class:
    """
    Class encoding information about the executed operations at a given airport.
    """

    def __init__(self):
        self.lastOp = -10.0  # hours
        self.capacity = 0.0  # operations per hour

        self.executedFlights = []


class Results_Class:
    """
    Class encoding the processed results of a simulation.
    """

    def __init__(self):
        self.avgArrivalDelay = 0  # hours
        self.avgDepartureDelay = 0  # hours
        self.numArrivalFlights = 0.0  # count
        self.numDepartureFlights = 0.0  # count
        self.totalArrivalDelay = 0.0  # hours
        self.totalDepartureDelay = 0.0  # hours
