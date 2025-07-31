"""Script to validate the configurations describing prosumers and generators.

It currently contains the following functions:
    - validate_all_agents: validates uniqueness of generator and prosumer IDs.
    - validate_prosumer: validates the prosumer dict.
    - get_prosumer_id: gets the prosumer ID from its configuration.
    - validate_required_entries: validates required entries in config.
    - validate_fields: recursively checks for empty key fields in config.
    - validate_asset_outputs: ensures assets produce outputs that match demand
        carriers or electricity.
    - validate_assets_input_output_efficiency_relationship: ensures that the set
        of asset's in(out)puts is the same as the set of efficiencies.
    - validate_asset_behavior: ensures that an asset has a valid behavior.
    - validate_asset_behavior_attributes: ensures that an asset has valid
        behavior attributes.
    - validate_base_or_flexible_demand: ensures prosumer has at least a base or
        flex demand.
    - validate_satisfiable_demand: ensures each demand can be satisfied by at
        least one asset.
    - validate_battery_operator: ensures battery operators have at least a
        battery asset & only VRE gens as other asset.
    - validate_irrelevant_prosumer: ensures prosumer with no electric demand or
        battery is not allowed (since it is irrelevant to the simulation).
    - validate_prosumer_potential_feasibility: validates that the prosumer's
        optimization problem is potentially feasible.
"""

import warnings

import pandas as pd

VALID_ASSET_BEHAVIORS = {"generator", "converter", "storage"}
GENERATOR_ATTRIBUTES = {"output", "installed_capacity", "availability_factor"}
CONVERTER_ATTRIBUTES = {"input", "output", "installed_capacity", "efficiency"}
STORAGE_ATTRIBUTES = {
    "input",
    "output",
    "energy_capacity",
    "initial_energy",
    "charge_capacity",
    "discharge_capacity",
    "charge_efficiency",
    "discharge_efficiency",
}


