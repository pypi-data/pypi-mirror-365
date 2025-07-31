from typing import Iterable

import numpy as np
import pandas as pd
import pyomo.environ as pyo


def extract_market_schedule(model: pyo.ConcreteModel, agent_ids: Iterable[str]) -> pd.DataFrame:
    """Extract the market schedule from the solved optimization model.

    Args:
    -----
        model: Solved Pyomo optimization model.
        agent_ids: Set of agent (generators and prosumers) IDs.

    Returns:
    --------
        market_schedule: DataFrame containing generator and prosumer dispatch.
    """
    # 1. Get market price as dual values of the system electric power balance constraint.
    market_price = [model.dual[model.system_electric_power_balance_constraint[t]] for t in model.time]

    # 2. Build market schedule: includes market price and electric power dispatch values for generators and prosumers.
    market_schedule = build_market_schedule(model, agent_ids, market_price)

    return market_schedule


def extract_market_schedule_milp(model: pyo.ConcreteModel, agent_ids: Iterable[str]) -> pd.DataFrame:
    """Extract the market schedule from the solved MILP optimization model.

    In a MILP model, the concept of duality is no longer applicable, hence,
    market price cannot be directly derived as the dual of the system electric
    power balance constraint. It is calculated using get_electricity_price function.

    Args:
    -----
        model: Solved Pyomo optimization model.
        agent_ids: Set of agent (generators and prosumers) IDs.

    Returns:
    --------
        market_schedule: DataFrame containing generator and prosumer dispatch.
    """
    # 1. Get market price as the cost of the most expensive dispatched generator.
    market_price = get_electricity_price(model)

    # 2. Build market schedule: includes market price and electric power dispatch values for generators and prosumers.
    market_schedule = build_market_schedule(model, agent_ids, market_price)

    return market_schedule


def build_market_schedule(model: pyo.ConcreteModel, agent_ids: Iterable[str], price: list[float]) -> pd.DataFrame:
    """Build market schedule dataframe from the solved optimization model.

    Args:
    -----
        model: Solved Pyomo optimization model.
        agent_ids: Set of agent (generators and prosumers) IDs.
        price: market price.

    Returns:
    --------
        market_schedule: DataFrame containing market_price, generator, and prosumer dispatch.
    """
    market_schedule = {"market-price": price}

    for agent_id in sorted(agent_ids):
        if agent_id.lower().startswith("g"):
            market_schedule[agent_id] = [model.gen_power[agent_id, t].value for t in model.time]
        else:
            var = getattr(model, f"{agent_id}_electric_power")
            market_schedule[agent_id] = [var[t].value for t in model.time]

    market_schedule_df = pd.DataFrame.from_dict(market_schedule, orient="columns", dtype=float)
    market_schedule_df.index = model.time
    market_schedule_df.index.name = "Timesteps"

    return market_schedule_df


def get_electricity_price(model: pyo.ConcreteModel) -> np.ndarray:
    """Get electricity price as the cost of the most expensive dispatched generator.

    Args:
    -----
        model: Solved pyomo instance of the optimization model.

    Returns:
    --------
        np.ndarray representing the electricity price at each timestep.
    """
    generator_costs = np.empty((len(model.time), len(model.gens)))

    for gen_idx, gen in enumerate(model.gens):
        linear_cost = model.gen_marginal_cost_linear[gen]
        quadratic_cost = model.gen_marginal_cost_quadratic[gen]

        for t_idx, t in enumerate(model.time):
            power_output = model.gen_power[gen, t].value
            generator_costs[t_idx, gen_idx] = marginal_cost(linear_cost, quadratic_cost, power_output)

    return np.max(generator_costs, axis=1)


def marginal_cost(linear_cost: float, quadratic_cost: float, power_output: float) -> float:
    """Calculate generator marginal cost as the derivative of the cost function w.r.t. power output.

    Args:
    -----
        linear_cost: linear cost coefficient of the generator.
        quadratic_cost: quadratic cost coefficient of the generator.
        power_output: power output (dispatch) of the generator.

    Returns:
    --------
        marginal_cost: marginal cost of the generator.
    """
    if power_output < 1e-8:
        return 0
    return linear_cost + 2 * quadratic_cost * power_output


