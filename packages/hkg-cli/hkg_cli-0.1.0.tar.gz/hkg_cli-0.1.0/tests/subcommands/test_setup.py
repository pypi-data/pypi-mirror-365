import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import typer

from hkg_cli.subcommands.setup import (
    initialize,
    update,
    initialize_component,
    clone_component_repositories,
)
from hkg_cli.components import ProjectConfig, ComponentConfig
from hkg_cli.components.models import BaseEnvVars
from hkg_cli.git.models import GitRepositoryModel


@patch("hkg_cli.subcommands.setup.Path.exists")
@patch("hkg_cli.subcommands.setup.Path.iterdir")
@patch("hkg_cli.subcommands.setup.Path.mkdir")
@patch("hkg_cli.subcommands.setup.ComponentManager")
@patch("hkg_cli.subcommands.setup.clone_component_repositories")
@patch("hkg_cli.subcommands.setup.initialize_component")
@patch("typer.echo")
def test_initialize_success(
    mock_echo,
    mock_init_comp,
    mock_clone,
    mock_manager,
    mock_mkdir,
    mock_iterdir,
    mock_exists,
):
    """Test the 'initialize' function directly for successful initialization."""
    # Setup
    folder_name = "my-hkg-project"
    mock_exists.return_value = False  # The project directory does not exist
    mock_iterdir.return_value = iter([])  # The project directory is empty

    mock_init_comp.return_value = ComponentConfig(
        name="mock-component", env_vars=BaseEnvVars()
    )
    mock_manager_instance = MagicMock()
    mock_manager.return_value = mock_manager_instance

    # Execute
    initialize(folder_name=folder_name, private=False, devops=False)

    # Assert
    mock_mkdir.assert_called_with(parents=True, exist_ok=True)
    mock_clone.assert_called_once()
    mock_manager.assert_called_once()
    mock_manager_instance.initialize_components.assert_called_once()
    mock_manager_instance.save_config.assert_called_once()
    mock_manager_instance.save_docker_compose.assert_called_once()


@patch("hkg_cli.subcommands.setup.Path.exists")
@patch("hkg_cli.subcommands.setup.Path.iterdir")
def test_initialize_folder_exists_not_empty(mock_iterdir, mock_exists):
    """Test that 'initialize' fails if the target directory is not empty."""
    # Setup
    folder_name = "my-hkg-project"
    mock_exists.return_value = True
    mock_iterdir.return_value = iter([Path("some-file.txt")])  # Not empty

    # Execute and Assert
    with pytest.raises(typer.Exit) as excinfo:
        initialize(folder_name=folder_name, private=False, devops=False)
    assert excinfo.value.exit_code == 1


@patch("hkg_cli.subcommands.setup.Path.cwd")
@patch("hkg_cli.subcommands.setup.ComponentManager")
@patch("hkg_cli.subcommands.setup.clone_component_repositories")
def test_update_success(mock_clone, mock_manager, mock_cwd, tmp_path):
    """Test the 'update' function directly for successful execution."""
    # Setup
    project_path = tmp_path
    mock_cwd.return_value = project_path
    config_file = project_path / "hkg-config.toml"
    config_file.touch()

    mock_manager_instance = MagicMock()
    mock_manager_instance.load_config.return_value = ProjectConfig(
        components={
            "test-component": ComponentConfig(
                name="test-component", env_vars=BaseEnvVars()
            )
        }
    )
    mock_manager.return_value = mock_manager_instance

    # Execute
    update()

    # Assert
    mock_manager_instance.load_config.assert_called_once()
    mock_clone.assert_called_once()
    mock_manager_instance.save_docker_compose.assert_called_once()


@patch("hkg_cli.subcommands.setup.Path.cwd")
def test_update_no_config_file(mock_cwd, tmp_path):
    """Test that 'update' fails if no config file is found."""
    # Setup
    mock_cwd.return_value = tmp_path  # A temp directory with no config file

    # Execute and Assert
    with pytest.raises(typer.Exit) as excinfo:
        update()
    assert excinfo.value.exit_code == 1


@patch("hkg_cli.subcommands.setup.COMPONENT_CLASSES", new_callable=dict)
def test_initialize_component_with_config(mock_component_classes):
    """Test initializing a component with a provided configuration."""
    mock_component_classes["test_component"] = MagicMock()
    config = {"name": "test_component", "enabled": False, "env_vars": {}}
    result = initialize_component("test_component", Path("/fake/path"), config=config)
    assert result.name == "test_component"
    assert not result.enabled


