import pyomo.environ as pyo
import pytest

from cronian.base_model import create_optimization_model
from cronian.generators import add_all_generators
from cronian.objective_func import set_model_objective_function
from cronian.prosumers import build_prosumer_model
from cronian.system_balance import set_system_electric_power_balance_constraint


def create_model(
    generic_config,
    base_load,
    price_timeseries,
    generic_csv,
    generators,
    prosumers,
    init_store_level,
):
    """Create a basic but complete optimization model that can be run."""
    num_timesteps = generic_config["General"]["number_of_timesteps"]
    model = create_optimization_model(base_load, price_timeseries, num_timesteps)
    add_all_generators(model, generators, generic_csv)
    for prosumer_config in prosumers.values():
        build_prosumer_model(
            model=model,
            prosumer=prosumer_config,
            timeseries_data=generic_csv,
            number_of_timesteps=num_timesteps,
            storage_model="simple",
            init_store_levels=init_store_level,
        )

    set_system_electric_power_balance_constraint(model)
    set_model_objective_function(model, prosumers, price_timeseries)

    return model


# Check if the Gurobi solver is available
gurobi_available = pyo.SolverFactory("gurobi").available(exception_flag=False)


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
@pytest.mark.parametrize(
    ["init_store", "expected"],
    [
        (None, {"transport": 1238.9589999999998, "industrial_hydrogen": 1420.6657}),
        ({"transport": 10}, {"transport": 1228.9589999999998, "industrial_hydrogen": 1420.6657}),
        ({"industrial_hydrogen": 20}, {"transport": 1238.9589999999998, "industrial_hydrogen": 1400.6657}),
    ],
)
def test_prosumer_init_store_level(
    sample_generic_config,
    sample_base_load,
    sample_price_timeseries,
    sample_generic_csv,
    sample_generators,
    sample_prosumers,
    init_store,
    expected,
):
    """Test that a given `init_store_level` results in matching reduced demand."""
    solver = pyo.SolverFactory("gurobi")
    generators = {
        "G01": {**sample_generators["G01"]},
        "G05": {**sample_generators["G05"]},
    }

    model = create_model(
        sample_generic_config,
        sample_base_load,
        sample_price_timeseries,
        sample_generic_csv,
        generators,
        sample_prosumers,
        init_store,
    )

    model_instance = model.create_instance()
    solver.solve(model_instance)

    transport_flex_energy = list(model_instance.P06_transport_flex_demand_energy.extract_values().values())
    hydrogen_flex_energy = list(model_instance.P08_industrial_hydrogen_flex_demand_energy.extract_values().values())

    assert transport_flex_energy[-1] == pytest.approx(expected["transport"])
    assert hydrogen_flex_energy[-1] == pytest.approx(expected["industrial_hydrogen"])
