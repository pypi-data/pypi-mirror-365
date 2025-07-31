import numpy as np
import pyomo.environ as pyo
import pytest

from cronian.base_model import create_optimization_model
from cronian.explicit_heat import add_explicit_heat_to_model
from cronian.generators import add_all_generators
from cronian.objective_func import set_model_objective_function
from cronian.prosumers import add_built_prosumers_to_optimization_model
from cronian.system_balance import set_system_electric_power_balance_constraint

# Check if the Gurobi solver is available
gurobi_available = pyo.SolverFactory("gurobi").available(exception_flag=False)


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_co_optimization_model_feasibility(sample_model):
    """Test that the entire co-optimization model is feasible and solves to optimality.

    NOTE: This test is done with all DataFrames having integer indices.
    """
    solver = pyo.SolverFactory("gurobi")

    co_optimization_model = sample_model.create_instance()
    results = solver.solve(co_optimization_model)

    assert results.solver.termination_condition == pyo.TerminationCondition.optimal


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_co_optimization_model_market_prices(sample_model, sample_generators):
    """Test that market prices are non-negative and less than the marginal costs of the most expensive generator."""
    # Iterate through generator marginal cost in the config file and get the most expensive marginal cost (b)
    max_marginal_cost = 0

    for _, params in sample_generators.items():
        if params["marginal_cost_linear"] > max_marginal_cost:
            max_marginal_cost = params["marginal_cost_linear"]

    # Solve model and get market_prices to run the test
    co_optimization_model = sample_model.create_instance()
    co_optimization_model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
    solver = pyo.SolverFactory("gurobi")
    solver.solve(co_optimization_model)
    market_prices = []

    for t in co_optimization_model.time:
        market_prices.append(
            co_optimization_model.dual[co_optimization_model.system_electric_power_balance_constraint[t]]
        )
    market_prices = np.array(market_prices)

    assert np.all(np.round(market_prices, 5) >= 0.0)
    assert np.all(np.round(market_prices, 5) <= max_marginal_cost)


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_co_optimization_model_feasibility_with_datetime_indexed_timeseries(
    sample_base_load,
    sample_generators,
    sample_prosumers,
    sample_generic_config,
    sample_explicit_config,
    sample_generic_csv,
    sample_price_timeseries,
    sample_explicit_csv,
    sample_datetime_index,
):
    """Test that the model still runs with DatetimeIndex timeseries."""
    num_timesteps = sample_generic_config["General"]["number_of_timesteps"]

    # Change the current integer indices of all DataFrames to DatetimeIndex.
    sample_generic_csv.index = sample_datetime_index
    sample_price_timeseries.index = sample_datetime_index
    sample_explicit_csv.index = sample_datetime_index

    model = create_optimization_model(sample_base_load, sample_price_timeseries, num_timesteps,)
    add_all_generators(model, sample_generators, sample_generic_csv)
    add_built_prosumers_to_optimization_model(
        model, sample_prosumers, sample_generic_csv, num_timesteps, storage_model="simple",
    )
    add_explicit_heat_to_model(model, sample_explicit_config, sample_explicit_csv, num_timesteps)
    set_system_electric_power_balance_constraint(model)
    set_model_objective_function(model, sample_prosumers, sample_price_timeseries)

    co_optimization_model = model.create_instance()
    solver = pyo.SolverFactory("gurobi")
    results = solver.solve(co_optimization_model)

    assert results.solver.termination_condition == pyo.TerminationCondition.optimal
