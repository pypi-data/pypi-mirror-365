from collections import Counter
from pathlib import Path

import yaml


def load_configurations(configurations_folder: Path) -> dict:
    """Load configurations and perform basic validation check for duplicate IDs.

    Args:
    -----
        configurations_folder: Path to folder containing configuration files.

    Returns:
    --------
        configurations: Nested dictionary containing the configurations defining
            generators, prosumers, and general parameters of the simulation.

    Raises:
    -------
        ValueError: If duplicate IDs exist among generator or prosumer agents.

    Example usage:
    --------------
    from pyprojroot import here

    configurations_folder = here("tests/test_data/demo_configurations")
    configurations = load_configurations(configurations_folder)
    print(configurations["Generators"])
    print()
    print(configurations["Prosumers"])
    """
    general_config_path = configurations_folder / "general_config.yaml"
    configurations = {"General": {}, "Prosumers": {}, "Generators": {}}  # Initialize with top-level entry keys

    if not general_config_path.exists():
        raise FileNotFoundError(
            f"Missing required 'general_config.yaml' file in {configurations_folder}"
            "Please include a 'general_config.yaml' that holds general parameters like 'number_of_timesteps', etc."
        )

    # Load the general configuration file that contains general parameters such as number of timesteps, etc.
    configurations["General"] = load_general_config(general_config_path)

    listed_ids = []  # Track ids separately to check for duplicates

    # Check for subdirectories
    for subdir in configurations_folder.iterdir():
        if subdir.is_dir():
            dir_name = subdir.name.title()
            configurations[dir_name] = load_configurations_subfolder(subdir, dir_name)
            listed_ids.extend(configurations[dir_name].keys())

    # Process separate config files present in the top level folder.
    for config_file in configurations_folder.glob("*.yaml"):
        if config_file.name == "general_config.yaml":
            continue

        with config_file.open() as f:
            config_data = yaml.safe_load(f)

        if "Generators" in config_data:  # Check if `Generators` is a top-level entry key
            generator_dict = config_data["Generators"]
            generator_id = generator_dict["id"]
            configurations["Generators"][generator_id] = generator_dict
            listed_ids.append(generator_id)  # Store generator ids to keep track of duplicates

        elif "Prosumers" in config_data:  # Check if `Prosumers` is a top-level entry key
            prosumer_dict = config_data["Prosumers"]
            prosumer_id = prosumer_dict["id"]
            configurations["Prosumers"][prosumer_id] = prosumer_dict
            listed_ids.append(prosumer_id)  # Store prosumer ids to keep track of duplicates

        else:
            raise ValueError(f"Unexpected top-level key in {config_file.name}. Must be Prosumers or Generators.")

    # Run early validation to check for any duplicate ids among generator and prosumer agents
    check_duplicate_ids(listed_ids)

    print("=============== Successfully loaded configuration files 🎉🎉🎉 !!! ===============")

    return configurations


def load_general_config(general_config_path: Path) -> dict:
    """Load the general configuration file.

    Args:
    -----
        general_config_path: Path to the general configuration.

    Returns:
    --------
        general_config: The loaded general configuration.

    Raises:
    -------
        ValueError: If 'General' key is missing in general configuration file.
    """
    with general_config_path.open() as f:
        general_config = yaml.safe_load(f)

    if "General" not in general_config:  # Ensure 'General' is a top-level entry key
        raise ValueError(
            "'General' key missing in general_config.yaml. " "File must contain a 'General' top-level entry key."
        )
    return general_config["General"]


def load_configurations_subfolder(folder: Path, top_level_key: str) -> dict[str, dict]:
    """Helper function to load YAML configuration files from a subfolder.

    Args:
    -----
        folder: Path to the folder containing configuration files.
        top_level_key: Top keys in configurations: `Generators` or `Prosumers`.

    Returns:
    --------
        agent_configurations: Dict with agent id as key and config as value.

    Raises:
    -------
        ValueError: If the top-level key is missing in any of the config files
            or if any configurations share an ID.
    """
    agent_configurations = {}
    agent_ids = []  # Track ids separately to check for duplicates
    for config_file in folder.glob("*.yaml"):
        if config_file.name == "general_config.yaml":
            continue

        with config_file.open() as f:
            config_data = yaml.safe_load(f)

        if top_level_key in config_data:
            agent_dict = config_data[top_level_key]
            agent_id = agent_dict["id"]
            agent_configurations[agent_id] = agent_dict
            agent_ids.append(agent_id)
        else:
            raise ValueError(f"Unexpected top-level key in {config_file.name}. Must contain '{top_level_key}'.")

    check_duplicate_ids(agent_ids)

    return agent_configurations


def check_duplicate_ids(ids: list[str]) -> None:
    """Check for duplicate ids within generator and prosumer agents.

    Args:
    -----
        ids: List of ids listed in the configuration files.

    Raises:
    --------
        ValueError: If any duplicates are detected.
    """
    id_counts = Counter(id_ for id_ in ids)
    duplicate_ids = [id_ for id_, id_count in id_counts.items() if id_count > 1]

    if duplicate_ids:
        raise ValueError(f"Duplicate IDs found in configuration file: {duplicate_ids}")
