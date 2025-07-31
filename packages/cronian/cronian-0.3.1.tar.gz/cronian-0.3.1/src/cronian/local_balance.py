"""Add prosumer's end_use demand carrier local supply-consumption balance constraint to the model."""

import pyomo.environ as pyo


def add_prosumer_local_balance_constraint(model: pyo.AbstractModel, prosumer: dict, end_use_demand: str) -> None:
    """Add prosumer's local carrier supply-consumption balance constraint.

    NOTE: A local a balance constraint is established for each end_use_demand
    whose carrier is not `electricity`. For end_use_demands with `electricity`
    as carrier, the balance is handled by the system electric power balance
    constraint at the market bus.

    Args:
    -----
        model: Pyomo Abstract model.
        prosumer: Dictionary containing prosumer details.
        end_use_demand: Name of the end_use_demand, e.g., space_heating.
    """
    prosumer_id = prosumer["id"]
    if prosumer_id.lower().startswith("b"):
        return  # Battery operator prosumers do not have demand

    end_use_demand_data = prosumer["demand"][end_use_demand]
    end_use_demand_carrier = end_use_demand_data["carrier"]

    # Electricity is explicitly balanced at the market level and so, does not need a local balance constraint.
    if end_use_demand_carrier.lower() == "electricity":
        return

    def prosumer_end_use_demand_carrier_balance_rule(model, t):
        """carrier_supply - carrier_consumption == base_demand + flexible_demand."""
        base_demand = end_use_demand_data.get("base", None)
        flex_demands = end_use_demand_data.get("flexible", None)
        if base_demand and not flex_demands:
            total_demand = getattr(model, f"{prosumer_id}_{end_use_demand}_base_demand")[t]
        elif flex_demands and not base_demand:
            total_demand = getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_power")[t]
        else:
            total_demand = (
                getattr(model, f"{prosumer_id}_{end_use_demand}_base_demand")[t]
                + getattr(model, f"{prosumer_id}_{end_use_demand}_flex_demand_power")[t]
            )

        carrier_supply = calculate_end_use_demand_carrier_supply(model, prosumer, end_use_demand_carrier, t)
        carrier_consumption = calculate_end_use_demand_carrier_consumption(model, prosumer, end_use_demand_carrier, t)

        return carrier_supply - carrier_consumption == total_demand

    setattr(
        model,
        f"{prosumer_id}_{end_use_demand}_local_{end_use_demand_carrier}_balance_constraint",
        pyo.Constraint(model.time, rule=prosumer_end_use_demand_carrier_balance_rule),
    )


def calculate_end_use_demand_carrier_supply(
    model: pyo.AbstractModel, prosumer: dict, end_use_demand_carrier: str, t: int
) -> pyo.Var:
    """Calculate total supply for the given end_use_demand's carrier.

    Args:
    -----
        model: Pyomo Abstract model.
        prosumer: Dictionary containing prosumer details.
        end_use_demand_carrier: Carrier of the end_use_demand, e.g., heat.
        t: Time index in the Pyomo model.

    Returns:
    --------
        pyo.Var: Total supply of an end_use_demand's carrier.
    """
    prosumer_id = prosumer["id"]
    assets = prosumer["assets"]
    # Calculate the carrier_supply: from the outputs of all assets.
    carrier_supply = 0
    for asset_name, asset_data in assets.items():
        asset_behavior = asset_data.get("behavior_type")
        asset_outputs = asset_data["output"] if isinstance(asset_data["output"], list) else [asset_data["output"]]
        for asset_output in asset_outputs:
            if (
                asset_output.lower() == "electricity"  # Electricity is balanced at the market level.
                or asset_output.lower() != end_use_demand_carrier.lower()
            ):
                continue
            if asset_behavior == "storage":
                carrier_supply += getattr(model, f"{prosumer_id}_{asset_name}_discharge")[t]
            else:
                carrier_supply += getattr(model, f"{prosumer_id}_{asset_name}_{asset_output}_supply")[t]

    return carrier_supply


def calculate_end_use_demand_carrier_consumption(
    model: pyo.AbstractModel, prosumer: dict, end_use_demand_carrier: str, t: int
) -> pyo.Var:
    """Calculate total consumption for the given end_use_demand's carrier.

    Args:
    -----
        model: Pyomo Abstract model.
        prosumer: Dictionary containing prosumer details.
        end_use_demand_carrier: Carrier of the end_use_demand, e.g., heat.
        t: Time index in the Pyomo model.

    Returns:
    --------
        pyo.Var: Total consumption of an end_use_demand's carrier.
    """
    prosumer_id = prosumer["id"]
    assets = prosumer["assets"]
    # Calculate carrier_consumption from buffers: supplied carrier directly satisfies load or is consumed by buffers.
    carrier_consumption = 0
    for asset_name, asset_data in assets.items():
        if asset_data.get("behavior_type") != "storage":
            continue
        asset_inputs = asset_data["input"] if isinstance(asset_data["input"], list) else [asset_data["input"]]
        for asset_input in asset_inputs:
            if (
                asset_input.lower() == "electricity"  # Electricity is balanced at the market level.
                or asset_input.lower() != end_use_demand_carrier.lower()
            ):
                continue
            carrier_consumption += getattr(model, f"{prosumer_id}_{asset_name}_charge")[t]

    return carrier_consumption
