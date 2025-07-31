"""Function to add prosumers' assets to the optimization model."""

import pandas as pd
import pyomo.environ as pyo

from .DERs.converter import add_energy_converter_asset_to_model
from .DERs.storage import add_storage_asset_to_model
from .DERs.vre_generator import add_vre_generator_to_model


def add_prosumer_assets_to_model(
    model: pyo.AbstractModel,
    prosumer: dict,
    timeseries_data: pd.DataFrame,
    number_of_timesteps: int | None,
    storage_model: str,
) -> pyo.AbstractModel:
    """Add prosumer's assets to the optimization model.

    Args:
    -----
        model: AbstractModel to which the prosumer's asset will be added.
        prosumer: Dictionary describing the prosumer's attributes.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        number_of_timesteps: Number of timesteps to run the optimization for.
        storage_model: Type of storage model to use: `simple` or `complex`.

    Returns:
    -------
        Pyomo AbstractModel with the prosumer's assets added to it.
    """
    for asset_name, asset_details in prosumer.get("assets", {}).items():
        asset_behavior = asset_details.get("behavior_type")
        if asset_behavior == "converter":
            add_energy_converter_asset_to_model(model, prosumer, asset_name)
        elif asset_behavior == "generator":
            add_vre_generator_to_model(model, prosumer, asset_name, timeseries_data, number_of_timesteps)
        elif asset_behavior == "storage":
            add_storage_asset_to_model(model, prosumer, asset_name, timeseries_data, number_of_timesteps, storage_model)

    return model
