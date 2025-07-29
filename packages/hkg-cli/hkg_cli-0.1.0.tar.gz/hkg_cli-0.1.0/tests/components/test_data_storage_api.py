import pytest
from hkg_cli.components.data_storage_api.core import DataStorageAPIComponent
from hkg_cli.components.data_storage_api.models import DataStorageAPIEnvVars


@pytest.fixture
def data_storage_api_component(temp_project_path):
    """Fixture for a DataStorageAPIComponent instance."""
    # We need to create the mock schema.sql file that the component expects
    schema_path = temp_project_path / "data_storage_api" / "core" / "db" / "postgres"
    schema_path.mkdir(parents=True, exist_ok=True)
    (schema_path / "schema.sql").touch()
    return DataStorageAPIComponent(project_root=temp_project_path)


def test_data_storage_api_initialization(data_storage_api_component):
    """Test that the DataStorageAPIComponent initializes with default values."""
    assert data_storage_api_component.name == "data-storage-api"
    assert data_storage_api_component.config.repository is not None
    assert isinstance(data_storage_api_component.config.env_vars, DataStorageAPIEnvVars)


def test_get_docker_services(data_storage_api_component):
    """Test the generation of Docker services for the data-storage-api."""
    services = data_storage_api_component.get_docker_services({})

    assert "postgresql" in services
    assert "data_storage_api" in services

    # Test postgresql service
    pg_service = services["postgresql"]
    assert pg_service["image"] == "postgres:17.5"
    assert pg_service["environment"]["POSTGRES_DB"] == "hkg_data_storage"
    assert pg_service["environment"]["POSTGRES_USER"] == "hkg_data_storage"
    assert "./data_storage_api/core/db/postgres/schema.sql" in pg_service["volumes"][1]

    # Test data_storage_api service
    api_service = services["data_storage_api"]
    assert api_service["build"]["context"] == "./data_storage_api"
    assert "APP_PORT" in api_service["environment"]
    assert api_service["environment"]["APP_PORT"] == "80"
    assert "postgresql" in api_service["depends_on"]


def test_get_docker_volumes(data_storage_api_component):
    """Test the generation of Docker volumes."""
    volumes = data_storage_api_component.get_docker_volumes({})
    assert "data_storage_api_db_data" in volumes
    assert volumes["data_storage_api_db_data"]["driver"] == "local"


def test_create_env_file(data_storage_api_component, temp_project_path):
    """Test the creation of the .env file for the data-storage-api."""
    data_storage_api_component.create_env_file()

    expected_env_file = temp_project_path / "data_storage_api" / ".env"
    assert expected_env_file.exists()
    content = expected_env_file.read_text()
    assert "POSTGRES_DB=hkg_data_storage" in content
    assert "APP_PORT=80" in content


def test_get_docker_services_no_schema_file(temp_project_path):
    """Test that an error is raised if the schema.sql file is missing."""
    # Create component without the schema file
    component = DataStorageAPIComponent(project_root=temp_project_path)
    with pytest.raises(ValueError) as excinfo:
        component.get_docker_services({})
    assert "Schema file not found" in str(excinfo.value)
