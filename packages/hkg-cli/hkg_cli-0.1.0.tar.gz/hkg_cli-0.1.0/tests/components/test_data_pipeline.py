import pytest
from hkg_cli.components.data_pipeline.core import DataPipelineComponent
from hkg_cli.components.data_pipeline.models import DataPipelineEnvVars


@pytest.fixture
def data_pipeline_component(temp_project_path):
    """Fixture for a DataPipelineComponent instance."""
    return DataPipelineComponent(project_root=temp_project_path)


def test_data_pipeline_initialization(data_pipeline_component):
    """Test that the DataPipelineComponent initializes with default values."""
    assert data_pipeline_component.name == "data-pipeline"
    assert data_pipeline_component.is_private is True
    assert data_pipeline_component.config.repository is not None
    assert isinstance(data_pipeline_component.config.env_vars, DataPipelineEnvVars)


def test_data_pipeline_docker_services_and_volumes(data_pipeline_component):
    """Test that docker services and volumes are empty."""
    assert data_pipeline_component.get_docker_services({}) == {}
    assert data_pipeline_component.get_docker_volumes({}) == {}


def test_data_pipeline_create_env_file(data_pipeline_component):
    """Test that create_env_file does nothing, as per its implementation."""
    # This test simply ensures that the method can be called without error.
    try:
        data_pipeline_component.create_env_file()
    except Exception as e:
        pytest.fail(f"create_env_file should not raise an exception, but raised {e}")
