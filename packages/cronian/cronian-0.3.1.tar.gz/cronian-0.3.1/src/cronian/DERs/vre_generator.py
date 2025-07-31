"""Model of a prosumer's variable renewable energy generator."""

import pandas as pd
import pyomo.environ as pyo


def add_vre_generator_to_model(
    model: pyo.AbstractModel,
    prosumer: dict,
    asset_name: str,
    timeseries_data: pd.DataFrame,
    number_of_timesteps: int | None,
) -> pyo.AbstractModel:
    """Add a prosumer's VRE generator to the optimization model.

    This includes any renewable energy source that is variable in nature with an
    arbitrary carrier: wind, solar_pv, geothermal, solar thermal, etc.

    Args:
    -----
        model: Pyomo model to which a prosumer's VRE generator will be added.
        prosumer: Dictionary containing prosumer details.
        asset_name: Name of the VRE generator asset.
        timeseries_data: Timeseries data containing the availability factors.
        number_of_timesteps: Number of timesteps to run the optimization for.
        asset_name: Name of the VRE generator asset.

    Returns:
    --------
        model: AbstractModel with the added VRE generator.

    Raises:
    -------
        KeyError: If a required asset parameter is missing
    """
    asset = prosumer["assets"][asset_name]
    prosumer_id = prosumer["id"]
    timesteps = timeseries_data.index[:number_of_timesteps]
    carrier = asset["output"]
    installed_capacity = asset["installed_capacity"]
    availability_name = asset["availability_factor"]

    availability_factor = timeseries_data.loc[timesteps, availability_name].values

    # Parameters
    setattr(model, f"{prosumer_id}_{asset_name}_available_capacity", pyo.Param(initialize=installed_capacity))
    setattr(
        model,
        f"{prosumer_id}_{asset_name}_availability_factor",
        pyo.Param(model.time, initialize=dict(zip(timesteps, availability_factor))),
    )

    # Variables
    setattr(
        model,
        f"{prosumer_id}_{asset_name}_{carrier}_supply",
        pyo.Var(model.time, domain=pyo.NonNegativeReals, initialize=0),
    )

    # Constraints
    # Capacity limit: vre_asset_carrier_production <= vre_asset_installed_capacity * vre_asset_availability_factor
    def vre_generator_capacity_limit_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_{asset_name}_{carrier}_supply")[t]
            <= getattr(model, f"{prosumer_id}_{asset_name}_available_capacity")
            * getattr(model, f"{prosumer_id}_{asset_name}_availability_factor")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_capacity_limit_constraint",
        pyo.Constraint(model.time, rule=vre_generator_capacity_limit_rule),
    )

    return model
