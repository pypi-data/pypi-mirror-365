"""Model of an energy converter asset."""

import pyomo.environ as pyo


def add_energy_converter_asset_to_model(model: pyo.AbstractModel, prosumer: dict, asset_name: str) -> pyo.AbstractModel:
    """Add energy converter asset to the optimization model of the given prosumer.

    Args:
    -----
        model: AbstractModel to which the prosumer's asset will be added.
        prosumer: Dictionary containing prosumer details.
        asset_name: Name of the converter asset to be added to the model.

    Returns:
    --------
        Pyomo AbstractModel with the energy converter asset added to it.

    Raises:
    -------
        KeyError: If a required asset parameter is missing.
        ValueError: If the asset has multiple inputs and outputs.
    """
    prosumer_id = prosumer["id"]
    try:
        asset_data = prosumer["assets"][asset_name]
        asset_inputs = asset_data["input"] if isinstance(asset_data["input"], list) else [asset_data["input"]]
        asset_outputs = asset_data["output"] if isinstance(asset_data["output"], list) else [asset_data["output"]]
        installed_capacity = asset_data["installed_capacity"]
        efficiency: float | dict = asset_data["efficiency"]
    except KeyError as e:
        raise KeyError(f"Missing key {e} in asset {asset_name} for prosumer {prosumer_id}")

    if len(set(asset_inputs)) == 1 and len(set(asset_outputs)) == 1:
        add_single_input_output_asset_to_model(
            model, prosumer_id, asset_name, asset_inputs[0], asset_outputs[0], installed_capacity, efficiency
        )
    elif len(set(asset_inputs)) == 1 and len(set(asset_outputs)) > 1:
        add_single_input_multiple_outputs_asset_to_model(
            model, prosumer_id, asset_name, asset_inputs[0], asset_outputs, installed_capacity, efficiency
        )
    elif len(set(asset_inputs)) > 1 and len(set(asset_outputs)) == 1:
        add_multiple_inputs_single_output_asset_to_model(
            model, prosumer_id, asset_name, asset_inputs, asset_outputs[0], installed_capacity, efficiency
        )
    else:
        raise ValueError(
            f"Prosumer {prosumer_id} {asset_name} has multiple inputs and outputs, which is not currently supported."
        )

    return model


def add_single_input_output_asset_to_model(
    model: pyo.AbstractModel,
    prosumer_id: str,
    asset_name: str,
    asset_input: str,
    asset_output: str,
    installed_capacity: float,
    efficiency: float,
) -> pyo.AbstractModel:
    """Add single-input-single-output energy converter asset to the model.

    Args:
    -----
        model: pyomo model to which the prosumer's assets will be added.
        prosumer_id: The prosumer's unique ID.
        asset_name: name of the converter asset to be added to the model.
        asset_input: name of the input carrier of the asset.
        asset_output: name of the output carrier of the asset.
        installed_capacity: installed capacity of the asset.
        efficiency: efficiency of the asset.

    Returns:
    --------
        pyomo AbstractModel with the asset added to it.
    """
    # Parameters
    setattr(model, f"{prosumer_id}_{asset_name}_capacity", pyo.Param(initialize=installed_capacity))
    setattr(model, f"{prosumer_id}_{asset_name}_efficiency", pyo.Param(initialize=efficiency))

    # Decision variables
    setattr(
        model, f"{prosumer_id}_{asset_name}_{asset_input}_consumption", pyo.Var(model.time, within=pyo.NonNegativeReals)
    )
    setattr(
        model, f"{prosumer_id}_{asset_name}_{asset_output}_supply", pyo.Var(model.time, within=pyo.NonNegativeReals)
    )

    # Constraints
    # 1. Input to output conversion constraint: asset_output_supply = efficiency * asset_input_consumption
    def input_to_output_conversion_rule(model, t):
        return (
            getattr(model, f"{prosumer_id}_{asset_name}_{asset_output}_supply")[t]
            == getattr(model, f"{prosumer_id}_{asset_name}_efficiency")
            * getattr(model, f"{prosumer_id}_{asset_name}_{asset_input}_consumption")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_{asset_input}_to_{asset_output}_conversion_constraint",
        pyo.Constraint(model.time, rule=input_to_output_conversion_rule),
    )

    # 2. Asset capacity limit constraint: input_consumption <= installed_capacity
    def capacity_limit_rule(model, t):
        return (
            0,
            getattr(model, f"{prosumer_id}_{asset_name}_{asset_input}_consumption")[t],
            getattr(model, f"{prosumer_id}_{asset_name}_capacity"),
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_capacity_limit_constraint",
        pyo.Constraint(model.time, rule=capacity_limit_rule),
    )

    return model


