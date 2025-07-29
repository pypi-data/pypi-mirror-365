import pytest
from hkg_cli.components.documentation.core import DocumentationComponent
from hkg_cli.components.documentation.models import DocumentationEnvVars


@pytest.fixture
def component(temp_project_path):
    """Fixture for a DocumentationComponent instance."""
    return DocumentationComponent(project_root=temp_project_path)


def test_initialization(component):
    """Test that the component initializes with default values."""
    assert component.name == "documentation"
    assert component.config.repository is not None
    assert isinstance(component.config.env_vars, DocumentationEnvVars)
    assert component.config.env_vars.server_url == "http://localhost:3000"


def test_get_docker_services(component):
    """Test the generation of Docker services for the documentation."""
    services = component.get_docker_services({})
    assert "documentation" in services
    doc_service = services["documentation"]
    assert doc_service["build"]["context"] == "./documentation"
    assert "ports" in doc_service
    assert "3000:80" in doc_service["ports"]
    build_args = doc_service["build"]["args"]
    assert build_args["SERVER_URL"] == "http://localhost:3000"
    assert build_args["NODE_ENV"] == "dev"


def test_get_docker_volumes(component):
    """Test that docker volumes are empty."""
    assert component.get_docker_volumes({}) == {}


def test_create_env_file(component, temp_project_path):
    """Test the creation of the .env file for the documentation."""
    component.create_env_file()
    expected_env_file = temp_project_path / "documentation" / ".env"
    assert expected_env_file.exists()
    content = expected_env_file.read_text()
    assert "SERVER_URL=http://localhost:3000" in content
    assert "NODE_ENV=dev" in content
