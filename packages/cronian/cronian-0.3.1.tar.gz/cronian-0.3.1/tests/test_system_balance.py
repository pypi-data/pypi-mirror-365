import numpy as np


def test_set_system_electric_power_constraint(sample_model, sample_base_load):
    """Test that system electric power balance constraint exist, and that the rhs is added correctly."""
    model_instance = sample_model.create_instance()

    assert hasattr(model_instance, "system_electric_power_balance_constraint")

    expected_rhs = sample_base_load.values
    actual_rhs = np.array(
        [model_instance.system_electric_power_balance_constraint[t].expr.args[1] for t in model_instance.time]
    )

    assert np.allclose(actual_rhs, expected_rhs)
