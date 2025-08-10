from pathlib import Path

import pytest


@pytest.fixture
def sample_members_yaml_path():
    """Fixture to provide path to sample test members yaml."""
    return Path(__file__).parent / ".sample" / "test_members.yaml"
