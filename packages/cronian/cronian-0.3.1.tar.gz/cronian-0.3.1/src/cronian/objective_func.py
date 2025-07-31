from itertools import product

import pandas as pd
import pyomo.environ as pyo


def set_model_objective_function(
    model: pyo.AbstractModel,
    prosumers: dict[str, dict],
    price_timeseries: pd.DataFrame,
) -> pyo.AbstractModel:
    """Set the objective function of the sector-coupled co-optimization model.

    The objective is to minimize the cost of electricity generation and the
    consumption costs of other energy carriers e.g., methane, hydrogen, biomass.

    Args:
    -----
        model: Pyomo AbstractModel to which the objective function is added.
        prosumers: Dictionary containing all prosumers (excludes explicitly
            modeled prosumers).
        price_timeseries: Dataframe containing the prices of energy carriers.

    Returns:
    --------
        Pyomo AbstractModel with objective function added.
    """
    externally_priced_consumption = []
    for energy_carrier, prosumer_id in product(price_timeseries.columns, prosumers.keys()):
        for asset_name, asset_data in prosumers[prosumer_id].get("assets", {}).items():
            asset_behavior = asset_data.get("behavior_type")
            asset_inputs = asset_data["input"] if isinstance(asset_data["input"], list) else [asset_data["input"]]
            if energy_carrier in map(str.lower, asset_inputs) and asset_behavior != "storage":
                # Storage obtains methane from other assets (e.g., gas pipelines) that consume (buy) methane.
                externally_priced_consumption.append((energy_carrier, prosumer_id, asset_name))

    def electricity_generation_and_carriers_consumption_cost(model):
        # 1. Electricity generation costs
        electricity_generation_cost = sum(
            model.gen_marginal_cost_quadratic[g] / 2 * model.gen_power[g, t] ** 2
            for g in model.gens
            for t in model.time
        ) + sum(model.gen_marginal_cost_linear[g] * model.gen_power[g, t] for g in model.gens for t in model.time)

        # 2. Consumption costs for other energy carriers (methane, hydrogen, biomass) of prosumers built using cronian.
        built_prosumers_consumption_cost_other_carriers = 0
        if hasattr(model, "built_prosumers") and model.built_prosumers:
            # Loop through built prosumers that were successfully added to the simulation.
            for energy_carrier, prosumer_id, asset_name in externally_priced_consumption:
                built_prosumers_consumption_cost_other_carriers += sum(
                    getattr(model, f"{prosumer_id}_{asset_name}_{energy_carrier}_consumption")[t]
                    * getattr(model, f"{energy_carrier}_price")[t]
                    for t in model.time
                )

        # ============ Explicitly modeled prosumers: prosumers not built using cronian. ============
        explicit_prosumer_gas_consumption_cost = 0
        if hasattr(model, "EXHSO_chp_methane_consumption"):
            explicit_prosumer_gas_consumption_cost += sum(
                getattr(model, "EXHSO_chp_methane_consumption")[t] * model.methane_price[t] for t in model.time
            )

        # Other explicitly modeled prosumers' gas or other energy carrier consumption variables ...

        return (
            electricity_generation_cost  # Electricity generation costs of all generators
            + built_prosumers_consumption_cost_other_carriers
            + explicit_prosumer_gas_consumption_cost  # Gas consumption costs of explicitly modeled prosumers
        )

    model.objective_func = pyo.Objective(sense=pyo.minimize, rule=electricity_generation_and_carriers_consumption_cost)

    return model
