import pandas as pd
import pytest
import yaml
from pyprojroot import here

from cronian.base_model import create_optimization_model
from cronian.configuration import load_configurations
from cronian.explicit_heat import add_explicit_heat_to_model
from cronian.generators import add_all_generators
from cronian.objective_func import set_model_objective_function
from cronian.prosumers import add_built_prosumers_to_optimization_model
from cronian.system_balance import set_system_electric_power_balance_constraint
from cronian.validate import validate_all_agents


@pytest.fixture(scope="module")
def sample_explicit_config() -> dict:
    """Yaml configuration file fixture."""
    with open(here("tests/data/demo_explicit_prosumer/explicit-heat-config-test.yaml"), "r") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="module")
def sample_generic_config() -> dict:
    """Yaml configuration file fixture."""
    configurations_folder = here("tests/data/demo_configurations")
    return load_configurations(configurations_folder)


@pytest.fixture(scope="module")
def sample_invalid_config() -> dict:
    """Invalid configuration file fixture."""
    invalid_config_folder = here("tests/data/demo_invalid_configs")
    return load_configurations(invalid_config_folder)


@pytest.fixture(scope="module")
def sample_generic_csv() -> pd.DataFrame:
    """Time series data fixture."""
    return pd.read_csv(here("tests/data/demo_csv/generic-timeseries.csv"), index_col=0)


@pytest.fixture(scope="module")
def sample_base_load(sample_generic_csv) -> pd.Series:
    """Time series data fixture."""
    return sample_generic_csv.loc[:, "BaseLoad"]


@pytest.fixture(scope="module")
def sample_price_timeseries() -> pd.DataFrame:
    """Price time series data fixture."""
    return pd.read_csv(here("tests/data/demo_csv/price-timeseries.csv"), index_col=0)


@pytest.fixture(scope="module")
def sample_explicit_csv() -> pd.DataFrame:
    """Time series data fixture."""
    return pd.read_csv(here("tests/data/demo_explicit_prosumer/explicit-heat-timeseries-test.csv"), index_col=0)


@pytest.fixture(scope="module")
def sample_datetime_index(sample_generic_csv) -> pd.DatetimeIndex:
    """Datetime index fixture."""
    return pd.date_range(start="2025-01-01 00:00:00", periods=len(sample_generic_csv), freq="h")


@pytest.fixture(scope="module")
def sample_generators(sample_generic_config) -> dict:
    """Sample generators."""
    return sample_generic_config["Generators"]


@pytest.fixture(scope="module")
def sample_prosumers(sample_generic_config) -> dict:
    """Sample prosumers."""
    all_prosumers = sample_generic_config["Prosumers"]
    selected_prosumers = ["P06", "P08"]
    sample_prosumers = {prosumer_id: all_prosumers[prosumer_id] for prosumer_id in selected_prosumers}
    return sample_prosumers


@pytest.fixture(scope="module")
def sample_invalid_prosumers(sample_invalid_config) -> dict:
    """Sample invalid prosumers."""
    prosumers = sample_invalid_config["Prosumers"]
    return prosumers


@pytest.fixture(scope="module")
def sample_model(
    sample_base_load,
    sample_generators,
    sample_prosumers,
    sample_generic_config,
    sample_explicit_config,
    sample_generic_csv,
    sample_price_timeseries,
    sample_explicit_csv,
):
    """Fixture to create the full sector-coupled optimization model."""
    num_timesteps = sample_generic_config["General"]["number_of_timesteps"]
    validate_all_agents(sample_generic_config, sample_generic_csv)
    model = create_optimization_model(sample_base_load, sample_price_timeseries, num_timesteps)
    add_all_generators(model, sample_generators, sample_generic_csv)
    add_built_prosumers_to_optimization_model(
        model, sample_prosumers, sample_generic_csv, num_timesteps, storage_model="simple",
    )
    add_explicit_heat_to_model(model, sample_explicit_config, sample_explicit_csv, num_timesteps)
    set_system_electric_power_balance_constraint(model)
    set_model_objective_function(model, sample_prosumers, sample_price_timeseries)

    return model
