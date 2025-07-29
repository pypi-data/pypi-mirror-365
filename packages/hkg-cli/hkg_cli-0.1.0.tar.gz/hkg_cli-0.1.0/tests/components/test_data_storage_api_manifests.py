import pytest
from hkg_cli.components.data_storage_api_manifests.core import (
    DataStorageApiManifestsComponent,
)
from hkg_cli.components.data_storage_api_manifests.models import (
    DataStorageApiManifestsEnvVars,
)


@pytest.fixture
def component(temp_project_path):
    """Fixture for a DataStorageApiManifestsComponent instance."""
    return DataStorageApiManifestsComponent(project_root=temp_project_path)


def test_initialization(component):
    """Test that the component initializes with default values."""
    assert component.name == "data-storage-api-manifests"
    assert component.is_private is True
    assert component.is_devops is True
    assert component.config.repository is not None
    assert isinstance(component.config.env_vars, DataStorageApiManifestsEnvVars)


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
