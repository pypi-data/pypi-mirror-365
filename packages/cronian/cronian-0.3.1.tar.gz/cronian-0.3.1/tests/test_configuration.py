import pytest
from pyprojroot import here

from cronian.configuration import load_configurations


def test_duplicate_ids():
    """Test that duplicate IDs in a folder of configuration files are caught."""
    with pytest.raises(ValueError):
        load_configurations(here("tests/data/demo_duplicate"))


def test_reused_ids():
    """Test that a generator and prosumer reusing the same ID raises an error."""
    with pytest.raises(ValueError):
        load_configurations(here("tests/data/demo_reused"))
