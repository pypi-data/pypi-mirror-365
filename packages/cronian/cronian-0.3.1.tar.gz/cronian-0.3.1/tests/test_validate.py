import pytest

import cronian.validate as validate_module


def test_validate_all_agents(sample_invalid_config, sample_generic_csv):
    """Test that all agents have valid ids."""
    prosumers = sample_invalid_config["Prosumers"]

    # G01 has an invalid id (currently has id "P01").
    valid_prosumer = {"P13": prosumers["P13"]}
    configs = {"Generators": sample_invalid_config["Generators"], "Prosumers": valid_prosumer}
    with pytest.raises(ValueError, match="Generator ID .*must start with 'g'"):
        validate_module.validate_all_agents(configs, sample_generic_csv)

    # P14 has an invalid id (currently has id "G14")
    valid_generator = {"G02": sample_invalid_config["Generators"]["G02"]}
    configs = {"Generators": valid_generator, "Prosumers": prosumers}
    with pytest.raises(ValueError, match="Prosumer ID .*must start with 'p' or 'b'"):
        validate_module.validate_all_agents(configs, sample_generic_csv)


def test_missing_required_keys(sample_invalid_prosumers):
    """Test that missing required keys are caught."""
    # P01 is missing the required `demand` key under demand.
    with pytest.raises(ValueError, match="is missing the following keys: .* Please provide them"):
        validate_module.validate_required_entries(sample_invalid_prosumers["P01"], "P01")

    # P03 is missing the required `carrier` key under demand.
    with pytest.raises(ValueError, match="is missing the 'carrier' key. .*Please provide the carrier for this demand."):
        validate_module.validate_required_entries(sample_invalid_prosumers["P03"], "P03")

    # P05 is missing non-required asset keys: validation should pass since they are not required.
    validate_module.validate_required_entries(sample_invalid_prosumers["P05"], "P05")


def test_empty_fields(sample_invalid_prosumers):
    """Test that empty fields are caught."""
    # P01 has an empty assets[refrigerator][efficiency] field.
    with pytest.raises(ValueError, match="Invalid val .*Check for None, empty str, or bool"):
        validate_module.validate_fields(sample_invalid_prosumers["P01"], "P01")

    # P02 has an empty demand[cooling][carrier][flexible] field.
    with pytest.raises(ValueError, match="Invalid val .*Check for None, empty str, or bool"):
        validate_module.validate_fields(sample_invalid_prosumers["P02"], "P02")

    # P03 has empty field for non-required keys: validation does not allow any empty values.
    with pytest.raises(ValueError, match="Invalid val .*Check for None, empty str, or bool"):
        validate_module.validate_fields(sample_invalid_prosumers["P03"], "P03")


def test_validate_asset_outputs(sample_invalid_prosumers):
    """Ensure set of asset outputs is a subset of {prosumer[d][carrier] for d in prosumer[demand]} + {electricity}."""
    # P02 electrolyzer produces hydrogen, which is not valid since it does not have a demand for it.
    with pytest.raises(ValueError, match=".*Expected outputs to match demand carriers"):
        validate_module.validate_asset_outputs(sample_invalid_prosumers["P02"], "P02")

    # P05 has no assets: validation should pass since there are no outputs to check.
    validate_module.validate_asset_outputs(sample_invalid_prosumers["P05"], "P05")


def test_validate_assets_input_output_efficiency_relationship(sample_invalid_prosumers):
    """Test the validation function with various asset configurations."""
    # P06 e_boiler (single-input-single-output asset) efficiency should be a float or int.
    with pytest.raises(ValueError, match="Expected a single efficiency value for a single input and single output"):
        validate_module.validate_assets_input_output_efficiency_relationship(sample_invalid_prosumers["P06"], "P06")

    # P07 hybrid_boiler (multiple-inputs(methane and electricity)-single-output) efficiency is a float and not a dict.
    with pytest.raises(ValueError, match="Expected a dictionary of efficiencies for each input"):
        validate_module.validate_assets_input_output_efficiency_relationship(sample_invalid_prosumers["P07"], "P07")

    # P08 fuel_cell (single-input-multiple-output) produces electricity and heat, but is missing efficiency for heat.
    with pytest.raises(ValueError, match="with missing efficiency: .*Expected efficiency keys to match asset_outputs"):
        validate_module.validate_assets_input_output_efficiency_relationship(sample_invalid_prosumers["P08"], "P08")

    # P09 hybrid_boiler (multiple-inputs(methane and electricity)-single-output) is missing efficiency for electricity.
    with pytest.raises(ValueError, match="with missing efficiency: .*Expected efficiency keys to match asset_inputs"):
        validate_module.validate_assets_input_output_efficiency_relationship(sample_invalid_prosumers["P09"], "P09")

    # P10 sabatier_reactor (multiple-inputs-multiple-outputs) is not yet supported (implemented).
    with pytest.raises(NotImplementedError, match="has asset unsupported .* with multiple inputs and outputs"):
        validate_module.validate_assets_input_output_efficiency_relationship(sample_invalid_prosumers["P10"], "P10")

    # P11 heat storage asset has inconsistent input and output.
    with pytest.raises(ValueError, match=".*Expected a 'single' consistent input and output for storage."):
        validate_module.validate_assets_input_output_efficiency_relationship(sample_invalid_prosumers["P11"], "P11")