def add_single_input_multiple_outputs_asset_to_model(
    model: pyo.AbstractModel,
    prosumer_id: str,
    asset_name: str,
    asset_input: str,
    asset_outputs: list,
    installed_capacity: float,
    efficiency: dict,
) -> pyo.AbstractModel:
    """Add single-input-multiple-outputs energy converter asset to the model.

    Args:
    -----
        model: pyomo model to which a prosumer's electric boiler will be added.
        prosumer_id: The prosumer's unique ID.
        asset_name: name of the converter asset to be added to the model.
        asset_input: name of the input carrier of the asset.
        asset_outputs: list of names of the output carriers of the asset.
        installed_capacity: installed capacity of the asset.
        efficiency: dictionary containing output efficiencies of the asset.

    Returns:
    --------
        pyomo AbstractModel with the asset added to it.
    """
    # Parameters.
    setattr(model, f"{prosumer_id}_{asset_name}_capacity", pyo.Param(initialize=installed_capacity))
    for output in asset_outputs:
        setattr(model, f"{prosumer_id}_{asset_name}_{output}_efficiency", pyo.Param(initialize=efficiency[output]))

    # Decision variables.
    setattr(
        model, f"{prosumer_id}_{asset_name}_{asset_input}_consumption", pyo.Var(model.time, within=pyo.NonNegativeReals)
    )
    for asset_output in asset_outputs:
        setattr(
            model, f"{prosumer_id}_{asset_name}_{asset_output}_supply", pyo.Var(model.time, within=pyo.NonNegativeReals)
        )

    # Constraints.
    # 1. Input carrier to output conversion constraint: output_supply1 = input_consumption * efficiency1.
    for asset_output in asset_outputs:

        def input_to_output_conversion_rule(model, t, asset_output=asset_output):
            return getattr(model, f"{prosumer_id}_{asset_name}_{asset_output}_supply")[t] == getattr(
                model, f"{prosumer_id}_{asset_name}_{asset_input}_consumption"
            )[t] * getattr(model, f"{prosumer_id}_{asset_name}_{asset_output}_efficiency")

        setattr(
            model,
            f"{prosumer_id}_{asset_name}_{asset_input}_to_{asset_output}_conversion_constraint",
            pyo.Constraint(model.time, rule=input_to_output_conversion_rule),
        )

    # 2. Capacity limit constraint: input_consumption <= installed_capacity.
    def capacity_limit_rule(model, t):
        return (
            0,
            getattr(model, f"{prosumer_id}_{asset_name}_{asset_input}_consumption")[t],
            getattr(model, f"{prosumer_id}_{asset_name}_capacity"),
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_capacity_limit_constraint",
        pyo.Constraint(model.time, rule=capacity_limit_rule),
    )

    return model


def add_multiple_inputs_single_output_asset_to_model(
    model: pyo.AbstractModel,
    prosumer_id: str,
    asset_name: str,
    asset_inputs: list,
    asset_output: str,
    installed_capacity: float,
    efficiency: dict,
) -> pyo.AbstractModel:
    """Add multiple-input-single-output energy converter asset to the model.

    Args:
    -----
        model: pyomo model to which a prosumer's electric boiler will be added.
        prosumer_id: The prosumer's unique ID.
        asset_name: name of the converter asset to be added to the model.
        asset_inputs: list of names of the input carriers of the asset.
        asset_output: name of the output carrier of the asset.
        installed_capacity: installed capacity of the asset.
        efficiency: dictionary containing input efficiencies of the asset.

    Returns:
    --------
        pyomo AbstractModel with the asset added to it.
    """
    # Parameters.
    setattr(model, f"{prosumer_id}_{asset_name}_capacity", pyo.Param(initialize=installed_capacity))
    for asset_input in asset_inputs:
        setattr(
            model, f"{prosumer_id}_{asset_name}_{asset_input}_efficiency", pyo.Param(initialize=efficiency[asset_input])
        )

    # Decision variables.
    for asset_input in asset_inputs:
        setattr(
            model,
            f"{prosumer_id}_{asset_name}_{asset_input}_consumption",
            pyo.Var(model.time, within=pyo.NonNegativeReals),
        )
    setattr(
        model, f"{prosumer_id}_{asset_name}_{asset_output}_supply", pyo.Var(model.time, within=pyo.NonNegativeReals)
    )

    # Constraints.
    # 1. Input carrier to output conversion constraint: output_supply = sum(input_<n>_consumption * efficiency_<n>).
    def input_to_output_conversion_rule(model, t):
        return getattr(model, f"{prosumer_id}_{asset_name}_{asset_output}_supply")[t] == sum(
            getattr(model, f"{prosumer_id}_{asset_name}_{asset_input}_consumption")[t]
            * getattr(model, f"{prosumer_id}_{asset_name}_{asset_input}_efficiency")
            for asset_input in asset_inputs
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_{asset_input}_to_{asset_output}_conversion_constraint",
        pyo.Constraint(model.time, rule=input_to_output_conversion_rule),
    )

    # 2. Capacity limit constraint: output_supply <= installed_capacity.
    def capacity_limit_rule(model, t):
        return (
            0,
            getattr(model, f"{prosumer_id}_{asset_name}_{asset_output}_supply")[t],
            getattr(model, f"{prosumer_id}_{asset_name}_capacity"),
        )

    setattr(
        model,
        f"{prosumer_id}_{asset_name}_capacity_limit_constraint",
        pyo.Constraint(model.time, rule=capacity_limit_rule),
    )

    return model
