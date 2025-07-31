"""Functions to build a prosumer's flexible demand (modeled as a store) constraint."""

import pyomo.environ as pyo


def store_feasible_energy_level_rule_factory(prosumer_id: str, end_use_demand: str) -> pyo.Constraint:
    """Creates the feasible energy level constraints of a store.

    Args:
    -----
       prosumer_id: The prosumer's ID.
       flex_demand: Flexible demand name in prosumer dict.
       end_use_demand: Name of end_use demand (electricity_for_space_heating).

    Returns:
    --------
        A Pyomo constraint for the feasible energy level (e_min and e_max) of
            the store.
    """

    def store_feasible_energy_level_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_min_energy")[t],
            getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_energy")[t],
            getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_max_energy")[t],
        )

    return store_feasible_energy_level_rule


def store_energy_level_consistency_rule_factory(prosumer_id: str, end_use_demand: str) -> pyo.Constraint:
    """Creates the energy level consistency Pyomo constraint of a store.

    Args:
    -----
        prosumer_id: The prosumer's ID.
        flex_demand: Flexible demand name in prosumer dict.
        end_use_demand: Name of end_use demand (electricity_for_space_heating).

    Returns:
    --------
        A Pyomo constraint for the energy level consistency of a store.
    """

    def store_energy_level_consistency_rule(model, t):
        if t == model.time.first():
            store_energy = 0
        else:
            store_energy = getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_energy")[model.time.prev(t)]

        return (
            getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_energy")[t]
            == store_energy + getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_power")[t]
        )

    return store_energy_level_consistency_rule
