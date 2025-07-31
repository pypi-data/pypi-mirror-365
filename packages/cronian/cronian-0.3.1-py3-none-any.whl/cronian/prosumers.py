"""Function to build a prosumer's optimization model from a yaml configuration."""

import pandas as pd
import pyomo.environ as pyo

from .all_assets import add_prosumer_assets_to_model
from .demands import add_prosumer_demands
from .electric_power import add_prosumer_electric_power
from .local_balance import add_prosumer_local_balance_constraint


def add_built_prosumers_to_optimization_model(
    model: pyo.AbstractModel,
    prosumers: dict[str, dict],
    timeseries_data: pd.DataFrame,
    number_of_timesteps: int,
    storage_model: str,
) -> pyo.AbstractModel:
    """Add all built prosumers to the optimization model.

    Args:
    -----
        model: The Pyomo model to add components to.
        prosumers: Dictionary containing all prosumers (excludes explicitly
            modeled prosumers).
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        number_of_timesteps: Number of timesteps to run the optimization for.
        storage_model: Type of storage model to use: `simple` or `complex`.

    Returns:
    --------
        Pyomo AbstractModel with all built prosumers added.
    """
    for prosumer in prosumers.values():
        build_prosumer_model(model, prosumer, timeseries_data, number_of_timesteps, storage_model)

    model.built_prosumers = pyo.Set(initialize=list(prosumers.keys()), ordered=True)
    print("===================================================================")
    print("Running the simulation with the following built prosumers:")
    print(sorted(prosumers.keys()))
    print()

    return model


def build_prosumer_model(
    model: pyo.AbstractModel,
    prosumer: dict,
    timeseries_data: pd.DataFrame,
    number_of_timesteps: int,
    storage_model: str,
    init_store_levels: dict[str, float] = None,
) -> pyo.AbstractModel:
    """Build prosumer's optim. model from prosumer dict and timeseries data.

    Args:
    -----
        model: The Pyomo model to add components to.
        prosumer: Dictionary containing prosumer details.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        number_of_timesteps: Number of timesteps to run the optimization for.
        storage_model: Type of storage model to use: `simple` or `complex`.
        init_store_levels: Amount of energy to initialize each `end_use_demand`
            store with from previously satisfied flexible demand.

    Returns:
    --------
        Pyomo AbstractModel of the given prosumer with all components added.

    Raises:
    -------
        ValueError: If an invalid storage model is provided. Must be 'simple' or 'complex'.
    """
    # Perform low level check for storage_model for cases that build_prosumer_model is used outside of main.
    if storage_model.lower() not in ["simple", "complex"]:
        raise ValueError(f"Invalid storage model: {storage_model}. Must be 'simple' or 'complex'.")

    init_store_levels = init_store_levels or {}  # initialize to empty dict if `None` given

    # Add prosumer DER assets to the base optimization model
    add_prosumer_assets_to_model(model, prosumer, timeseries_data, number_of_timesteps, storage_model)

    for end_use_demand in prosumer.get("demand", {}):
        # Add prosumer's base and flexible demand to the model
        add_prosumer_demands(
            model,
            prosumer,
            timeseries_data,
            number_of_timesteps,
            end_use_demand,
            init_store_levels.get(end_use_demand, 0),
        )

        add_prosumer_local_balance_constraint(model, prosumer, end_use_demand)

    add_prosumer_electric_power(model, prosumer)

    return model