def extract_prosumer_dispatch(model: pyo.ConcreteModel, prosumer: dict) -> pd.DataFrame:
    """Extract the dispatch of a prosumer from the solved optimization model.

    Args:
    -----
        model: Solved Pyomo optimization model.
        prosumer: Dictionary containing the prosumer configuration.

    Returns:
    --------
        prosumer_dispatch: DataFrame containing the prosumer's flexible demand
            power and store (energy) levels, and the schedule of all its assets.
    """
    # 1. Get prosumer's flexible demand power and store (energy) levels.
    prosumer_dispatch = get_flexible_demand_schedule(model, prosumer)

    # 2. Get the schedules of all assets of the prosumer.
    all_assets_schedule = get_schedule_of_all_assets(model, prosumer)
    prosumer_dispatch.update(all_assets_schedule)

    # 3. Construct DataFrame from the results dictionary.
    prosumer_dispatch_df = pd.DataFrame.from_dict(prosumer_dispatch, orient="columns", dtype=float)
    prosumer_dispatch_df.index = model.time
    prosumer_dispatch_df.index.name = "Timesteps"

    return prosumer_dispatch_df


def get_flexible_demand_schedule(model: pyo.ConcreteModel, prosumer: dict) -> dict:
    """Get the schedule (power & store level) of the prosumer's flexible demand.

    Args:
    -----
        model: Solved Pyomo optimization model.
        prosumer: Dictionary containing the prosumer configuration.

    Returns:
    --------
        flex_demand_schedule: Dictionary containing the prosumer's flexible
            demand power and store (energy) levels.
    """
    prosumer_id = prosumer["id"]
    flex_demand_schedule = {}

    for end_use_demand in prosumer.get("demand", {}):
        if "flexible" not in prosumer["demand"][end_use_demand]:
            continue

        # Get minimum/maximum energy level of the flexible demand store.
        for bound in ["min", "max"]:
            attribute = getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_{bound}_energy")
            flex_demand_schedule[f"{end_use_demand}_{bound}_energy"] = [attribute[t] for t in model.time]

        # Get flexible demand power/store (energy) level.
        for value in ["power", "energy"]:
            attribute = getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_{value}")
            flex_demand_schedule[f"{end_use_demand}_{value}"] = [attribute[t].value for t in model.time]

    return flex_demand_schedule


def get_schedule_of_all_assets(model: pyo.ConcreteModel, prosumer: dict) -> dict:
    """Get the schedule of all assets of a prosumer.

    Args:
    -----
        model: Solved Pyomo optimization model.
        prosumer: Dictionary containing the prosumer configuration.

    Returns:
    --------
        all_assets_schedule: Dictionary containing the schedule of all assets.
    """
    prosumer_id = prosumer["id"]
    all_assets_schedule = {}

    # Initialize dictionary to store the total consumption of externally priced energy carriers by all assets.
    priced_carriers = [
        p.name.removesuffix("_price") for p in model.component_objects(pyo.Param) if p.name.endswith("_price")
    ]
    priced_carr_consumption = {priced_carrier: np.zeros(len(model.time)) for priced_carrier in priced_carriers }

    for asset_name, asset_data in prosumer.get("assets", {}).items():
        asset_inputs = asset_data["input"] if isinstance(asset_data["input"], list) else [asset_data["input"]]
        asset_outputs = asset_data["output"] if isinstance(asset_data["output"], list) else [asset_data["output"]]

        asset_behavior = asset_data["behavior_type"]

        if asset_behavior == "storage":
            # Get asset (dis)charge and state-of-charge schedule.
            for value in ["charge", "discharge", "energy"]:
                attribute = getattr(model, f"{prosumer_id}_{asset_name}_{value}")
                all_assets_schedule[f"{asset_name}_{value}"] = [attribute[t].value for t in model.time]

        elif asset_behavior == "generator":
            all_assets_schedule[f"{asset_name}_power"] = [
                getattr(model, f"{prosumer_id}_{asset_name}_{asset_outputs[0]}_supply")[t].value for t in model.time
            ]

        elif asset_behavior == "converter":
            # Get asset consumption/supply schedule.
            for carrier_list, carrier_activity_type in zip([asset_inputs, asset_outputs], ["consumption", "supply"]):
                for carrier in carrier_list:
                    attribute = getattr(model, f"{prosumer_id}_{asset_name}_{carrier}_{carrier_activity_type}")
                    all_assets_schedule[f"{asset_name}_{carrier}_{carrier_activity_type}"] = [
                        attribute[t].value for t in model.time
                    ]

                    # Update the total consumption of externally priced energy carriers by all assets.
                    if carrier in priced_carriers and carrier_activity_type == "consumption":
                        priced_carr_consumption[carrier] += np.array([attribute[t].value for t in model.time])

    for priced_carrier, priced_carrier_consumption in priced_carr_consumption.items():
        if np.any(priced_carrier_consumption):  # Only include if consumption is non-zero.
            all_assets_schedule[f"total_{priced_carrier}_consumption"] = priced_carrier_consumption

    return all_assets_schedule
