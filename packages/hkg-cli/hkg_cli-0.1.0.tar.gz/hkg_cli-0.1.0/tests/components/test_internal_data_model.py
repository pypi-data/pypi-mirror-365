import pytest
from hkg_cli.components.internal_data_model.core import InternalDataModelComponent
from hkg_cli.components.internal_data_model.models import (
    InternalDataModelEnvVars,
)


@pytest.fixture
def component(temp_project_path):
    """Fixture for an InternalDataModelComponent instance."""
    return InternalDataModelComponent(project_root=temp_project_path)


def test_initialization(component):
    """Test that the component initializes with default values."""
    assert component.name == "internal-data-model"
    assert component.is_private is False
    assert component.config.repository is not None
    assert isinstance(component.config.env_vars, InternalDataModelEnvVars)


def test_docker_services_and_volumes(component):
    """Test that docker services and volumes are empty."""
    assert component.get_docker_services({}) == {}
    assert component.get_docker_volumes({}) == {}


def test_create_env_file(component):
    """Test that create_env_file does nothing."""
    try:
        component.create_env_file()
    except Exception as e:
        pytest.fail(f"create_env_file should not raise an exception, but raised {e}")
