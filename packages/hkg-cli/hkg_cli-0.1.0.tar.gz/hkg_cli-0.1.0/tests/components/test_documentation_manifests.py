import pytest
from hkg_cli.components.documentation_manifests.core import (
    DocumentationManifestsComponent,
)
from hkg_cli.components.documentation_manifests.models import (
    DocumentationManifestsEnvVars,
)


@pytest.fixture
def component(temp_project_path):
    """Fixture for a DocumentationManifestsComponent instance."""
    return DocumentationManifestsComponent(project_root=temp_project_path)


def test_initialization(component):
    """Test that the component initializes with default values."""
    assert component.name == "documentation-manifests"
    assert component.is_private is True
    assert component.is_devops is True
    assert component.config.repository is not None
    assert isinstance(component.config.env_vars, DocumentationManifestsEnvVars)


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
