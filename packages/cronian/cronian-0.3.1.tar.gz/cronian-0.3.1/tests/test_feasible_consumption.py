import numpy as np
import pandas as pd
import pytest

from cronian.feasible_consumption import calculate_flex_store_bounds, parse_flex_amount


@pytest.fixture(scope="module")
def sample_prosumers(sample_generic_config) -> tuple[dict, dict]:
    """Sample generators."""
    prosumers = sample_generic_config["Prosumers"]
    return prosumers["P01"], prosumers["P02"]


@pytest.fixture(scope="module")
def p01_store_dicts(sample_generic_csv, sample_prosumers) -> tuple[dict, dict, dict]:
    """Prosumer 01 store dictionary fixture."""
    prosumer01, _ = sample_prosumers

    flex_load_names = prosumer01["demand"]["space_heating"]["flexible"]
    store_e_min, store_e_max, store_e_nom = extract_store_bounds(flex_load_names, sample_generic_csv)
    return store_e_min, store_e_max, store_e_nom


@pytest.fixture(scope="module")
def p02_store_dicts(sample_generic_csv, sample_prosumers) -> tuple[dict, dict, dict]:
    """Prosumer 02 store dictionary fixture."""
    _, prosumer02 = sample_prosumers

    flex_loads = prosumer02["demand"]["hot_water"]["flexible"]
    store_e_min, store_e_max, store_e_nom = extract_store_bounds(flex_loads, sample_generic_csv)
    return store_e_min, store_e_max, store_e_nom


def extract_store_bounds(flexible_loads: dict, time_series_data: pd.DataFrame):
    """Extract the e_min, e_max and e_nom per store for given flexible demand."""
    store_e_min, store_e_max, store_e_nom = {}, {}, {}

    for fd, fd_data in flexible_loads.items():
        if not fd_data:
            continue
        nprofile_name_in_csv = flexible_loads[fd].get("n_profile")
        peak_flex_demand = flexible_loads[fd]["peak"]
        if nprofile_name_in_csv is not None:
            fd_profile = peak_flex_demand * time_series_data.loc[:, nprofile_name_in_csv].values
        else:
            fd_profile = np.full(len(time_series_data), peak_flex_demand)
        e_min, e_max = calculate_flex_store_bounds(fd, fd_profile)
        store_e_min[fd] = e_min
        store_e_max[fd] = e_max

        store_e_nom[fd] = np.sum(fd_profile, axis=0)

    return store_e_min, store_e_max, store_e_nom


def test_flex_store_bounds(p01_store_dicts):
    """Test that certain flexibility results in certain store bounds."""
    store_e_min, store_e_max, _ = p01_store_dicts
    expected = np.array(
        [
            160.0835,
            357.7070,
            439.7070,
            491.7905,
            556.7070,
            594.8570,
            645.1070,
            710.0235,
            756.6735,
            831.4235,
            908.3400,
            1097.7185,
            1336.1250,
            1666.6175,
            2043.5970,
            2320.2350,
            3232.0790,
            3456.7525,
            4297.0055,
            4711.7605,
            5116.9835,
            5472.7020,
            5981.9235,
            6335.7115,
        ]
    )
    assert np.allclose(store_e_min["flex+2"], expected)
    assert np.allclose(store_e_max["flex+2"][:-2], expected[2:])
    assert len(set(store_e_max["flex+2"][-3:])) == 1  # last elements are equal


def test_length_of_array(p01_store_dicts, p02_store_dicts, sample_generic_csv):
    """Test the length of e_min and e_max matches the length of timesteps in the data timeseries."""
    P01_e_min_dict, P01_e_max_dict, _ = p01_store_dicts
    P02_e_min_dict, P02_e_max_dict, _ = p02_store_dicts

    # Prosumer01's first flexible load (space_heating: flex+2)
    P01_e_min_1, P01_e_max_1 = P01_e_min_dict["flex+2"], P01_e_max_dict["flex+2"]

    assert len(P01_e_min_1) == len(P01_e_max_1) == len(sample_generic_csv)

    # Prosumer01's second flexible load (space_heating: flex+3)
    P01_e_min_2, P01_e_max_2 = P01_e_min_dict["flex+3"], P01_e_max_dict["flex+3"]

    assert len(P01_e_min_2) == len(P01_e_max_2) == len(sample_generic_csv)

    # Prosumer02's first flexible load (hot_water: flex+2)
    P02_e_min_1, P02_e_max_1 = P02_e_min_dict["flex+2"], P02_e_max_dict["flex+2"]

    assert len(P02_e_min_1) == len(P02_e_max_1) == len(sample_generic_csv)

    # Prosumer02's second flexible load (hot_water: flex+3)
    P02_e_min_2, P02_e_max_2 = P02_e_min_dict["flex+3"], P02_e_max_dict["flex+3"]

    assert len(P02_e_min_2) == len(P02_e_max_2) == len(sample_generic_csv)


