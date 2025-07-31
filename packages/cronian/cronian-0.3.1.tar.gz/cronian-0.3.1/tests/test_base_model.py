import numpy as np

from cronian.base_model import create_optimization_model


def test_create_optimization_model(sample_generic_config, sample_base_load, sample_price_timeseries):
    """Tests create optimization model."""
    num_timesteps = sample_generic_config["General"]["number_of_timesteps"]
    # Test with base load
    model = create_optimization_model(sample_base_load, sample_price_timeseries, num_timesteps).create_instance()

    # Check model attributes
    assert hasattr(model, "time")
    assert hasattr(model, "methane_price")
    assert hasattr(model, "hydrogen_price")
    assert hasattr(model, "biomass_price")
    assert hasattr(model, "base_load")
    assert len(model.time) == num_timesteps

    # Check base_load parameter
    actual_base_load_values = np.array([model.base_load[t] for t in model.time])
    expected_base_load = sample_base_load.values
    assert np.allclose(actual_base_load_values, expected_base_load)
