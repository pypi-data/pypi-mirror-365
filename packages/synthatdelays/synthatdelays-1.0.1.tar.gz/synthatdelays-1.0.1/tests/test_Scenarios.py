import pytest
import numpy as np

import synthatdelays as satd


@pytest.mark.parametrize("numAirports", [2, 3, 4])
@pytest.mark.parametrize("numAircraft", [5, 10, 15, 20])
def test_Scenario_RandomConnectivity(numAirports, numAircraft):
    """Test the Random Connectivity scenario by design."""

    Options = satd.Scenario_RandomConnectivity(numAirports, numAircraft, 0.5)
    Options.simTime = 2
    satd.ExecSimulation(Options)


def test_Scenario_IndependentOperationsWithTrends():
    """Test the Trends scenario by design."""

    Options = satd.Scenario_IndependentOperationsWithTrends(True)
    Options.simTime = 2
    satd.ExecSimulation(Options)

    Options = satd.Scenario_IndependentOperationsWithTrends(False)
    Options.simTime = 2
    satd.ExecSimulation(Options)
