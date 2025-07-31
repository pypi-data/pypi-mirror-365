"""Functions to add prosumer's demands to the optimization model.

It currently contains the following functions:
    - add_prosumer_demands
    - add_prosumer_base_demand
    - add_prosumer_flex_demands
"""

import numpy as np
import pandas as pd
import pyomo.environ as pyo

from .feasible_consumption import calculate_flex_store_bounds
from .store_factory import (
    store_energy_level_consistency_rule_factory,
    store_feasible_energy_level_rule_factory,
)


def add_prosumer_demands(
    model: pyo.AbstractModel,
    prosumer: dict,
    timeseries_data: pd.DataFrame,
    number_of_timesteps: int,
    end_use_demand: str,
    init_store_level: float = 0,
) -> None:
    """Add the end_use demands of the prosumer to the optimization model.

    Args:
    -----
        model: The Pyomo model to add components to.
        prosumer: Dictionary containing prosumer details.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        number_of_timesteps: Number of timesteps to run the optimization for.
        end_use_demand: Name of end_use demand, e.g., space_heating.
        init_store_level: Amount of energy to initialize the store with from
            previously satisfied flexible demand.
    """
    demands = prosumer["demand"][end_use_demand]

    if "base" in demands:  # Check if prosumer has base electric demand
        add_prosumer_base_demand(model, prosumer, timeseries_data, number_of_timesteps, end_use_demand)

    if "flexible" in demands:
        add_prosumer_flex_demands(
            model, prosumer, timeseries_data, number_of_timesteps, end_use_demand, init_store_level
        )


def add_prosumer_base_demand(
    model: pyo.AbstractModel,
    prosumer: dict,
    timeseries_data: pd.DataFrame,
    number_of_timesteps: int,
    end_use_demand: str,
) -> None:
    """Add prosumer's base demand as Pyomo Param to the optimization model.

    Args:
    -----
        model: Pyomo Abstract model.
        prosumer:  Dictionary containing prosumer details.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators, demand profiles of prosumers, etc.
        number_of_timesteps: Number of timesteps to run the optimization for.
        end_use_demand: Name of end_use demand, e.g., space_heating.
    """
    if "base" not in prosumer["demand"][end_use_demand]:
        return

    prosumer_id = prosumer["id"]
    base_demand = prosumer["demand"][end_use_demand]["base"]

    # Retrieve the normalized profile and peak value of the base demand, and compute base_demand_profile.
    timesteps = timeseries_data.index[:number_of_timesteps]
    peak_demand = base_demand["peak"]
    nprofile_name_in_csv = base_demand.get("n_profile")

    if nprofile_name_in_csv is not None:
        scaled_demand = peak_demand * timeseries_data.loc[:, nprofile_name_in_csv]
        base_demand_profile = {t: scaled_demand[t] for t in timesteps}
    else:  # If a normalized timeseries profile is not provided, use the peak demand value for all timesteps.
        base_demand_profile = {t: peak_demand for t in timesteps}

    setattr(
        model,
        f"{prosumer_id}_{end_use_demand}_base_demand",
        pyo.Param(model.time, initialize=base_demand_profile),
    )


def add_prosumer_flex_demands(
    model: pyo.AbstractModel,
    prosumer: dict,
    timeseries_data: pd.DataFrame,
    number_of_timesteps: int,
    end_use_demand: str,
    init_store_level: float = 0,
) -> None:
    """Add prosumer's flexible demand as Pyomo Var (with Cons) to the model.

    Flexible demand is modeled as a store, with constraints on its energy level
    feasible region (e_min and e_max) and energy level consistency.

    If `init_store_level` is given, the energy level feasible region is shifted
    down by the specified amount, with any resulting negative values for `e_min`
    set to 0.

    Args:
    -----
        model: Pyomo Abstract model.
        prosumer:  Dictionary containing prosumer details.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators, demand profiles of prosumers, etc.
        number_of_timesteps: Number of timesteps to run the optimization for.
        end_use_demand: Name of end_use demand (electricity_for_space_heating).
        init_store_level: Amount of energy to initialize the store with from
            previously satisfied flexible demand.
    """
    if "flexible" not in prosumer["demand"][end_use_demand]:
        return

    prosumer_id = prosumer["id"]
    flex_demands = prosumer["demand"][end_use_demand]["flexible"]
    timesteps = timeseries_data.index[:number_of_timesteps]

    # Calculate store (flexible demand) energy feasible region (min and max energy levels)
    flex_demand_store_e_min, flex_demand_store_e_max = [], []

    for fd in flex_demands:
        peak_flex_demand = flex_demands[fd]["peak"]
        nprofile_name_in_csv = flex_demands[fd].get("n_profile")
        if nprofile_name_in_csv is not None:
            fd_profile = peak_flex_demand * timeseries_data.loc[timesteps, nprofile_name_in_csv].values
        else:
            fd_profile = np.full(number_of_timesteps, peak_flex_demand)
        e_min, e_max = calculate_flex_store_bounds(fd, fd_profile)
        flex_demand_store_e_min.append(e_min)
        flex_demand_store_e_max.append(e_max)

    # adjust min and max bound down by initial store level
    store_e_min = np.sum(flex_demand_store_e_min, axis=0) - init_store_level
    store_e_max = np.sum(flex_demand_store_e_max, axis=0) - init_store_level
    store_e_min[store_e_min < 0] = 0  # correct any negative minimum values to 0

    # Add store min and max energy level parameters
    setattr(
        model,
        f"{prosumer_id}_{end_use_demand}_flex_demand_min_energy",
        pyo.Param(model.time, initialize=dict(zip(timesteps, store_e_min))),
    )

    setattr(
        model,
        f"{prosumer_id}_{end_use_demand}_flex_demand_max_energy",
        pyo.Param(model.time, initialize=dict(zip(timesteps, store_e_max))),
    )

    # Add store power and energy level decision variables
    setattr(
        model,
        f"{prosumer_id}_{end_use_demand}_flex_demand_power",
        pyo.Var(model.time, within=pyo.NonNegativeReals),
    )

    setattr(
        model,
        f"{prosumer_id}_{end_use_demand}_flex_demand_energy",
        pyo.Var(model.time, within=pyo.NonNegativeReals),
    )

    # Add store feasible energy level constraint
    setattr(
        model,
        f"{prosumer_id}_{end_use_demand}_flex_feasible_energy_level_constraint",
        pyo.Constraint(model.time, rule=store_feasible_energy_level_rule_factory(prosumer_id, end_use_demand)),
    )

    # Add stores energy level consistency constraint
    setattr(
        model,
        f"{prosumer_id}_{end_use_demand}_flex_energy_level_consistency_constraint",
        pyo.Constraint(
            model.time,
            rule=store_energy_level_consistency_rule_factory(prosumer_id, end_use_demand),
        ),
    )
