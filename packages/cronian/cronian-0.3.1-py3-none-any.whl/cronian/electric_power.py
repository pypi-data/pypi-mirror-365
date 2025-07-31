from functools import partial

import pyomo.environ as pyo


def add_prosumer_electric_power(model: pyo.AbstractModel, prosumer: dict) -> None:
    """Add prosumer's electric power variable to the model.

    The prosumer interacts with the rest of the system (grid/market) through its
    electric power variable. It is positive when the prosumer is net injecting
    electricity to the grid, and negative when net consuming from the grid.

    Args:
    -----
        model: Pyomo Abstract model.
        prosumer: Dictionary containing prosumer details.
    """
    prosumer_id = prosumer["id"]
    assets = prosumer.get("assets", {})

    add_prosumer_total_electricity_generated_locally_to_model(model, prosumer_id, assets)
    add_prosumer_total_electricity_withdrawn_from_grid_to_model(model, prosumer_id, assets)

    has_electric_demand = check_if_prosumer_has_electric_demand(prosumer)
    if has_electric_demand:
        add_prosumer_corrected_electric_demand_to_model(model, prosumer)

    # Define the electric power decision variable (free variable: -ve when consuming from, & +ve injecting to the grid)
    setattr(model, f"{prosumer_id}_electric_power", pyo.Var(model.time, domain=pyo.Reals))

    def construct_net_electric_power_constraint_rule(model, t):
        """electric_power = total_e_generated_locally - total_e_withdrawn_from_grid - corrected_electric_demand."""
        if has_electric_demand:
            return (
                getattr(model, f"{prosumer_id}_electric_power")[t]
                == getattr(model, f"{prosumer_id}_total_electricity_generated_locally")[t]
                - getattr(model, f"{prosumer_id}_total_electricity_withdrawn_from_grid")[t]
                - getattr(model, f"{prosumer_id}_corrected_electric_demand")[t]
            )
        return (
            getattr(model, f"{prosumer_id}_electric_power")[t]
            == getattr(model, f"{prosumer_id}_total_electricity_generated_locally")[t]
            - getattr(model, f"{prosumer_id}_total_electricity_withdrawn_from_grid")[t]
        )

    setattr(
        model,
        f"{prosumer_id}_net_electric_power_constraint",
        pyo.Constraint(model.time, rule=construct_net_electric_power_constraint_rule),
    )


def add_prosumer_total_electricity_expression_to_model(
    model: pyo.AbstractModel,
    prosumer_id: str,
    assets: dict,
    expression_type: str,
    asset_direction_of_electricity_flow: str,
    storage_asset_attribute: str,
    non_storage_asset_attribute: str,
) -> None:
    """Add total electricity  (withdrawn or generated) expression to model.

    Args:
    -----
        model: Pyomo Abstract model.
        prosumer_id: The prosumer's unique ID.
        assets: Dictionary containing prosumer's assets.
        expression_type: total_electricity expression type: withdrawn/generated.
        asset_direction_of_electricity_flow: Asset's direction of electricity
            flow: input or output.
        storage_asset_attribute: charge if the direction of electricity flow is
            input, and discharge if the direction of electricity flow is output.
        non_storage_asset_attribute: electricity_consumption if the direction of
            electricity flow is input, and electricity_supply if the direction
            of electricity flow is output.
    """

    def total_electricity_expression_rule(model, t):
        total_electricity = 0  # Prosumer's total electricity generated_locally/withdrawn_from_grid.
        for asset_name, asset_data in assets.items():
            behavior = asset_data.get("behavior_type")
            electricity_flow_directions = asset_data[asset_direction_of_electricity_flow]  # inputs or outputs.
            electricity_flow_directions = (
                electricity_flow_directions
                if isinstance(electricity_flow_directions, list)
                else [electricity_flow_directions]
            )
            if "electricity" not in map(str.lower, electricity_flow_directions):
                continue
            attribute = (
                f"{prosumer_id}_{asset_name}_{storage_asset_attribute}"
                if behavior == "storage"
                else f"{prosumer_id}_{asset_name}_{non_storage_asset_attribute}"
            )
            total_electricity += getattr(model, attribute)[t]
        return total_electricity

    setattr(
        model,
        f"{prosumer_id}_total_electricity_{expression_type}",
        pyo.Expression(model.time, rule=total_electricity_expression_rule),
    )


# Define function to add a prosumer's total electricity generated locally to the model.
add_prosumer_total_electricity_generated_locally_to_model = partial(
    add_prosumer_total_electricity_expression_to_model,
    expression_type="generated_locally",
    asset_direction_of_electricity_flow="output",
    storage_asset_attribute="discharge",
    non_storage_asset_attribute="electricity_supply",
)

