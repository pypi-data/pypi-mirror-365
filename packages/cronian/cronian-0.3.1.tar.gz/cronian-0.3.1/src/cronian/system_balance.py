import pyomo.environ as pyo

# NOTE: Contains hard coded explicit heat system operator


def set_system_electric_power_balance_constraint(model: pyo.AbstractModel) -> pyo.AbstractModel:
    """Set an electric power balance constraints for the whole system (market).

    Args:
    -----
        model: Pyomo AbstractModel to which the constraint is added.
        include_base_load: if True, base load from passive consumers is
            included in the optimization model.

    Returns:
    --------
        Pyomo AbstractModel with electric power balance constraint added.
    """

    def system_electric_power_balance_rule(model, t):
        base_load_from_passive_consumers = model.base_load[t]
        generators_total_electric_power = sum(model.gen_power[g, t] for g in model.gens)

        built_prosumers_total_electric_power = 0
        if hasattr(model, "built_prosumers") and model.built_prosumers:
            built_prosumers_total_electric_power += sum(
                getattr(model, f"{prosumer_id}_electric_power")[t] for prosumer_id in model.built_prosumers
            )

        # ============== Hard Coded Explicit Heat System Operator ==============
        explicit_prosumer_electric_power = 0
        if hasattr(model, "EXHSO_electric_power"):
            explicit_prosumer_electric_power += model.EXHSO_electric_power[t]
        # Other explicitly modeled prosumers' electric power variables ...

        return (
            generators_total_electric_power + built_prosumers_total_electric_power + explicit_prosumer_electric_power
            == base_load_from_passive_consumers
        )

    model.system_electric_power_balance_constraint = pyo.Constraint(model.time, rule=system_electric_power_balance_rule)

    return model
