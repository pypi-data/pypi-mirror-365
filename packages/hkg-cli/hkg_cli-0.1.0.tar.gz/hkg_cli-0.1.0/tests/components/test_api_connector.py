import pytest
from hkg_cli.components.api_connector.core import ApiConnectorComponent
from hkg_cli.components.api_connector.models import ApiConnectorEnvVars


@pytest.fixture
def api_connector_component(temp_project_path):
    """Fixture for an ApiConnectorComponent instance."""
    return ApiConnectorComponent(project_root=temp_project_path)


def test_api_connector_initialization(api_connector_component):
    """Test that the ApiConnectorComponent initializes with default values."""
    assert api_connector_component.name == "api-connector"
    assert api_connector_component.config.repository is not None
    assert isinstance(api_connector_component.config.env_vars, ApiConnectorEnvVars)


def test_api_connector_docker_services_and_volumes(api_connector_component):
    """Test that docker services and volumes are empty."""
    assert api_connector_component.get_docker_services({}) == {}
    assert api_connector_component.get_docker_volumes({}) == {}


def test_api_connector_create_env_file(api_connector_component, temp_project_path):
    """Test the creation of the .env file for the api-connector."""
    # Execute
    api_connector_component.create_env_file()

    # Assert
    expected_env_file = temp_project_path / "apiconnector" / ".env"
    assert expected_env_file.exists()
    content = expected_env_file.read_text()
    assert "DEBUG=False" in content
    assert "STORAGE_API_URL=http://localhost" in content
    assert "API_MAX_RETRIES=1" in content