def validate_all_agents(configurations: dict[str, dict], timeseries_data: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Validate agents' IDs and configs before building the optimization model.

    Args:
    -----
        configurations: Nested dictionary containing the configurations defining
            generators, prosumers, and general parameters of the simulation.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...

    Returns:
    --------
        prosumer_ids: A list of unique prosumer IDs.
        generator_ids: A list of unique generator IDs.

    Raises:
    -------
        ValueError: If duplicate IDs exist among prosumers/generators, or if
            prosumers & generators have the same ID.

    Example usage:
    --------------
        from pyprojroot import here
        from configuration import load_configurations

        config_folder = here("tests/test_data/demo_configurations")
        configurations = load_configurations(config_folder)
        validate_all_agents(configurations)
    """
    generators = configurations["Generators"]
    prosumers = configurations["Prosumers"]
    all_prosumers_ids = list(prosumers)
    all_generator_ids = list(generators)

    # Check that the ID of all agents starts with either 'p' or 'b' or 'g'
    for prosumer_id in all_prosumers_ids:
        if not prosumer_id.lower().startswith("p") and not prosumer_id.lower().startswith("b"):
            raise ValueError(f"Prosumer ID {prosumer_id} must start with 'p' or 'b'.")

    for generator_id in all_generator_ids:
        if not generator_id.lower().startswith("g"):
            raise ValueError(f"Generator ID {generator_id} must start with 'g'.")

    all_passed = []
    for prosumer in prosumers.values():
        all_passed.append(validate_prosumer(prosumer, timeseries_data))

    if all(all_passed):
        print()
        print("All agents' yaml configuration files have been validated successfully 🎉🎉🎉 !!!")
        print("==================================================================================")
        print()

    return all_prosumers_ids, all_generator_ids


def validate_prosumer(prosumer: dict, timeseries_data: pd.DataFrame) -> bool:
    """Perform some validation checks on prosumer dict.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...

    Returns:
    --------
        True if all validations for this prosumer are successful.

    Raises:
    -------
        ValueError: If any validation check fails.
    """
    prosumer_id = prosumer["id"]

    demand_carriers = validate_required_entries(prosumer, prosumer_id)
    validate_fields(prosumer, prosumer_id)
    validate_asset_outputs(prosumer, prosumer_id)
    validate_assets_input_output_efficiency_relationship(prosumer, prosumer_id)
    validate_asset_behavior(prosumer, prosumer_id)
    validate_asset_behavior_attributes(prosumer, prosumer_id)
    validate_base_or_flexible_demand(prosumer, prosumer_id)
    validate_satisfiable_demand(prosumer, prosumer_id, demand_carriers)
    validate_battery_operator_assets(prosumer)
    validate_prosumer_relevance(prosumer, prosumer_id)
    validate_prosumer_potential_feasibility(prosumer, timeseries_data)

    return True


def validate_required_entries(prosumer: dict, prosumer_id: str) -> set[str]:
    """Validate required entries for a prosumer.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        prosumer_id: The prosumer's unique ID.

    Returns:
    --------
        demand_carriers: Set of carriers for all demands of the prosumer.

    Raises:
    -------
        ValueError: If any required key is missing in the prosumer dict.
    """
    if prosumer_id.lower().startswith("b"):  # Battery operators do not have demand
        required_keys = ["name", "id"]
    else:  # Non-battery prosumer
        # Prosumers with `electricity` demand are allowed not to have own assets: they are attached to the market bus.
        required_keys = ["name", "id", "demand"]

    missing_keys = [key for key in required_keys if key not in prosumer]
    if missing_keys:
        raise ValueError(f"Prosumer {prosumer_id} is missing the following keys: {missing_keys}. Please provide them.")

    # Check that carrier key is present in demand dict (demand keys are required for non-battery prosumers)
    demand_carriers = set()
    for demand_key, demand_details in prosumer.get("demand", {}).items():
        try:
            demand_carriers.add(demand_details["carrier"])
        except KeyError:
            raise ValueError(
                f"Prosumer {prosumer_id} demand key '{demand_key}' is missing the 'carrier' key. "
                "Please provide the carrier for this demand."
            )

    return demand_carriers


def validate_fields(agent: any, agent_id: str, key_path: str = "") -> None:
    """Recursively check for empty entries in prosumer's configuration file.

    Args:
    -----
        agent: Dictionary containing the agent's details.
        agent_id: The prosumer or generator agent's unique ID.
        key_path: String representing path to the current key for error report.

    Raises:
    -------
        ValueError: If any entry or subentry is empty.
    """
    id = agent_id

    # Handle dict type (start with the prosumer or generator dict)
    if isinstance(agent, dict):
        if not agent:  # Empty dict
            raise ValueError(f"Agent {id} has an empty key: {key_path}. Delete this key if not needed.")

        for key, value in agent.items():
            if isinstance(value, (dict, list)):  # Check for data type (dict or list)
                validate_fields(value, agent_id, key_path + f"['{key}']")  # Recursively check for non-empty entries

            # Handle values (e.g., prosumer[assets][asset_name][asset_param] returns a value)
            elif value is None or value == "" or isinstance(value, bool):  # Invalid: None, empty string, or boolean
                raise ValueError(f"Invalid val {key_path}['{key}'] for agent {id}. Check for None, empty str, or bool")

    # Handle list type (e.g., prosumer[assets] or prosumer[assets][asset_name] returns a list)
    elif isinstance(agent, list):
        if not agent:  # Empty list
            raise ValueError(f"Agent {id} has an empty list: {key_path}. Delete this entry if not needed.")
        for idx, item in enumerate(agent):
            validate_fields(item, agent_id, key_path + f"[{idx}]")


def validate_asset_outputs(prosumer: dict, prosumer_id: str) -> None:
    """Ensure assets produce outputs that match electricity or demand carriers.

    That is, for each asset, its output must be a subset of the prosumer's
    demand carriers and `electricity`. We do not allow assets to produce
    carriers they don't consume except for `electricity` since `electricity` can
    be exchanged with other prosumers at the market bus where they interact.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        prosumer_id: The prosumer's unique ID.

    Raises:
    -------
        ValueError: If an asset has invalid outputs.
    """
    demand_carriers = {demand_data["carrier"] for demand_data in prosumer.get("demand", {}).values()}
    if not demand_carriers:  # Skip validation for prosumers with no demand, for example, battery operators.
        return

    assets = {asset_name.lower(): asset_data for asset_name, asset_data in prosumer.get("assets", {}).items()}
    for asset_name, asset_data in assets.items():
        asset_outputs = set(asset_data["output"]) if isinstance(asset_data["output"], list) else {asset_data["output"]}
        invalid_outputs = asset_outputs - demand_carriers - {"electricity"}
        if invalid_outputs:
            raise ValueError(
                f"Prosumer {prosumer_id} has asset '{asset_name}' with invalid output: {asset_outputs}. "
                f"Expected outputs to match demand carriers: {demand_carriers} or 'electricity'."
            )


def validate_assets_input_output_efficiency_relationship(prosumer: dict, prosumer_id: str) -> None:
    """Ensure that the set of asset's in(out)puts is the same as efficiencies.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        prosumer_id: The prosumer's unique ID.

    Raises:
    -------
        ValueError: If set of asset's in(out)puts is not same as efficiencies.
        NotImplementedError: If the asset has multiple inputs and outputs.
    """
    assets = {asset_name.lower(): asset_data for asset_name, asset_data in prosumer.get("assets", {}).items()}
    for asset_name, asset_data in assets.items():
        # Normalize inputs and outputs to sets
        asset_inputs = set(asset_data["input"]) if isinstance(asset_data["input"], list) else {asset_data["input"]}
        asset_outputs = set(asset_data["output"]) if isinstance(asset_data["output"], list) else {asset_data["output"]}
        asset_efficiencies = asset_data.get("efficiency")

        # 1. Check single-input-single-output assets
        if len(asset_inputs) == 1 and len(asset_outputs) == 1:
            if asset_efficiencies and not isinstance(asset_efficiencies, (float, int)):
                raise ValueError(
                    f"Prosumer {prosumer_id} has asset '{asset_name}' with invalid efficiency: {asset_efficiencies}. "
                    "Expected a single efficiency value for a single input and single output asset."
                )

        # 2. Check single-input-multiple-output assets (e.g., a chp)
        elif len(asset_inputs) == 1 and len(asset_outputs) > 1:
            if asset_efficiencies and not isinstance(asset_efficiencies, dict):
                raise ValueError(
                    f"Prosumer {prosumer_id} has asset '{asset_name}' with invalid efficiency: {asset_efficiencies}. "
                    "Expected a dictionary of efficiencies for each output."
                )
            missing_efficiencies = asset_outputs - set(asset_efficiencies.keys())
            if set(asset_efficiencies.keys()) != asset_outputs and missing_efficiencies:
                missing_efficiencies = asset_outputs - set(asset_efficiencies.keys())
                raise ValueError(
                    f"Prosumer {prosumer_id} has asset '{asset_name}' with missing efficiency: {missing_efficiencies}. "
                    f"Expected efficiency keys to match asset_outputs: {asset_outputs}."
                )

        # 3. Check multiple-input-single-output assets (e.g., a hybrid boiler)
        elif len(asset_inputs) > 1 and len(asset_outputs) == 1:
            if asset_efficiencies and not isinstance(asset_efficiencies, dict):
                raise ValueError(
                    f"Prosumer {prosumer_id} has asset '{asset_name}' with invalid efficiency: {asset_efficiencies}. "
                    "Expected a dictionary of efficiencies for each input."
                )
            missing_efficiencies = asset_inputs - set(asset_efficiencies.keys())
            if set(asset_efficiencies.keys()) != asset_inputs and missing_efficiencies:
                raise ValueError(
                    f"Prosumer {prosumer_id} has asset '{asset_name}' with missing efficiency: {missing_efficiencies}. "
                    f"Expected efficiency keys to match asset_inputs: {asset_inputs}."
                )

        else:  # 4. Multiple-input-multiple-output assets (not yet implemented/supported)
            raise NotImplementedError(
                f"Prosumer {prosumer_id} has asset unsupported '{asset_name}' with multiple inputs and outputs."
            )

        # 5. Validate that the input and output of the storage asset are the same.
        if asset_data.get("behavior_type") != "storage":
            continue
        if len(asset_inputs) != 1 or len(asset_outputs) != 1 or asset_data["input"] != asset_data["output"]:
            raise ValueError(
                f"Prosumer {prosumer_id} storage asset '{asset_name}' has inconsistent: {asset_inputs=} and "
                f"{asset_outputs=} Expected a 'single' consistent input and output for storage."
            )


def validate_asset_behavior(prosumer: dict, prosumer_id: str) -> None:
    """Ensure that an asset has a valid behavior.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        prosumer_id: The prosumer's unique ID.

    Raises:
    -------
        ValueError: If an asset has an invalid behavior.
    """
    assets = {asset_name.lower(): asset for asset_name, asset in prosumer.get("assets", {}).items()}
    for asset_name, asset_details in assets.items():
        if "behavior_type" not in asset_details or asset_details.get("behavior_type") not in VALID_ASSET_BEHAVIORS:
            raise ValueError(
                f"Prosumer {prosumer_id} has asset {asset_name} with no/invalid behavior_type. Please specify one of "
                f"the following behavior_type: {VALID_ASSET_BEHAVIORS}."
            )


def validate_asset_behavior_attributes(prosumer: dict, prosumer_id: str) -> None:
    """Ensure that an asset has valid behavior attributes.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        prosumer_id: The prosumer's unique ID.

    Raises:
    -------
        ValueError: If an asset has an invalid behavior attribute.
    """
    assets = {asset_name.lower(): asset for asset_name, asset in prosumer.get("assets", {}).items()}
    for asset_name, asset_details in assets.items():
        if asset_details.get("behavior_type") == "generator":
            if not GENERATOR_ATTRIBUTES.issubset(set(asset_details.keys())):
                raise ValueError(
                    f"Prosumer {prosumer_id} has generator asset {asset_name} with missing behavior attributes. "
                    f"Please provide all of the following generator attributes: {GENERATOR_ATTRIBUTES}."
                )
        elif asset_details.get("behavior_type") == "converter":
            if not CONVERTER_ATTRIBUTES.issubset(set(asset_details.keys())):
                raise ValueError(
                    f"Prosumer {prosumer_id} has converter asset {asset_name} with missing behavior attributes. "
                    f"Please provide all of the following converter attributes: {CONVERTER_ATTRIBUTES}."
                )
        else:  # If asset is not a generator or converter, then it is a storage asset (see VALID_ASSET_BEHAVIORS).
            if not STORAGE_ATTRIBUTES.issubset(set(asset_details.keys())):
                raise ValueError(
                    f"Prosumer {prosumer_id} has storage asset {asset_name} with missing behavior attributes. "
                    f"Please provide all of the following storage attributes: {STORAGE_ATTRIBUTES}."
                )


def validate_base_or_flexible_demand(prosumer: dict, prosumer_id: str) -> None:
    """Ensure that a prosumer has a base or flexible demand for each demand key.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        prosumer_id: The prosumer's unique ID.

    Raises:
    -------
        ValueError: If the prosumer has no base or flexible demand for each for
            any listed demand key.
    """
    if prosumer_id.lower().startswith("b"):
        return  # Skip validation for battery operators (they don't have demand keys)

    demand_keys = prosumer["demand"].keys()
    missing_demand = []

    for key in demand_keys:
        demand_item = prosumer["demand"][key]
        if "base" not in demand_item and "flexible" not in demand_item:
            missing_demand.append(key)

    if missing_demand:
        raise ValueError(
            f"Prosumer {prosumer_id} is missing 'base' or 'flexible' demand for the following: {missing_demand}. "
            "Each demand key must contain at least a 'base' or 'flexible' demand."
        )


def validate_satisfiable_demand(
    prosumer: dict,
    prosumer_id: str,
    demand_carriers: set,
) -> None:
    """Ensure that each demand can be satisfied by at least one asset.

    This function checks that each demand listed can be satisfied by at
    least one of the prosumer's assets. This is done by creating by creating a
    a set of output of all assets, and then checking that the difference between
    this set and the demand_carriers set is an empty set.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        prosumer_id: The prosumer's unique ID.
        demand_carriers: Set of carriers for all demands of the prosumer.

    Raises:
    -------
        ValueError: If a demand cannot be satisfied by at least one asset.
    """
    all_assets_outputs = set()
    for _, asset_data in prosumer.get("assets", {}).items():
        asset_outputs = asset_data["output"] if isinstance(asset_data["output"], list) else [asset_data["output"]]
        all_assets_outputs.update(asset_outputs)

    carrier_of_unsatisfied_demands = demand_carriers - all_assets_outputs
    # Demands with `electricity` carrier can be satisfied without own assets since they are attached to the market bus.
    carrier_of_unsatisfied_demands.discard("electricity")
    if carrier_of_unsatisfied_demands:
        unsatisfied_demands = {
            d for d in prosumer["demand"] if prosumer["demand"][d]["carrier"] in carrier_of_unsatisfied_demands
        }
        raise ValueError(
            f"Prosumer {prosumer_id} has no asset to satisfy the demands: {unsatisfied_demands} that have carriers :"
            f"{carrier_of_unsatisfied_demands}. Outputs {carrier_of_unsatisfied_demands} must be produced by an asset."
        )


def validate_battery_operator_assets(prosumer: dict) -> None:
    """Ensure all assets of battery operator agent have `electricity` as output.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.

    Raises:
    -------
        ValueError: If any asset of the battery operator does not have
            `electricity` as output.
    """
    prosumer_id = prosumer["id"]
    if not prosumer_id.lower().startswith("b"):
        return

    for asset_name, asset_data in prosumer.get("assets", {}).items():
        asset_outputs = asset_data["output"] if isinstance(asset_data["output"], list) else [asset_data["output"]]
        if "electricity" not in asset_outputs:
            raise ValueError(
                f"Prosumer {prosumer_id} has asset '{asset_name}' with no 'electricity' as output. "
                "All assets of a battery operator/service provider must have at least 'electricity' as output."
            )


def validate_prosumer_relevance(prosumer: dict, prosumer_id: str) -> None:
    """Ensure that a prosumer with no electric demand or asset is not allowed.

    Such a prosumer is irrelevant to the simulation since it does not interact
    with the market bus and hence, does not interact with other prosumers.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        prosumer_id: The prosumer's unique ID.

    Raises:
    -------
        ValueError: If prosumer has no electric demand or electric asset.
    """
    has_electric_demand = any(demand.get("carrier") == "electricity" for demand in prosumer.get("demand", {}).values())

    has_electric_asset = False

    for asset_name, asset_data in prosumer.get("assets", {}).items():
        asset_outputs = asset_data["output"] if isinstance(asset_data["output"], list) else [asset_data["output"]]
        asset_inputs = asset_data["input"] if isinstance(asset_data["input"], list) else [asset_data["input"]]
        if "electricity" in asset_outputs or "electricity" in asset_inputs:
            has_electric_asset = True
            break

    if not has_electric_demand and not has_electric_asset:
        raise ValueError(
            f"Prosumer {prosumer_id} is irrelevant to the simulation: it has no electric demand or electric asset."
        )


def validate_prosumer_potential_feasibility(prosumer: dict, timeseries_data: pd.DataFrame) -> None:
    """Validate that the prosumer's optimization problem is potentially feasible.

    Validate that for each demand carrier, the combined capacity of all assets
    that can satisfy the demand, multiplied by their respective efficiency is
    greater than the maximum demand for that carrier. This is to ensure that the
    optimization problem of the prosumer is feasible. Since the check can be a
    little tricky if storage is present, and hence, we cannot for sure say that
    it is infeasible, we do not immediately crash the simulation but instead, we
    raise a warning for a potential infeasibility in the prosumer's optimization
    problem.

    NOTE: This is done only for non-electric demands since electric demand can
    be directly satisfied at the market bus even without prosumer's own assets.

    Args:
    -----
        prosumer: Dictionary containing prosumer details.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
    """
    prosumer_id = prosumer["id"]
    demand_carriers = {demand_data["carrier"] for demand_data in prosumer.get("demand", {}).values()}

    for demand_carrier in demand_carriers:
        if demand_carrier == "electricity":
            continue

        combined_capacity_assets_supplying_carrier = calculate_capacity_of_current_assets(prosumer, demand_carrier)
        maximum_demand_power = calculate_max_demand_for_a_given_demand_carrier(
            prosumer,
            timeseries_data,
            demand_carrier,
        )

        if combined_capacity_assets_supplying_carrier < maximum_demand_power:
            warnings.warn(
                (
                    f"Prosumer {prosumer_id} optimization problem might be infeasible: The combined capacity of assets "
                    f"supplying '{demand_carrier}' is less than the maximum demand: "
                    f"'{combined_capacity_assets_supplying_carrier}' < '{maximum_demand_power}'."
                ),
                RuntimeWarning,
            )


def calculate_capacity_of_current_assets(prosumer: dict, demand_carrier: str) -> float:
    """Calculate the combined capacity of converter assets for a given prosumer.

    The combined capacity is the sum of the product of the capacity of each
    converter asset and its efficiency.

    Args:
    -----
        prosumer: dictionary containing the prosumer's details.
        demand_carrier: carrier for which the capacity of converter assets is
            calculated.

    Returns:
    --------
        combined capacity of converter assets supplying the demand carrier.
    """
    converter_assets = {
        asset_name: asset_data
        for asset_name, asset_data in prosumer["assets"].items()
        if asset_supplies_demand_carrier(asset_data, demand_carrier) and asset_data["behavior_type"] == "converter"
    }
    combined_capacity_assets_supplying_demand_carrier = sum(
        asset_data["installed_capacity"] * get_asset_efficiency(asset_data, demand_carrier)
        for asset_data in converter_assets.values()
    )

    return combined_capacity_assets_supplying_demand_carrier


def asset_supplies_demand_carrier(asset_data: dict, demand_carrier) -> bool:
    """Check if an asset supplies a given demand carrier.

    Args:
    -----
        asset_data: Dictionary containing asset details.
        demand_carrier: Carrier for which the asset supplies power.
    """
    asset_outputs = asset_data["output"] if isinstance(asset_data["output"], list) else [asset_data["output"]]
    return demand_carrier in asset_outputs


def get_asset_efficiency(asset_data: dict, demand_carrier) -> float:
    """Get the efficiency of an asset for a given demand carrier.

    For multiple-inputs-single-output assets, simply set this value to 1.0  For
    example, a hybrid boiler has input: [methane, electricity] and output: heat.
    Although it produces heat, heat does not appear in its efficiency dict:
    {methane: 0.9, electricity: 0.9}. So, we set the efficiency to 1.0.

    Args:
    -----
        asset_data: Dictionary containing asset details.
        demand_carrier: Carrier for which the asset supplies power.

    Returns:
    --------
        Efficiency of the asset for the given demand carrier.
    """
    if isinstance(asset_data["efficiency"], dict):
        efficiency = asset_data["efficiency"].get(demand_carrier)  # None for multiple-input-single-output assets.
        return efficiency if efficiency is not None else 1.0
    return asset_data["efficiency"]


def calculate_max_demand_for_a_given_demand_carrier(
    prosumer: dict,
    timeseries_data: pd.DataFrame,
    demand_carrier: str,
) -> float:
    """Calculate the max demand of a given demand carrier of the prosumer.

    Args:
    -----
        prosumer: dictionary containing the prosumer's details.
        timeseries_data: Timeseries data containing the availability factors for
            VRE generators and EVs doing V2G, demand profiles for prosumers, ...
        demand_carrier: carrier for which the maximum demand power is calculated.

    Returns:
    --------
        Max value in the timeseries for a given demand carrier of the prosumer.
    """
    maximum_demand = 0.0
    for demand_name, demand_data in prosumer.get("demand", {}).items():  # E.g., {space_heating, {...}}
        if demand_data["carrier"] != demand_carrier:
            continue
        if "base" in demand_data:
            data = demand_data["base"]
            if "n_profile" in data:  # If there is an `n_profile` then there is a `peak` which we multiply with.
                maximum_demand += timeseries_data.loc[:, data["n_profile"]].max() * data["peak"]
            else:
                maximum_demand += data["peak"]
        if "flexible" in demand_data:
            data = demand_data["flexible"]  # {flex+1: {"peak": 1, "n_profile": "DE0 heat"}, flex+2: {"peak": 100}}
            for sub_key, sub_data in data.items():
                if "n_profile" in sub_data:
                    maximum_demand += timeseries_data.loc[:, sub_data["n_profile"]].max() * sub_data["peak"]
                else:
                    maximum_demand += sub_data["peak"]

    return maximum_demand
