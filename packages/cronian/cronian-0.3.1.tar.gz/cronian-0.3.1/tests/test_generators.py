import pyomo.environ as pyo
import pytest

from cronian.base_model import create_optimization_model
from cronian.generators import add_all_generators


@pytest.fixture()
def sample_model(sample_base_load, sample_generic_config, sample_price_timeseries) -> pyo.AbstractModel:
    """Sample Pyomo optimization model.

    NOTE: Do not set the scope to 'module' since we want to create a new pyomo model for each tests. This avoids
    pyomo complaining about adding already existing model components (similar names).
    """
    return create_optimization_model(
        sample_base_load,
        sample_price_timeseries,
        number_of_timesteps=sample_generic_config["General"]["number_of_timesteps"],
    )


def test_generator_attributes(sample_model, sample_generators, sample_generic_csv):
    """Test that generator attributes exist in the model."""
    model = add_all_generators(sample_model, sample_generators, sample_generic_csv).create_instance()

    # Check model attributes
    assert hasattr(model, "gens")
    assert hasattr(model, "gen_power")
    assert hasattr(model, "gen_available_cap")
    assert hasattr(model, "gen_available_cap")
    assert hasattr(model, "gen_capacity_limit_constraint")

    # Validate the generators set
    expected_generators = list(sample_generators)
    assert sorted(model.gens) == sorted(expected_generators)


def test_generator_parameter_vals(sample_model, sample_generators, sample_generic_csv):
    """Test that generator parameters are correctly include in the model."""
    model = add_all_generators(sample_model, sample_generators, sample_generic_csv).create_instance()

    # Validate generator parameters (costs, installed capacity)
    for g in model.gens:
        assert model.gen_marginal_cost_quadratic[g] == pytest.approx(sample_generators[g]["marginal_cost_quadratic"])
        assert model.gen_marginal_cost_linear[g] == sample_generators[g]["marginal_cost_linear"]
        assert model.gen_installed_cap[g] == sample_generators[g]["installed_capacity"]


def test_generator_constraints(sample_model, sample_generators, sample_generic_csv):
    """Test that the generator capacity constraints are correctly set."""
    model = add_all_generators(sample_model, sample_generators, sample_generic_csv).create_instance()

    # Check if the rhs of the generator capacity constraints is correctly set
    for t in model.time:
        for g in model.gens:
            constraint_rhs = pyo.value(model.gen_capacity_limit_constraint[g, t].expr.args[1])
            available_cap_value = pyo.value(model.gen_available_cap[g, t])  # Extract numerical value from expression.
            assert constraint_rhs == pytest.approx(available_cap_value)

    # Check if generator available capacity is correctly set
    for t in model.time:
        for g in model.gens:
            availability_factor = 1  # default availability factor for conventional generators
            if "availability_factor" in sample_generators[g].keys():
                availability_factor = sample_generic_csv.loc[t, sample_generators[g]["availability_factor"]]
            expected_available_cap = pyo.value(model.gen_installed_cap[g]) * availability_factor

            assert pyo.value(model.gen_available_cap[g, t]) == pytest.approx(expected_available_cap)