@patch("hkg_cli.subcommands.setup.clone_and_checkout")
@patch("hkg_cli.subcommands.setup.COMPONENT_CLASSES", new_callable=dict)
def test_clone_component_repositories_general_case(mock_component_classes, mock_clone):
    """Test cloning repositories for enabled components."""
    # Setup mocks
    mock_repo = GitRepositoryModel(
        remote_url="https://example.com/repo.git",
        branch="main",
        repo_folder="repo",
    )
    mock_component_config = ComponentConfig(
        name="test_component",
        enabled=True,
        repository=mock_repo.model_dump(),
        env_vars=BaseEnvVars(),
    )
    project_config = ProjectConfig(
        components={"test_component": mock_component_config},
        private=True,
        devops=True,
    )

    mock_component_class = MagicMock()
    mock_component_instance = mock_component_class.return_value
    mock_component_instance.is_private = False
    mock_component_instance.is_devops = False
    mock_component_classes["test_component"] = mock_component_class

    # Execute
    project_path = Path("/fake/project")
    clone_component_repositories(project_config, project_path)

    # Assert
    mock_clone.assert_called_once_with(mock_repo, project_path / "repo")


@patch("hkg_cli.subcommands.setup.clone_and_checkout")
@patch("hkg_cli.subcommands.setup.COMPONENT_CLASSES", new_callable=dict)
def test_clone_component_repositories_disabled(mock_component_classes, mock_clone):
    """Test that disabled components are not cloned."""
    mock_component_config = ComponentConfig(
        name="test_component", enabled=False, env_vars=BaseEnvVars()
    )
    project_config = ProjectConfig(components={"test_component": mock_component_config})
    project_path = Path("/fake/project")

    clone_component_repositories(project_config, project_path)

    mock_clone.assert_not_called()


@patch("hkg_cli.subcommands.setup.clone_and_checkout")
@patch("hkg_cli.subcommands.setup.COMPONENT_CLASSES", new_callable=dict)
def test_clone_component_repositories_no_repo(mock_component_classes, mock_clone):
    """Test that components without repositories are not cloned."""
    mock_component_config = ComponentConfig(
        name="test_component", enabled=True, env_vars=BaseEnvVars()
    )
    project_config = ProjectConfig(components={"test_component": mock_component_config})
    project_path = Path("/fake/project")

    clone_component_repositories(project_config, project_path)

    mock_clone.assert_not_called()


@patch("hkg_cli.subcommands.setup.clone_and_checkout")
@patch("hkg_cli.subcommands.setup.COMPONENT_CLASSES", new_callable=dict)
def test_clone_component_repositories_private_skipped(
    mock_component_classes, mock_clone
):
    """Test that private repositories are skipped if private flag is not set."""
    mock_repo = GitRepositoryModel(
        remote_url="https://example.com/repo.git",
        branch="main",
        repo_folder="repo",
    )
    mock_component_config = ComponentConfig(
        name="test_component",
        enabled=True,
        repository=mock_repo.model_dump(),
        env_vars=BaseEnvVars(),
    )
    project_config = ProjectConfig(
        components={"test_component": mock_component_config}, private=False
    )

    mock_component_class = MagicMock()
    mock_component_instance = mock_component_class.return_value
    mock_component_instance.is_private = True
    mock_component_classes["test_component"] = mock_component_class

    project_path = Path("/fake/project")
    clone_component_repositories(project_config, project_path)

    mock_clone.assert_not_called()


@patch("hkg_cli.subcommands.setup.clone_and_checkout")
@patch("hkg_cli.subcommands.setup.COMPONENT_CLASSES", new_callable=dict)
def test_clone_component_repositories_devops_skipped(
    mock_component_classes, mock_clone
):
    """Test that devops repositories are skipped if devops flag is not set."""
    mock_repo = GitRepositoryModel(
        remote_url="https://example.com/repo.git",
        branch="main",
        repo_folder="repo",
    )
    mock_component_config = ComponentConfig(
        name="test_component",
        enabled=True,
        repository=mock_repo.model_dump(),
        env_vars=BaseEnvVars(),
    )
    project_config = ProjectConfig(
        components={"test_component": mock_component_config}, devops=False
    )

    mock_component_class = MagicMock()
    mock_component_instance = mock_component_class.return_value
    mock_component_instance.is_private = False
    mock_component_instance.is_devops = True
    mock_component_classes["test_component"] = mock_component_class

    project_path = Path("/fake/project")
    clone_component_repositories(project_config, project_path)

    mock_clone.assert_not_called()
