import pytest
from hkg_cli.components.mapping.core import MappingComponent
from hkg_cli.components.mapping.models import MappingEnvVars


@pytest.fixture
def component(temp_project_path):
    """Fixture for a MappingComponent instance."""
    return MappingComponent(project_root=temp_project_path)


def test_initialization(component):
    """Test that the component initializes with default values."""
    assert component.name == "mapping"
    assert component.config.repository is not None
    assert isinstance(component.config.env_vars, MappingEnvVars)


def test_docker_services_and_volumes(component):
    """Test that docker services and volumes are empty."""
    assert component.get_docker_services({}) == {}
    assert component.get_docker_volumes({}) == {}


def test_create_env_file(component, temp_project_path):
    """Test the creation of the .env file for the mapping component."""
    # Execute
    component.create_env_file()

    # Assert
    expected_env_file = temp_project_path / "mapping" / ".env"
    assert expected_env_file.exists()
    content = expected_env_file.read_text()
    assert "MAX_THREADS=1" in content
    assert "STORAGE_API=http://localhost" in content
    assert "OPENSEARCH_HOST=http://localhost:9200" in content
