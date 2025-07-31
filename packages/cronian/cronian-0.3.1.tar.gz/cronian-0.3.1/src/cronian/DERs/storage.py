"""Model of a storage asset that can buffer an arbitrary energy carrier."""

import pandas as pd
import pyomo.environ as pyo


def add_storage_asset_to_model(
    model: pyo.AbstractModel,
    prosumer: dict,
    asset_name: str,
    timeseries_data: pd.DataFrame,
    number_of_timesteps,
    storage_model: str,
):
    """Add a storage asset to the optimization model of the given prosumer.

    Example of storage assets: battery, heat storage, hydrogen storage, etc.

    Args:
    -----
        model: Pyomo model to which the prosumer's storage will be added.
        prosumer: Dictionary containing prosumer details.
        asset_name: Name of the storage asset, e.g., battery.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        number_of_timesteps: Number of timesteps to run the optimization for.
        storage_model: Type of storage model to use: `simple` or `complex`.

    Returns:
    --------
        Pyomo AbstractModel with the storage asset added to it.

    Raises:
    -------
        ValueError: If an invalid storage model is specified.
    """
    if storage_model.lower() == "simple":
        return add_simple_model_of_storage_asset(model, prosumer, asset_name, timeseries_data, number_of_timesteps)
    elif storage_model.lower() == "complex":
        return add_complex_model_of_storage_asset(model, prosumer, asset_name, timeseries_data, number_of_timesteps)
    else:
        raise ValueError(f"Invalid storage model specified: {storage_model}. Choose 'simple' or 'complex'.")


def add_simple_model_of_storage_asset(
    model: pyo.AbstractModel,
    prosumer: dict,
    asset_name: str,
    timeseries_data: pd.DataFrame,
    number_of_timesteps,
) -> pyo.AbstractModel:
    """Add a simple model of the storage asset to the optimization model.

    NOTE: The `simple_storage` model does not strictly/explicitly restrict the
    simultaneous charge and discharge of the storage. Hence, under negative electricity
    prices and excess wind generation, storage may charge and discharge at the same time.

    Args:
    -----
        model: Pyomo model to which the prosumer's storage will be added.
        prosumer: Dictionary containing prosumer details.
        asset_name: Name of the storage asset, e.g., battery.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        number_of_timesteps: Number of timesteps to run the optimization for.

    Returns:
    --------
        Pyomo AbstractModel with the storage asset added to it.

    Raises:
    -------
        KeyError: If a required asset parameter is missing
    """
    prosumer_id = prosumer["id"]
    storage_asset = prosumer["assets"][asset_name]

    try:
        initial_energy = storage_asset["initial_energy"]
        energy_capacity = storage_asset["energy_capacity"]
        charge_capacity = storage_asset["charge_capacity"]
        discharge_capacity = storage_asset["discharge_capacity"]
        charge_efficiency = storage_asset["charge_efficiency"]
        discharge_efficiency = storage_asset["discharge_efficiency"]
    except KeyError as e:
        raise KeyError(f"Missing key {e} in storage asset {asset_name} for prosumer {prosumer_id}")

    # Parameters
    setattr(model, f"{prosumer_id}_{asset_name}_init_energy", pyo.Param(initialize=initial_energy, mutable=True))
    setattr(model, f"{prosumer_id}_{asset_name}_energy_capacity", pyo.Param(initialize=energy_capacity))
    setattr(model, f"{prosumer_id}_{asset_name}_charge_capacity", pyo.Param(initialize=charge_capacity))
    setattr(model, f"{prosumer_id}_{asset_name}_discharge_capacity", pyo.Param(initialize=discharge_capacity))
    setattr(model, f"{prosumer_id}_{asset_name}_charge_efficiency", pyo.Param(initialize=charge_efficiency))
    setattr(model, f"{prosumer_id}_{asset_name}_discharge_efficiency", pyo.Param(initialize=discharge_efficiency))

    # Variables
    setattr(model, f"{prosumer_id}_{asset_name}_charge", pyo.Var(model.time, within=pyo.NonNegativeReals))
    setattr(model, f"{prosumer_id}_{asset_name}_discharge", pyo.Var(model.time, within=pyo.NonNegativeReals))
    setattr(model, f"{prosumer_id}_{asset_name}_energy", pyo.Var(model.time, within=pyo.NonNegativeReals))

    # Constraints
    # 1. Storage asset charge and discharge power limits
    def storage_charge_power_limit_rule(model, t):
        return getattr(model, f"{prosumer_id}_{asset_name}_charge")[t] <= getattr(
            model, f"{prosumer_id}_{asset_name}_charge_capacity"
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_charge_constraint",
        pyo.Constraint(model.time, rule=storage_charge_power_limit_rule),
    )

    def storage_discharge_power_limit_rule(model, t):
        return getattr(model, f"{prosumer_id}_{asset_name}_discharge")[t] <= getattr(
            model, f"{prosumer_id}_{asset_name}_discharge_capacity"
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_discharge_constraint",
        pyo.Constraint(model.time, rule=storage_discharge_power_limit_rule),
    )

    # 2. Storage asset energy level consistency balance
    def storage_energy_level_consistency_rule(model, t):
        if t == model.time.first():
            storage_energy = getattr(model, f"{prosumer_id}_{asset_name}_init_energy")
        else:
            storage_energy = getattr(model, f"{prosumer_id}_{asset_name}_energy")[model.time.prev(t)]

        return (
            getattr(model, f"{prosumer_id}_{asset_name}_energy")[t]
            == storage_energy
            + getattr(model, f"{prosumer_id}_{asset_name}_charge_efficiency")
            * getattr(model, f"{prosumer_id}_{asset_name}_charge")[t]
            - (1 / getattr(model, f"{prosumer_id}_{asset_name}_discharge_efficiency"))
            * getattr(model, f"{prosumer_id}_{asset_name}_discharge")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_energy_level_consistency_constraint",
        pyo.Constraint(model.time, rule=storage_energy_level_consistency_rule),
    )

    # 3. Storage asset energy capacity limit constraint
    def storage_energy_capacity_limit_rule(model, t):
        return (
            0,
            getattr(model, f"{prosumer_id}_{asset_name}_energy")[t],
            getattr(model, f"{prosumer_id}_{asset_name}_energy_capacity"),
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_energy_capacity_constraint",
        pyo.Constraint(model.time, rule=storage_energy_capacity_limit_rule),
    )

    # 4. Add optional minimum state-of-charge (SOC) constraint.
    if storage_asset.get("minimum_SOC"):
        add_storage_asset_minimum_state_of_charge_constraint(
            model, prosumer, asset_name, timeseries_data, number_of_timesteps
        )

    # 5. Add optional storage availability charge and discharge constraints.
    if storage_asset.get("availability"):
        add_storage_asset_availability_constraints(model, prosumer, asset_name, timeseries_data, number_of_timesteps)

    return model


