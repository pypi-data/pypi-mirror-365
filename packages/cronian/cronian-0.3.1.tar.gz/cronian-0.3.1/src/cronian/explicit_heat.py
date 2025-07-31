"""Explicitly built optimization problem of a heat system prosumer.

At the time of implementation (2024-09-01), this prosumer had an unsupported
assets (a heat storage tank: its model was not yet available in the DERs
directory). This script therefore shows how prosumers with unsupported assets
can be added to the simulation: by preparing their explicit configuration and
explicit timeseries data files, and explicitly building their model components.
"""

import pandas as pd
import pyomo.environ as pyo

from .feasible_consumption import calculate_flex_store_bounds


def add_explicit_heat_to_model(
    model: pyo.ConcreteModel,
    explicit_configuration: dict,
    explicit_prosumer_timeseries_data: pd.DataFrame,
    number_of_timesteps: int | None,
) -> pyo.ConcreteModel:
    """Add an explicitly built heat system to the simulation.

    This heat system prosumer agent currently has the following assets:
    1. A large scale heat pump that consumes electricity to produce heat.
    2. A CHP which consumes methane to produce heat and electricity.
    3. A heat storage tank to temporarily buffer heat consumption for later use.

    It also has a flexible heat load which is modeled as a store with deadlines
    on its energy level.

    Args:
    -----
        model: The optimization model to which the heat system will be added.
        explicit_configuration: Yaml config file of the explicit prosumer.
        explicit_prosumer_timeseries_data: The csv file containing timeseries
            data for the explicit prosumer.
        number_of_timesteps: Number of timesteps to run the optimization for.

    Returns:
    --------
        model: The optimization model with the heat system added to it.

    Raises:
    -------
        ValueError: If flex_demand name does not match 'flex+{n:d}'.
    """
    heat_agent_name = "Heat_System_Operator"
    heat_agent_attributes = explicit_configuration["Prosumers"][heat_agent_name]
    prosumer_id = heat_agent_attributes["id"]

    # Heat pump and CHP parameters TODO read from config file
    hp_installed_capacity = 500  # MW
    chp_installed_capacity = 1000  # MW
    heat_storage_initial_energy = 0  # MWh
    heat_storage_energy_capacity = 5000  # MWh
    heat_storage_charge_capacity = 200  # MW
    heat_storage_discharge_capacity = 200  # MW
    heat_storage_charge_efficiency = 0.8
    heat_storage_discharge_efficiency = 0.8
    hp_coefficient_of_performance = 2.0
    chp_electric_efficiency = 0.4
    chp_heat_efficiency = 0.4  # chp methane to heat conversion efficiency

    # ============================ Model parameters ============================
    setattr(model, f"{prosumer_id}_hp_cap", pyo.Param(initialize=hp_installed_capacity))
    setattr(model, f"{prosumer_id}_chp_cap", pyo.Param(initialize=chp_installed_capacity))
    setattr(model, f"{prosumer_id}_q_storage_init_energy", pyo.Param(initialize=heat_storage_initial_energy))
    setattr(model, f"{prosumer_id}_q_storage_energy_cap", pyo.Param(initialize=heat_storage_energy_capacity))
    setattr(model, f"{prosumer_id}_q_storage_charge_cap", pyo.Param(initialize=heat_storage_charge_capacity))
    setattr(model, f"{prosumer_id}_q_storage_discharge_cap", pyo.Param(initialize=heat_storage_discharge_capacity))
    setattr(model, f"{prosumer_id}_hp_COP", pyo.Param(initialize=hp_coefficient_of_performance))
    setattr(model, f"{prosumer_id}_chp_e_eff", pyo.Param(initialize=chp_electric_efficiency))
    setattr(model, f"{prosumer_id}_chp_q_eff", pyo.Param(initialize=chp_heat_efficiency))
    setattr(model, f"{prosumer_id}_q_storage_charge_eff", pyo.Param(initialize=heat_storage_charge_efficiency))
    setattr(model, f"{prosumer_id}_q_storage_discharge_eff", pyo.Param(initialize=heat_storage_discharge_efficiency))

    # Base heat demand profile
    def heat_base_load_profile(model, t):
        base_load_peak_value = heat_agent_attributes["Base_load"]["Peak"]
        csv_column_name = heat_agent_attributes["Base_load"]["Normalized"]
        normalized_profile_base_load = explicit_prosumer_timeseries_data.loc[t, csv_column_name]
        return base_load_peak_value * normalized_profile_base_load

    setattr(model, f"{prosumer_id}_base_q_demand", pyo.Param(model.time, initialize=heat_base_load_profile))

    # Flexible load profile
    flex_load_names = heat_agent_attributes["Flexible_loads"]

    # Initialize store min and max energy levels
    store_min_energy_level, store_max_energy_level = {}, {}

    # Calculate min and max consumption levels for each flexible load
    timesteps = explicit_prosumer_timeseries_data.index[:number_of_timesteps]
    for fd in flex_load_names:
        flex_load_peak_value = heat_agent_attributes["Flexible_loads"][fd]["Peak"]
        csv_column_name = heat_agent_attributes["Flexible_loads"][fd]["Normalized"]
        normalized_profile_flex_load = explicit_prosumer_timeseries_data.loc[timesteps, csv_column_name]
        flex_load_profile = flex_load_peak_value * normalized_profile_flex_load

        # Call function to calculate min and max energy levels
        e_min, e_max = calculate_flex_store_bounds(fd, flex_load_profile.values)
        store_min_energy_level[fd] = e_min
        store_max_energy_level[fd] = e_max

    for fd in flex_load_names:
        # Add store min energy level pyomo param
        setattr(
            model,
            f"{prosumer_id}_{fd}_store_q_e_min",  # model.ID_Flex+1_store_q_e_min
            pyo.Param(model.time, initialize=dict(zip(timesteps, store_min_energy_level[fd]))),
        )

        # Add store max energy level pyomo param
        setattr(
            model,
            f"{prosumer_id}_{fd}_store_q_e_max",  # model.ID_Flex+1_store_q_e_max
            pyo.Param(model.time, initialize=dict(zip(timesteps, store_max_energy_level[fd]))),
        )

    # ============================= Model variables ============================
    setattr(
        model,
        f"{prosumer_id}_hp_electricity_consumption",
        pyo.Var(model.time, domain=pyo.NonNegativeReals, initialize=0),
    )
    setattr(model, f"{prosumer_id}_hp_heat_production", pyo.Var(model.time, domain=pyo.NonNegativeReals, initialize=0))
    setattr(
        model,
        f"{prosumer_id}_chp_methane_consumption",
        pyo.Var(model.time, domain=pyo.NonNegativeReals, initialize=0),
    )
    setattr(
        model,
        f"{prosumer_id}_chp_electricity_production",
        pyo.Var(model.time, domain=pyo.NonNegativeReals, initialize=0),
    )
    setattr(model, f"{prosumer_id}_chp_heat_production", pyo.Var(model.time, domain=pyo.NonNegativeReals, initialize=0))
    setattr(
        model,
        f"{prosumer_id}_q_storage_charge_power",
        pyo.Var(model.time, domain=pyo.NonNegativeReals, initialize=0),
    )
    setattr(
        model,
        f"{prosumer_id}_q_storage_discharge_power",
        pyo.Var(model.time, domain=pyo.NonNegativeReals, initialize=0),
    )
    setattr(model, f"{prosumer_id}_q_storage_energy", pyo.Var(model.time, domain=pyo.NonNegativeReals, initialize=0))

    for fd in flex_load_names:
        # Add store power decision variables
        setattr(
            model,
            f"{prosumer_id}_{fd}_store_q_power",  # model.ID_Flex+1_store_q_power
            pyo.Var(model.time, within=pyo.NonNegativeReals),
        )

        # Add store energy level decision variables
        setattr(
            model,
            f"{prosumer_id}_{fd}_store_q_energy",
            pyo.Var(model.time, within=pyo.NonNegativeReals),
        )

    # Heat agent electric power: negative if withdrawing from, and positive if injecting electricity to the grid
    setattr(model, f"{prosumer_id}_electric_power", pyo.Var(model.time, domain=pyo.Reals, initialize=0))

    # =============== Relationship between optimization variables ==============
    # Relationship between prosumer electric power and electricity production/consumption of chp/hp
    def prosumer_electric_power_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_electric_power")[t]
            == getattr(model, f"{prosumer_id}_chp_electricity_production")[t]
            - getattr(model, f"{prosumer_id}_hp_electricity_consumption")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_net_electric_power_constraint",
        pyo.Constraint(model.time, rule=prosumer_electric_power_rule),
    )

    # ============================ Model constraints ===========================
    def hp_capacity_limit_rule(model, t):
        return (0, getattr(model, f"{prosumer_id}_hp_heat_production")[t], getattr(model, f"{prosumer_id}_hp_cap"))

    setattr(model, f"{prosumer_id}_hp_cap_limit_constraint", pyo.Constraint(model.time, rule=hp_capacity_limit_rule))

    def chp_capacity_limit_rule(model, t):
        return (
            0,
            getattr(model, f"{prosumer_id}_chp_methane_consumption")[t],
            getattr(model, f"{prosumer_id}_chp_cap"),
        )

    setattr(model, f"{prosumer_id}_chp_cap_limit_constraint", pyo.Constraint(model.time, rule=chp_capacity_limit_rule))

    def heat_storage_charge_capacity_limit_rule(model, t):
        return (
            0,
            getattr(model, f"{prosumer_id}_q_storage_charge_power")[t],
            getattr(model, f"{prosumer_id}_q_storage_charge_cap"),
        )

    setattr(
        model,
        f"{prosumer_id}_q_storage_charge_cap_constraint",
        pyo.Constraint(model.time, rule=heat_storage_charge_capacity_limit_rule),
    )

    def heat_storage_discharge_capacity_limit_rule(model, t):
        return (
            0,
            getattr(model, f"{prosumer_id}_q_storage_discharge_power")[t],
            getattr(model, f"{prosumer_id}_q_storage_discharge_cap"),
        )

    setattr(
        model,
        f"{prosumer_id}_q_storage_discharge_cap_constraint",
        pyo.Constraint(model.time, rule=heat_storage_discharge_capacity_limit_rule),
    )

    def hp_electricity_to_heat_conversion_rule(model, t):
        return getattr(model, f"{prosumer_id}_hp_heat_production")[t] == getattr(
            model, f"{prosumer_id}_hp_electricity_consumption"
        )[t] * getattr(model, f"{prosumer_id}_hp_COP")

    setattr(
        model,
        f"{prosumer_id}_hp_electricity_to_heat_conversion_constraint",
        pyo.Constraint(model.time, rule=hp_electricity_to_heat_conversion_rule),
    )

    def chp_methane_to_electricity_conversion_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_chp_electricity_production")[t]
            == getattr(model, f"{prosumer_id}_chp_e_eff") * getattr(model, f"{prosumer_id}_chp_methane_consumption")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_chp_methane_to_electricity_conversion_constraint",
        pyo.Constraint(model.time, rule=chp_methane_to_electricity_conversion_rule),
    )

    def chp_methane_to_heat_conversion_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_chp_heat_production")[t]
            == getattr(model, f"{prosumer_id}_chp_q_eff") * getattr(model, f"{prosumer_id}_chp_methane_consumption")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_chp_methane_to_heat_conversion_constraint",
        pyo.Constraint(model.time, rule=chp_methane_to_heat_conversion_rule),
    )

    # General function for flexible demand (store) feasible energy levels
    def store_feasible_energy_level_rule_factory(flex_demand):
        def store_feasible_energy_level_rule(model, t):
            return (
                getattr(model, f"{prosumer_id}_{flex_demand}_store_q_e_min")[t],
                getattr(model, f"{prosumer_id}_{flex_demand}_store_q_energy")[t],
                getattr(model, f"{prosumer_id}_{flex_demand}_store_q_e_max")[t],
            )

        return store_feasible_energy_level_rule

    for fd in flex_load_names:
        setattr(
            model,
            f"{prosumer_id}_{fd}_store_q_feasible_region_constraint",
            pyo.Constraint(model.time, rule=store_feasible_energy_level_rule_factory(fd)),
        )

    # General function for flexible demand (store) energy level consistency
    def energy_level_consistency_rule_factory(flex_demand):
        def energy_level_consistency_rule(model, t):
            if t == model.time.first():
                return (
                    getattr(model, f"{prosumer_id}_{flex_demand}_store_q_energy")[t]
                    == 0 + getattr(model, f"{prosumer_id}_{flex_demand}_store_q_power")[t]
                )
            else:
                return (
                    getattr(model, f"{prosumer_id}_{flex_demand}_store_q_energy")[t]
                    == getattr(model, f"{prosumer_id}_{flex_demand}_store_q_energy")[model.time.prev(t)]
                    + getattr(model, f"{prosumer_id}_{flex_demand}_store_q_power")[t]
                )

        return energy_level_consistency_rule

    for fd in flex_load_names:
        setattr(
            model,
            f"{prosumer_id}_{fd}_store_q_energy_level_consistency_constraint",
            pyo.Constraint(model.time, rule=energy_level_consistency_rule_factory(fd)),
        )

    def heat_storage_energy_level_consistency_rule(model, t):
        if t == model.time.first():
            return (
                getattr(model, f"{prosumer_id}_q_storage_energy")[t]
                == getattr(model, f"{prosumer_id}_q_storage_init_energy")  # Initial energy level
                + getattr(model, f"{prosumer_id}_q_storage_charge_eff")
                * getattr(model, f"{prosumer_id}_q_storage_charge_power")[t]
                - (
                    1
                    / getattr(model, f"{prosumer_id}_q_storage_discharge_eff")
                    * getattr(model, f"{prosumer_id}_q_storage_discharge_power")[t]
                )
            )
        else:
            return getattr(model, f"{prosumer_id}_q_storage_energy")[t] == getattr(
                model, f"{prosumer_id}_q_storage_energy"
            )[model.time.prev(t)] + getattr(model, f"{prosumer_id}_q_storage_charge_eff") * getattr(
                model, f"{prosumer_id}_q_storage_charge_power"
            )[t] - (
                1
                / getattr(model, f"{prosumer_id}_q_storage_discharge_eff")
                * getattr(model, f"{prosumer_id}_q_storage_discharge_power")[t]
            )

    setattr(
        model,
        f"{prosumer_id}_q_storage_energy_level_consistency_constraint",
        pyo.Constraint(model.time, rule=heat_storage_energy_level_consistency_rule),
    )

    def heat_storage_energy_capacity_limit_rule(model, t):
        return (
            0,
            getattr(model, f"{prosumer_id}_q_storage_energy")[t],
            getattr(model, f"{prosumer_id}_q_storage_energy_cap"),
        )

    setattr(
        model,
        f"{prosumer_id}_q_storage_energy_cap_constraint",
        pyo.Constraint(model.time, rule=heat_storage_energy_capacity_limit_rule),
    )

    # Heat prosumer agent internal heat balance constraint
    def heat_power_balance_rule(model, t):
        return getattr(model, f"{prosumer_id}_hp_heat_production")[t] + getattr(
            model, f"{prosumer_id}_chp_heat_production"
        )[t] + getattr(model, f"{prosumer_id}_q_storage_discharge_power")[t] - getattr(
            model, f"{prosumer_id}_q_storage_charge_power"
        )[t] == getattr(model, f"{prosumer_id}_base_q_demand")[t] + sum(
            getattr(model, f"{prosumer_id}_{fd}_store_q_power")[t] for fd in flex_load_names
        )

    setattr(
        model,
        f"{prosumer_id}_local_heat_balance_constraint",
        pyo.Constraint(model.time, rule=heat_power_balance_rule),
    )

    return model