def test_min_max_relationship(p01_store_dicts, p02_store_dicts):
    """Test that e_min is always <= e_max, and that their final values are always equal."""
    P01_e_min_dict, P01_e_max_dict, _ = p01_store_dicts
    P02_e_min_dict, P02_e_max_dict, _ = p02_store_dicts

    # Prosumer01's first flexible load (space_heating: flex+2)
    P01_e_min_1, P01_e_max_1 = P01_e_min_dict["flex+2"], P01_e_max_dict["flex+2"]

    assert np.all(np.round(P01_e_min_1, 5) <= np.round(P01_e_max_1, 5))
    assert P01_e_min_1[-1] == pytest.approx(P01_e_max_1[-1])

    # Prosumer01's second flexible load (space_heating: flex+3)
    P01_e_min_2, P01_e_max_2 = P01_e_min_dict["flex+3"], P01_e_max_dict["flex+3"]

    assert np.all(np.round(P01_e_min_2, 5) <= np.round(P01_e_max_2, 5))
    assert P01_e_min_2[-1] == pytest.approx(P01_e_max_2[-1])

    # Prosumer02's first flexible load (hot_water: flex+2)
    P02_e_min_1, P02_e_max_1 = P02_e_min_dict["flex+2"], P02_e_max_dict["flex+2"]

    assert np.all(np.round(P02_e_min_1, 5) <= np.round(P02_e_max_1, 5))
    assert P02_e_min_1[-1] == pytest.approx(P02_e_max_1[-1])

    # Prosumer02's second flexible load (hot_water: flex+3)
    P02_e_min_2, P02_e_max_2 = P02_e_min_dict["flex+3"], P02_e_max_dict["flex+3"]

    assert np.all(np.round(P02_e_min_2, 5) <= np.round(P02_e_max_2, 5))
    assert P02_e_min_2[-1] == pytest.approx(P02_e_max_2[-1])


def test_e_min_pu_e_max_pu(p01_store_dicts, p02_store_dicts):
    """Test that the normalized values of e_min and e_max (w.r.t e_nom) are within 0 and 1."""
    P01_e_min_dict, P01_e_max_dict, P01_e_nom_dict = p01_store_dicts
    P02_e_min_dict, P02_e_max_dict, P02_e_nom_dict = p02_store_dicts

    # Prosumer01's flexible load (flex+2)
    P01_e_min_1 = P01_e_min_dict["flex+2"]
    P01_e_max_1 = P01_e_max_dict["flex+2"]
    P01_e_nom_1 = P01_e_nom_dict["flex+2"]

    P01_e_min_pu_1, P01_e_max_pu_1 = P01_e_min_1 / P01_e_nom_1, P01_e_max_1 / P01_e_nom_1

    assert np.all((np.round(P01_e_min_pu_1, 1) >= 0.0) & (np.round(P01_e_min_pu_1, 1) <= 1.0))
    assert np.all((np.round(P01_e_max_pu_1, 1) >= 0.0) & (np.round(P01_e_max_pu_1, 1) <= 1.0))

    # Prosumer01's second flexible load (flex+3)
    P01_e_min_2 = P01_e_min_dict["flex+3"]
    P01_e_max_2 = P01_e_max_dict["flex+3"]
    P01_e_nom_2 = P01_e_nom_dict["flex+3"]

    P01_e_min_pu_2, P01_e_max_pu_2 = P01_e_min_2 / P01_e_nom_2, P01_e_max_2 / P01_e_nom_2

    assert np.all((np.round(P01_e_min_pu_2, 1) >= 0.0) & (np.round(P01_e_min_pu_2, 1) <= 1.0))
    assert np.all((np.round(P01_e_max_pu_2, 1) >= 0.0) & (np.round(P01_e_max_pu_2, 1) <= 1.0))

    # Prosumer02's first flexible load (flex+2)
    P02_e_min_1 = P02_e_min_dict["flex+2"]
    P02_e_max_1 = P02_e_max_dict["flex+2"]
    P02_e_nom_1 = P02_e_nom_dict["flex+2"]

    P02_e_min_pu_1, P02_e_max_pu_1 = P02_e_min_1 / P02_e_nom_1, P02_e_max_1 / P02_e_nom_1

    assert np.all((np.round(P02_e_min_pu_1, 1) >= 0.0) & (np.round(P02_e_min_pu_1, 1) <= 1.0))
    assert np.all((np.round(P02_e_max_pu_1, 1) >= 0.0) & (np.round(P02_e_max_pu_1, 1) <= 1.0))

    # Prosumer02's second flexible load (flex+3)
    P02_e_min_2 = P02_e_min_dict["flex+3"]
    P02_e_max_2 = P02_e_max_dict["flex+3"]
    P02_e_nom_2 = P02_e_nom_dict["flex+3"]

    P02_e_min_pu_2, P02_e_max_pu_2 = P02_e_min_2 / P02_e_nom_2, P02_e_max_2 / P02_e_nom_2

    assert np.all((np.round(P02_e_min_pu_2, 1) >= 0.0) & (np.round(P02_e_min_pu_2, 1) <= 1.0))
    assert np.all((np.round(P02_e_max_pu_2, 1) >= 0.0) & (np.round(P02_e_max_pu_2, 1) <= 1.0))


@pytest.mark.parametrize(
    ("name", "n"),
    (
        ("flex+1", 1),
        ("flex+002", 2),
        ("flex+3.25", 3),
        ("demo_flex+4", 4),
        ("flex+5_demo", 5),
        ("demo_flex+6-demo", 6),
    ),
)
def test_parse_flex_amount(name: str, n: int):
    """Test parsing the amount of flexibility from a column name."""
    assert parse_flex_amount(name) == n


def test_parse_flex_amount_exception():
    """Check the correct error is raised on invalid input."""
    with pytest.raises(ValueError):
        parse_flex_amount("some_string_without_flex_amount")