def add_complex_model_of_storage_asset(
    model: pyo.AbstractModel,
    prosumer: dict,
    asset_name: str,
    timeseries_data: pd.DataFrame,
    number_of_timesteps,
) -> pyo.AbstractModel:
    """Add a complex model of the storage asset to the optimization model.

    NOTE: The `complex_storage` model strictly/explicitly restricts the simultaneous
    charge and discharge of the storage using binary variables.

    Args:
    -----
        model: Pyomo model to which the prosumer's storage will be added.
        prosumer: Dictionary containing prosumer details.
        asset_name: Name of the storage asset, e.g., battery.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        number_of_timesteps: Number of timesteps to run the optimization for.

    Returns:
    --------
        Pyomo AbstractModel with the storage asset added to it.
    """
    prosumer_id = prosumer["id"]

    # First, add the simple model of the storage asset to reuse model attributes.
    model = add_simple_model_of_storage_asset(model, prosumer, asset_name, timeseries_data, number_of_timesteps)

    # Remove simple storage model's charge and discharge power limits constraints: to be updated with binary variables.
    for attr_name in ["charge_constraint", "discharge_constraint"]:
        model.del_component(getattr(model, f"{prosumer_id}_{asset_name}_{attr_name}"))

    # Introduce binary variables to strictly avoid simultaneous charge and discharge.
    setattr(model, f"{prosumer_id}_{asset_name}_charge_status", pyo.Var(model.time, within=pyo.Binary))
    setattr(model, f"{prosumer_id}_{asset_name}_discharge_status", pyo.Var(model.time, within=pyo.Binary))

    # 1 Redefine storage asset charge and discharge power limits with binary variables.
    # 1.1 Storage asset charge power limit.
    def storage_charge_power_limit_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_{asset_name}_charge")[t]
            <= getattr(model, f"{prosumer_id}_{asset_name}_charge_status")[t]
            * getattr(model, f"{prosumer_id}_{asset_name}_charge_capacity")
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_charge_constraint",
        pyo.Constraint(model.time, rule=storage_charge_power_limit_rule),
    )

    # 1.2 Storage asset discharge power limit.
    def storage_discharge_power_limit_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_{asset_name}_discharge")[t]
            <= getattr(model, f"{prosumer_id}_{asset_name}_discharge_status")[t]
            * getattr(model, f"{prosumer_id}_{asset_name}_discharge_capacity")
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_discharge_constraint",
        pyo.Constraint(model.time, rule=storage_discharge_power_limit_rule),
    )

    # 2. Add constraints to ensure that charge and discharge cannot happen simultaneously.
    def storage_charge_discharge_status_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_{asset_name}_charge_status")[t]
            + getattr(model, f"{prosumer_id}_{asset_name}_discharge_status")[t]
            <= 1
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_charge_discharge_status_constraint",
        pyo.Constraint(model.time, rule=storage_charge_discharge_status_rule),
    )

    return model


