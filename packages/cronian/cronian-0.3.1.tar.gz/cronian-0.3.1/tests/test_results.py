import numpy as np
import pandas as pd
import pyomo.environ as pyo
import pytest

from cronian.results import (
    extract_market_schedule,
    extract_prosumer_dispatch,
    get_electricity_price,
    get_flexible_demand_schedule,
    get_schedule_of_all_assets,
    marginal_cost,
)


@pytest.fixture(scope="module")
def solved_model(sample_model):
    """Solve the model and return the solved model."""
    model = sample_model.create_instance()
    solver = pyo.SolverFactory("gurobi")
    model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
    solver.solve(model)
    return model


gurobi_available = pyo.SolverFactory("gurobi").available(exception_flag=False)


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_extract_market_schedule_output_structure(solved_model, sample_generators, sample_prosumers):
    """Test the output (dataframe) structure of extract_market_schedule."""
    agents = sample_generators.keys() | sample_prosumers.keys()
    market_schedule = extract_market_schedule(solved_model, agents)

    assert isinstance(market_schedule, pd.DataFrame)
    assert set(market_schedule.columns) == set(agents) | {"market-price"}
    assert market_schedule.index.name == "Timesteps"
    assert market_schedule.shape == (len(solved_model.time), len(agents) + 1)


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_extract_market_schedule_values(solved_model, sample_generators, sample_prosumers):
    """Test values of the market schedule (dataframe) extracted from the solved model."""
    agents = sample_generators.keys() | sample_prosumers.keys()
    market_schedule = extract_market_schedule(solved_model, agents)
    for agent_id in list(agents):
        expected_values = (
            [solved_model.gen_power[agent_id, t].value for t in solved_model.time]
            if agent_id.lower().startswith("g")
            else [getattr(solved_model, f"{agent_id}_electric_power")[t].value for t in solved_model.time]
        )

        assert market_schedule[agent_id].to_numpy() == pytest.approx(expected_values)


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_get_flexible_demand_schedule(solved_model, sample_prosumers):
    """Test that for each flexible demand, the function returns a dictionary with the correct keys."""
    prosumer = sample_prosumers["P08"]
    flex_demand_schedule = get_flexible_demand_schedule(solved_model, prosumer)

    assert isinstance(flex_demand_schedule, dict)

    # Each flex_demand has ["min_energy", "max_energy", "power", "energy"].
    for end_use_demand in prosumer.get("demand", {}):
        if "flexible" not in prosumer["demand"][end_use_demand]:
            continue
        for attribute in ["min_energy", "max_energy", "power", "energy"]:
            assert f"{end_use_demand}_{attribute}" in flex_demand_schedule


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_get_schedule_of_all_assets_high_level(solved_model, sample_prosumers):
    """Test that the function returns schedules for all prosumer assets with the correct keys."""
    prosumer = sample_prosumers["P08"]
    all_assets_schedule = get_schedule_of_all_assets(solved_model, prosumer)

    # Get index location across first (and only) dimension of nonzero scheduled hydrogen consumption
    nonzero_hydrogen = (all_assets_schedule["total_hydrogen_consumption"] > 1e-6).nonzero()[0]
    # Check that the consumption of externally priced carrier (hydrogen) is present at the correct times.
    assert (nonzero_hydrogen == [16, 17, 18, 19]).all()

    for asset_name, asset_data in prosumer.get("assets", {}).items():
        asset_inputs = asset_data["input"] if isinstance(asset_data["input"], list) else [asset_data["input"]]
        asset_outputs = asset_data["output"] if isinstance(asset_data["output"], list) else [asset_data["output"]]
        behavior_type = asset_data["behavior_type"]

        if behavior_type == "converter":
            # Ensure input_consumption and output_supply keys exist
            for carrier in asset_inputs:
                assert f"{asset_name}_{carrier}_consumption" in all_assets_schedule
            for carrier in asset_outputs:
                assert f"{asset_name}_{carrier}_supply" in all_assets_schedule

        elif behavior_type == "storage":
            # Ensure charge, discharge, and energy keys exist
            for key in ["charge", "discharge", "energy"]:
                assert f"{asset_name}_{key}" in all_assets_schedule

        elif behavior_type == "generator":
            # Ensure the output_supply key exists
            assert f"{asset_name}_{asset_outputs[0]}_supply" in all_assets_schedule


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_extract_prosumer_dispatch(solved_model, sample_prosumers):
    """Test extract prosumer dispatch."""
    prosumer = sample_prosumers["P08"]
    prosumer_dispatch = extract_prosumer_dispatch(solved_model, prosumer)

    assert isinstance(prosumer_dispatch, pd.DataFrame)
    assert prosumer_dispatch.index.name == "Timesteps"
    assert len(prosumer_dispatch) == len(solved_model.time)

    # Ensure the dispatch is empty if no assets or demand
    empty_prosumer = {"id": "P999", "assets": {}, "demand": {}}
    prosumer_dispatch = extract_prosumer_dispatch(solved_model, empty_prosumer)
    assert prosumer_dispatch.empty


@pytest.fixture(scope="module")
def gen_with_quadratic_costs():
    """Generators with non-zero marginal-cost-quadratic."""
    return {
        "G11": {
            "name": "Gas-1",
            "id": "G11",
            "marginal_cost_quadratic": 0.004,
            "marginal_cost_linear": 6,
            "installed_capacity": 670,
        },
        "G12": {
            "name": "Gas-2",
            "id": "G12",
            "marginal_cost_quadratic": 0.006,
            "marginal_cost_linear": 5,
            "installed_capacity": 530,
        },
    }


def optim_model_two_gens_with_quadratic_costs(gen2_dispatch: int):
    """Optimization model with two generators with non-zero marginal-cost-quadratic."""
    model = pyo.ConcreteModel()
    model.time = pyo.Set(initialize=[0, 1])
    model.gens = pyo.Set(initialize=["Gen1", "Gen2"])

    model.gen_marginal_cost_linear = pyo.Param(model.gens, initialize={"Gen1": 50, "Gen2": 30})
    model.gen_marginal_cost_quadratic = pyo.Param(model.gens, initialize={"Gen1": 0.1, "Gen2": 0.2})

    model.gen_power = pyo.Var(
        model.gens,
        model.time,
        initialize={
            ("Gen1", 0): 5,
            ("Gen1", 1): 5,
            ("Gen2", 0): gen2_dispatch,
            ("Gen2", 1): gen2_dispatch,
        },
    )
    return model


@pytest.mark.parametrize("gen2_dispatch", [5, 100])
def test_get_electricity_price(gen2_dispatch: int):
    """Test get electricity price.

    The 1st case tests that price is determined by the `linear_cost` coefficient because the dispatch
    of generators is low enough that the influence of the `quadratic_cost` coefficient is negligible.
    The 2nd case tests that price is determined by the `quadratic_cost` coefficient because the dispatch
    of generators is high enough that the influence of the `quadratic_cost` coefficient is significant.
    """
    model = optim_model_two_gens_with_quadratic_costs(gen2_dispatch)
    electricity_price = get_electricity_price(model)

    # Price is calculated as max(d(C1)/dQ1, d(C2)/dQ2)
    expected_price = [
        max(marginal_cost(50, 0.1, 5), marginal_cost(30, 0.2, gen2_dispatch)),  # t=0
        max(marginal_cost(50, 0.1, 5), marginal_cost(30, 0.2, gen2_dispatch)),  # t=1
    ]

    assert np.allclose(electricity_price, expected_price)
