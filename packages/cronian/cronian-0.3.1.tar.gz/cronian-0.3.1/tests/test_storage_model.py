"""Test for the two storage models: simple and complex. A battery is used here.

The test is designed such that if a `simple` model is used, the optimizer will
choose to charge and discharge the battery at the same time. This event is provoked
by setting the electricity prices to negative in some timesteps and increasing wind
generation at that time step. The prosumer battery is assigned a small capacity so that
it can be easily flooded with electricity from the wind generator. Since the battery operator
wants to minimize power injection to the grid during negative price periods, it will charge and
discharge the battery at the same time so that some of the electricity from its wind generator is
lost in the round trip due to battery charge and discharge efficiencies.
"""

import pandas as pd
import pyomo.environ as pyo
import pytest

from cronian.prosumers import build_prosumer_model
from cronian.results import extract_prosumer_dispatch

gurobi_available = pyo.SolverFactory("gurobi").available(exception_flag=False)


@pytest.fixture(scope="module")
def battery_prosumer():
    """Battery operator prosumer."""
    return {
        "name": "battery-operator",
        "id": "B01",
        "assets": {
            "battery": {
                "behavior_type": "storage",
                "input": "electricity",
                "output": "electricity",
                "energy_capacity": 5,
                "initial_energy": 0,
                "charge_capacity": 10,
                "discharge_capacity": 10,
                "charge_efficiency": 0.9,
                "discharge_efficiency": 0.9,
            },
            "wind_generator": {
                "behavior_type": "generator",
                "input": "wind",
                "output": "electricity",
                "installed_capacity": 10,
                "availability_factor": "B01_WIND",
            },
        },
    }

@pytest.fixture(scope="module")
def timesteps():
    """Time steps."""
    return [0, 1, 2]

@pytest.fixture(scope="module")
def timeseries_data(timesteps):
    """Time series data."""
    return pd.DataFrame({"B01_WIND": [0.1, 0.5, 0.1]}, index=timesteps)

@pytest.fixture(scope="module")
def e_price(timesteps):
    """Electricity price."""
    return pd.Series([10, -200, 10], index=timesteps)

@pytest.fixture(scope="function")
def base_optimization_model(timesteps, e_price):
    """Create prosumer's optimization model."""
    model = pyo.ConcreteModel()
    model.time = pyo.Set(initialize=timesteps, ordered=True)
    model.e_price = pyo.Param(model.time, initialize=dict(zip(model.time, e_price)))
    return model

def add_objective_function(model):
    """Add prosumer's objective function: maximize profit from energy arbitrage."""

    def objective_rule(model):
        return sum(model.e_price[t] * getattr(model, "B01_electric_power")[t] for t in model.time)

    model.objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)
    return model

@pytest.fixture(scope="function")
def simple_battery_model(timesteps, timeseries_data, battery_prosumer, base_optimization_model):
    """Create a simple battery model."""
    model = build_prosumer_model(
        base_optimization_model, battery_prosumer, timeseries_data, len(timesteps), storage_model="simple",
    )
    model = add_objective_function(model)
    return model

@pytest.fixture(scope="function")
def complex_battery_model(timesteps, timeseries_data, battery_prosumer, base_optimization_model):
    """Create a complex battery model."""
    model = build_prosumer_model(
        base_optimization_model, battery_prosumer, timeseries_data, len(timesteps), storage_model="complex",
    )
    model = add_objective_function(model)
    return model


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_simple_battery_model(simple_battery_model, battery_prosumer):
    """Test that a simple battery model allows for simultaneously charging and discharging."""
    model = simple_battery_model
    solver = pyo.SolverFactory("gurobi")
    solver.solve(model, tee=True)

    results_df = extract_prosumer_dispatch(model, battery_prosumer)

    # Check for simultaneous charge and discharge: the battery should charge and discharge simultaneously at timestep 1
    found_simultaneous_charge_and_discharge_event = (
        results_df.loc[1, "battery_charge"] > 0 and results_df.loc[1, "battery_discharge"] > 0
    )

    assert found_simultaneous_charge_and_discharge_event, "Battery did not charge and discharge simultaneously."


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_complex_battery_model(complex_battery_model, battery_prosumer):
    """Test that a complex battery model does not allow for simultaneously charging and discharging."""
    model = complex_battery_model
    solver = pyo.SolverFactory("gurobi")
    solver.solve(model, tee=True)

    results_df = extract_prosumer_dispatch(model, battery_prosumer)

    found_simultaneous_charge_and_discharge_event = any(
        row["battery_charge"] > 0 and row["battery_discharge"] > 0 for _, row in results_df.iterrows()
    )

    assert not found_simultaneous_charge_and_discharge_event, "Battery charged and discharged simultaneously."
