import pyomo.environ as pyo
import pytest

from cronian.base_model import create_optimization_model
from cronian.explicit_heat import add_explicit_heat_to_model
from cronian.generators import add_all_generators
from cronian.objective_func import set_model_objective_function


def set_power_balance_cons_with_gens_and_explicit_heat_only(model, sample_explicit_config):
    """Set electricity power balance constraint with all generators and the explicit heat system only."""
    prosumer_id = sample_explicit_config["Prosumers"]["Heat_System_Operator"]["id"]

    def system_electric_power_balance(model, t):
        return (
            sum(model.gen_power[g, t] for g in model.gens) + getattr(model, f"{prosumer_id}_electric_power")[t]
            == model.base_load[t]
        )

    model.system_electric_power_balance_cons = pyo.Constraint(model.time, rule=system_electric_power_balance)

    return model


def test_model_constraints(
    sample_generic_config, sample_explicit_config, sample_base_load, sample_explicit_csv, sample_price_timeseries
):
    """Test that all heat system constraints are added to the model.

    This already implicitly tests that model parameters are added, since constraints are constructed using parameters.
    """
    prosumer_id = sample_explicit_config["Prosumers"]["Heat_System_Operator"]["id"]
    fd = list(sample_explicit_config["Prosumers"]["Heat_System_Operator"]["Flexible_loads"])[0]  # First flex demand
    num_timesteps = sample_generic_config["General"]["number_of_timesteps"]

    model = create_optimization_model(sample_base_load, sample_price_timeseries, num_timesteps)
    add_explicit_heat_to_model(model, sample_explicit_config, sample_explicit_csv, num_timesteps)
    model_instance = model.create_instance()

    heat_constraint_attributes = [
        f"{prosumer_id}_hp_cap_limit_constraint",
        f"{prosumer_id}_chp_cap_limit_constraint",
        f"{prosumer_id}_q_storage_charge_cap_constraint",
        f"{prosumer_id}_q_storage_discharge_cap_constraint",
        f"{prosumer_id}_hp_electricity_to_heat_conversion_constraint",
        f"{prosumer_id}_chp_methane_to_electricity_conversion_constraint",
        f"{prosumer_id}_chp_methane_to_heat_conversion_constraint",
        f"{prosumer_id}_{fd}_store_q_feasible_region_constraint",
        f"{prosumer_id}_{fd}_store_q_energy_level_consistency_constraint",
        f"{prosumer_id}_q_storage_energy_level_consistency_constraint",
        f"{prosumer_id}_q_storage_energy_cap_constraint",
        f"{prosumer_id}_local_heat_balance_constraint",
    ]

    for attr in heat_constraint_attributes:
        assert hasattr(model_instance, attr)


# Check if the Gurobi solver is available
gurobi_available = pyo.SolverFactory("gurobi").available(exception_flag=False)


@pytest.mark.skipif(not gurobi_available, reason="Gurobi solver is not freely available.")
def test_feasibility_model_with_explicit_heat(
    sample_base_load,
    sample_generators,
    sample_generic_config,
    sample_explicit_config,
    sample_generic_csv,
    sample_price_timeseries,
    sample_explicit_csv,
):
    """Test that the model is feasible and solves to optimality after adding generators and the heat system only."""
    prosumers = {}  # No prosumer to be built by the package
    solver = pyo.SolverFactory("gurobi")
    num_timesteps = sample_generic_config["General"]["number_of_timesteps"]

    model = create_optimization_model(sample_base_load, sample_price_timeseries, num_timesteps)
    add_all_generators(model, sample_generators, sample_generic_csv)
    add_explicit_heat_to_model(model, sample_explicit_config, sample_explicit_csv, num_timesteps)
    set_power_balance_cons_with_gens_and_explicit_heat_only(model, sample_explicit_config)
    set_model_objective_function(model, prosumers, sample_price_timeseries)
    model_instance = model.create_instance()
    results = solver.solve(model_instance)

    assert results.solver.termination_condition == pyo.TerminationCondition.optimal
