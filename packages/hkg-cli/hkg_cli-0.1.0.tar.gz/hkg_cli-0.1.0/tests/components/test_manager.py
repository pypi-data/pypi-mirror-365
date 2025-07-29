from hkg_cli.components.manager import (
    ComponentManager,
    ENV_VARS_MODELS,
)
from hkg_cli.components.models import ProjectConfig, BaseEnvVars
from unittest.mock import patch


def test_save_and_load_config(mock_project_config, temp_project_path):
    """
    Test saving a ProjectConfig to a TOML file and loading it back.
    """
    # 1. Setup the ComponentManager
    manager = ComponentManager(
        config=mock_project_config, project_root=temp_project_path
    )
    manager.config_file = temp_project_path / "hkg-config.toml"

    # 2. Save the configuration
    manager.save_config()

    # 3. Verify the file was created and has content
    assert manager.config_file.exists()
    content = manager.config_file.read_text()
    assert "[components.test-component]" in content
    assert 'remote_url = "https://github.com/test/repo.git"' in content

    # 4. Load the configuration back using a new manager instance
    # We need to patch the manager's lookups to include our mock component
    with patch.dict(ENV_VARS_MODELS, {"test-component": BaseEnvVars}):
        new_manager = ComponentManager(
            config=ProjectConfig(), project_root=temp_project_path
        )
        loaded_config = new_manager.load_config()

    # 5. Assert that the loaded config matches the original
    assert loaded_config.private is False
    assert "test-component" in loaded_config.components
    component = loaded_config.components["test-component"]
    assert component.enabled is True
    assert component.repository.branch == "main"
    assert str(component.repository.remote_url) == "https://github.com/test/repo.git"


def test_generate_docker_compose(mock_project_config, temp_project_path):
    """
    Test the generation of the docker-compose dictionary.
    """
    # Setup the manager and initialize a mock component
    manager = ComponentManager(
        config=mock_project_config, project_root=temp_project_path
    )

    # We need to manually add a mock component to the manager's components dict
    # to simulate that initialize_components has run.
    from unittest.mock import MagicMock

    mock_component = MagicMock()
    mock_component.get_docker_services.return_value = {
        "test-service": {"image": "test-image"}
    }
    mock_component.get_docker_volumes.return_value = {"test-volume": None}
    manager.components["test-component"] = mock_component

    # Generate the docker-compose config
    compose_config = manager.generate_docker_compose()

    # Assert that the base services are present
    assert "hkg-opensearch-node-1" in compose_config["services"]
    assert "opensearch-data1" in compose_config["volumes"]

    # Assert that the services and volumes from our mock component are included
    assert "test-service" in compose_config["services"]
    assert "test-volume" in compose_config["volumes"]
    mock_component.get_docker_services.assert_called_once()
    mock_component.get_docker_volumes.assert_called_once()