def add_storage_asset_minimum_state_of_charge_constraint(
    model: pyo.AbstractModel,
    prosumer: dict,
    asset_name: str,
    timeseries_data: pd.DataFrame,
    number_of_timesteps,
) -> pyo.AbstractModel:
    """Add minimum state-of-charge constraint for the storage asset.

    Args:
    -----
        model: Pyomo model to which the prosumer's storage will be added.
        prosumer: Dictionary containing prosumer details.
        asset_name: Name of the storage asset, e.g., battery.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        number_of_timesteps: Number of timesteps to run the optimization for.

    Returns:
    --------
        Pyomo AbstractModel with the storage asset's min SOC constraints added.
    """
    timesteps = timeseries_data.index[:number_of_timesteps]
    prosumer_id = prosumer["id"]
    storage_asset = prosumer["assets"][asset_name]
    storage_minimum_SOC = storage_asset["minimum_SOC"]

    if isinstance(storage_minimum_SOC, str):  # If str, then its values should be picked from timeseries_data.
        storage_minimum_SOC = timeseries_data.loc[timesteps, f"{prosumer_id}_{asset_name}_min_soc"].values
    else:
        storage_minimum_SOC = [storage_minimum_SOC] * number_of_timesteps

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_minimum_SOC",
        pyo.Param(model.time, initialize=dict(zip(timesteps, storage_minimum_SOC))),
    )

    def storage_min_soc_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_{asset_name}_energy")[t]
            >= getattr(model, f"{prosumer_id}_{asset_name}_energy_capacity")
            * getattr(model, f"{prosumer_id}_{asset_name}_minimum_SOC")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_{asset_name}_minimum_SOC_constraint",
        pyo.Constraint(model.time, rule=storage_min_soc_rule),
    )

    return model


def add_storage_asset_availability_constraints(
    model: pyo.AbstractModel,
    prosumer: dict,
    asset_name: str,
    timeseries_data: pd.DataFrame,
    number_of_timesteps,
) -> pyo.AbstractModel:
    """Add availability constraints for the storage asset.

    Args:
    -----
        model: Pyomo model to which the prosumer's storage will be added.
        prosumer: Dictionary containing prosumer details.
        asset_name: Name of the storage asset, e.g., battery.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        number_of_timesteps: Number of timesteps to run the optimization for.

    Returns:
    --------
        Pyomo AbstractModel with the storage's availability constraints added.
    """
    timesteps = timeseries_data.index[:number_of_timesteps]
    prosumer_id = prosumer["id"]
    storage_asset = prosumer["assets"][asset_name]
    storage_availability = storage_asset["availability"]

    if isinstance(storage_availability, str):  # If str, then its values should be picked from timeseries_data.
        storage_availability = timeseries_data.loc[timesteps, f"{prosumer_id}_{asset_name}_availability"].values
    else:
        storage_availability = [storage_availability] * number_of_timesteps

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_availability",
        pyo.Param(model.time, initialize=dict(zip(timesteps, storage_availability))),
    )

    # 1. Storage asset availability charge constraint.
    def storage_availability_charge_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_{asset_name}_charge")[t]
            <= getattr(model, f"{prosumer_id}_{asset_name}_charge_capacity")
            * getattr(model, f"{prosumer_id}_{asset_name}_availability")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_availability_charge_constraint",
        pyo.Constraint(model.time, rule=storage_availability_charge_rule),
    )

    # 2. Storage asset availability discharge constraint.
    def storage_availability_discharge_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_{asset_name}_discharge")[t]
            <= getattr(model, f"{prosumer_id}_{asset_name}_discharge_capacity")
            * getattr(model, f"{prosumer_id}_{asset_name}_availability")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_availability_discharge_constraint",
        pyo.Constraint(model.time, rule=storage_availability_discharge_rule),
    )

    return model
