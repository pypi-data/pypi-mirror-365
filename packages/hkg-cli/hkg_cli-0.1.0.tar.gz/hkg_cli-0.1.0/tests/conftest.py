"""Global pytest configuration."""

import pytest
from pathlib import Path
from hkg_cli.components.models import ProjectConfig, ComponentConfig, BaseEnvVars
from hkg_cli.git.models import GitRepositoryModel


@pytest.fixture
def mock_project_config() -> ProjectConfig:
    """Returns a mock ProjectConfig object for testing."""
    return ProjectConfig(
        components={
            "test-component": ComponentConfig(
                enabled=True,
                name="test-component",
                env_vars=BaseEnvVars(),
                repository=GitRepositoryModel(
                    remote_url="https://github.com/test/repo.git",
                    branch="main",
                ),
            )
        },
        private=False,
        devops=False,
    )


@pytest.fixture
def temp_project_path(tmp_path: Path) -> Path:
    """Creates a temporary project directory and returns its path."""
    project_path = tmp_path / "my-hkg-project"
    project_path.mkdir()
    return project_path
