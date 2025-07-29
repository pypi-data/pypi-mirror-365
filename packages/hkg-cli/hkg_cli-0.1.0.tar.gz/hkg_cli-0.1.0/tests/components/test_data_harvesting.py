import pytest
from hkg_cli.components.data_harvesting.core import DataHarvestingComponent
from hkg_cli.components.data_harvesting.models import DataHarvestingEnvVars


@pytest.fixture
def data_harvesting_component(temp_project_path):
    """Fixture for a DataHarvestingComponent instance."""
    return DataHarvestingComponent(project_root=temp_project_path)


def test_data_harvesting_initialization(data_harvesting_component):
    """Test that the DataHarvestingComponent initializes with default values."""
    assert data_harvesting_component.name == "data-harvesting"
    assert data_harvesting_component.config.repository is not None
    assert isinstance(data_harvesting_component.config.env_vars, DataHarvestingEnvVars)


def test_data_harvesting_docker_services_and_volumes(data_harvesting_component):
    """Test that docker services and volumes are empty."""
    assert data_harvesting_component.get_docker_services({}) == {}
    assert data_harvesting_component.get_docker_volumes({}) == {}


def test_data_harvesting_create_env_file(data_harvesting_component, temp_project_path):
    """Test the creation of the .env file for the data-harvesting component."""
    # Execute
    data_harvesting_component.create_env_file()

    # Assert
    expected_env_file = temp_project_path / "data_harvesting" / ".env"
    assert expected_env_file.exists()
    content = expected_env_file.read_text()
    assert "DEBUG=False" in content
    assert "STORAGE_API=http://localhost/api/v1/raw/entities" in content
    assert "MAX_RETRIES_API=2" in content