# Define function to add a prosumer's total electricity withdrawn from the grid to the model.
add_prosumer_total_electricity_withdrawn_from_grid_to_model = partial(
    add_prosumer_total_electricity_expression_to_model,
    expression_type="withdrawn_from_grid",
    asset_direction_of_electricity_flow="input",
    storage_asset_attribute="charge",
    non_storage_asset_attribute="electricity_consumption",
)


def add_prosumer_corrected_electric_demand_to_model(model: pyo.AbstractModel, prosumer: dict) -> None:
    """Add the prosumer's corrected electric demand to the model.

    The corrected electric demand is calculated by summing the base and flexible
    `electricity` demand of the prosumer and dividing that by the average
    efficiency of assets directly supplying the electric demand.

    Args:
    -----
        model: Pyomo Abstract model.
        prosumer: Dictionary containing prosumer details.
    """
    prosumer_id = prosumer["id"]
    assets = prosumer.get("assets", {})

    has_electric_demand = check_if_prosumer_has_electric_demand(prosumer)
    if not has_electric_demand:
        return model

    # 1. Define the corrected electric demand as a Pyomo variable.
    setattr(model, f"{prosumer_id}_corrected_electric_demand", pyo.Var(model.time, domain=pyo.NonNegativeReals))

    # 2. Calculate the average efficiency of assets directly supplying electric demand.
    average_efficiency = calculate_average_efficiency_of_assets_directly_supplying_electric_demand(assets)

    # 3. Add the corrected electric demand rule: corrected_electric_demand = electric_demand / average_efficiency.
    def corrected_electric_demand_rule(model, t):
        end_use_demand_with_electricity_as_carrier = 0
        # Some prosumers such as battery operators may not have a 'demand' key
        for end_use_demand, end_use_demand_data in prosumer.get("demand", {}).items():
            # Non-electricity case already handled by local balance constraints
            if end_use_demand_data["carrier"] != "electricity":
                continue
            if "base" in end_use_demand_data:
                end_use_demand_with_electricity_as_carrier += getattr(
                    model, f"{prosumer_id}_{end_use_demand}_base_demand"
                )[t]
            if "flexible" in end_use_demand_data:
                end_use_demand_with_electricity_as_carrier += getattr(
                    model, f"{prosumer_id}_{end_use_demand}_flex_demand_power"
                )[t]

        return getattr(model, f"{prosumer_id}_corrected_electric_demand")[t] == (
            end_use_demand_with_electricity_as_carrier / average_efficiency
        )

    setattr(
        model,
        f"{prosumer_id}_corrected_electric_demand_constraint",
        pyo.Constraint(model.time, rule=corrected_electric_demand_rule),
    )


def check_if_prosumer_has_electric_demand(prosumer: dict) -> bool:
    """Check if the prosumer has an electric demand.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.

    Returns:
    --------
        True if the prosumer has electric demand, False otherwise.
    """
    demands = prosumer.get("demand", {})
    for end_use_demand_name, end_use_demand_data in demands.items():
        if end_use_demand_data.get("carrier") == "electricity":
            return True
    return False


def calculate_average_efficiency_of_assets_directly_supplying_electric_demand(assets: dict) -> float:
    """Calculate average efficiency of assets directly supplying electric demand.

    Args:
    -----
        assets: Dictionary containing prosumer's assets.

    Returns:
    --------
        Average efficiency of assets directly supplying electric demand.
    """
    asset_efficiencies = []  # For assets having electricity as both input and output.
    for asset_name, asset_data in assets.items():
        asset_behavior = asset_data.get("behavior_type")
        asset_inputs = asset_data["input"] if isinstance(asset_data["input"], list) else [asset_data["input"]]
        asset_outputs = asset_data["output"] if isinstance(asset_data["output"], list) else [asset_data["output"]]
        asset_inputs_lower_case = [asset_input.lower() for asset_input in asset_inputs]
        asset_outputs_lower_case = [asset_output.lower() for asset_output in asset_outputs]
        if (
            "electricity" not in asset_inputs_lower_case
            or "electricity" not in asset_outputs_lower_case
            or asset_behavior == "storage"  # Battery storage is indirectly supplies the electric demand.
        ):
            continue
        # Currently assume it is a single-input-single-output with single efficiency: electricity as input & output.
        asset_efficiencies.append(asset_data["efficiency"])

    average_efficiency = sum(asset_efficiencies) / len(asset_efficiencies) if asset_efficiencies else 1

    return average_efficiency
