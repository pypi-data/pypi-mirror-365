"""Create the base model to which all generators, prosumers, constraints, and the objective function will be added."""

import pandas as pd
import pyomo.environ as pyo


def create_optimization_model(
    base_load: pd.Series | None,
    price_timeseries: pd.DataFrame,
    number_of_timesteps: int | None,
) -> pyo.AbstractModel:
    """Create optimization model with common parameters.

    Args:
    -----
        base_load: pd.Series of Base load from passive consumers.
        price_timeseries: Dataframe containing the prices of energy carriers.
        number_of_timesteps: Number of timesteps to run the optimization for.

    Returns:
    --------
        Abstract Pyomo model with general parameters.
    """
    timesteps = price_timeseries.index[:number_of_timesteps]
    model = pyo.AbstractModel(name="Sector-coupled-co-optimization-model")
    model.time = pyo.Set(initialize=timesteps, ordered=True)

    for energy_carrier in price_timeseries.columns:
        setattr(
            model,
            f"{energy_carrier}_price",
            pyo.Param(
                model.time, initialize=dict(zip(timesteps, price_timeseries.loc[timesteps, energy_carrier].values))
            ),
        )

    # Base electricity demand (represents the electricity demand of passive consumers)
    if base_load is not None:
        model.base_load = pyo.Param(model.time, initialize=dict(zip(timesteps, base_load.values)))
    else:
        model.base_load = pyo.Param(model.time, initialize=dict(zip(timesteps, [0] * len(timesteps))))

    return model