def test_validate_asset_behavior(sample_invalid_prosumers):
    """Test that asset `behavior_type` key is present and valid."""
    # P01 electrolyzer is missing the required `behavior_type` key.
    with pytest.raises(ValueError, match=".*with no/invalid behavior_type. Please specify one of the following .*"):
        validate_module.validate_asset_behavior(sample_invalid_prosumers["P01"], "P01")

    # P02 freezer has an invalid behavior_type.
    with pytest.raises(ValueError, match=".*with no/invalid behavior_type. Please specify one of the following .*"):
        validate_module.validate_asset_behavior(sample_invalid_prosumers["P02"], "P02")


def test_validate_asset_behavior_attributes(sample_invalid_prosumers):
    """Test that an asset with a valid behavior_type has all required attributes for that behavior."""
    # P03 freezer which is a converter is missing the required `input` attribute.
    with pytest.raises(ValueError, match=".*has converter asset .*with missing behavior attributes"):
        validate_module.validate_asset_behavior_attributes(sample_invalid_prosumers["P03"], "P03")

    # P04 wind_turbine is missing the required `availability_factor` attribute.
    with pytest.raises(ValueError, match=".*has generator asset .*with missing behavior attributes"):
        validate_module.validate_asset_behavior_attributes(sample_invalid_prosumers["P04"], "P04")

    # P06 heat_storage is missing the required `charge_efficiency` attribute.
    with pytest.raises(ValueError, match=".*has storage asset .*with missing behavior attributes"):
        validate_module.validate_asset_behavior_attributes(sample_invalid_prosumers["P06"], "P06")


def test_validate_base_or_flexible_demand(sample_invalid_prosumers):
    """Test that for non-battery prosumers, there is at least a base or flexible demand."""
    # P03 lacks both base and flexible demand.
    with pytest.raises(ValueError, match=".*is missing 'base' or 'flexible' demand .*"):
        validate_module.validate_base_or_flexible_demand(sample_invalid_prosumers["P04"], "P04")


def test_validate_satisfiable_demand(sample_invalid_prosumers):
    """Test that each listed demand can be satisfied by at least one asset."""
    # P06 has cooling demand but none of its assets produces cooling: its demand is not satisfiable.
    with pytest.raises(ValueError, match=".*has no asset to satisfy the demands.*"):
        validate_module.validate_satisfiable_demand(sample_invalid_prosumers["P06"], "P06", demand_carriers={"cooling"})


def test_validate_battery_operator_assets(sample_invalid_prosumers):
    """Test that all assets of a battery operator/service provider (with no demand) have electricity as output."""
    # B01 has an asset whose output is not electricity (gas boiler).
    message = ".*All assets of a battery operator/service provider must have at least 'electricity' as output."
    with pytest.raises(ValueError, match=message):
        validate_module.validate_battery_operator_assets(sample_invalid_prosumers["B01"])


def test_validate_prosumer_relevance(sample_invalid_prosumers):
    """Test that a prosumer with no electric demand or electric asset is not allowed in the simulation."""
    # P12 has no electric demand or electric asset.
    with pytest.raises(ValueError, match="irrelevant to the simulation: it has no electric demand or electric asset."):
        validate_module.validate_prosumer_relevance(sample_invalid_prosumers["P12"], "P12")

    # P13 has no electric demand but has an electric asset (e_boiler). So, test should pass.
    validate_module.validate_prosumer_relevance(sample_invalid_prosumers["P13"], "P13")

    valid_prosumer = {
        "name": "heat prosumer",
        "id": "B0002",
        "assets": {
            "CHP": {
                "behavior_type": "converter",
                "input": "methane",
                "output": ["electricity", "heat"],
                "installed_capacity": 57958,
                "efficiency": {"heat": 0.4, "electricity": 0.1},
            }
        },
    }

    # B0002 has no electric demand but has an electric asset (CHP). So, test should pass.
    validate_module.validate_prosumer_relevance(valid_prosumer, "B0002")


def test_infeasible_prosumer(sample_invalid_prosumers, sample_generic_csv):
    """Test that a RuntimeWarning is raised for a prosumer with a potential infeasible optimization problem."""
    # P15 has cooling demand with max value greater than the installed capacity of its refrigerator asset.
    message = "The combined capacity of assets supplying 'cold' is less than the maximum demand"
    with pytest.warns(RuntimeWarning, match=f".*optimization problem might be infeasible.*{message}"):
        validate_module.validate_prosumer_potential_feasibility(sample_invalid_prosumers["P15"], sample_generic_csv)
