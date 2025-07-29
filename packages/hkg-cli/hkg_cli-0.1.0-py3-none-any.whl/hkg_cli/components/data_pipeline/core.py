from hkg_cli.components.base import BaseComponent
from hkg_cli.components.models import ComponentConfig, BaseEnvVars
from typing import Dict, Any, Optional
from tomlkit import TOMLDocument
from pathlib import Path
from hkg_cli.git.models import GitRepositoryModel
from hkg_cli.components.data_pipeline.models import DataPipelineEnvVars


class DataPipelineComponent(BaseComponent):
    """Data Pipeline component."""

    name = "data-pipeline"
    is_private = True

    def __init__(
        self,
        project_root: Optional[Path] = None,
        config: Optional[ComponentConfig] = None,
    ):
        super().__init__(project_root, config)
        if self.config is None:
            self.config = ComponentConfig(
                name=self.name,
                repository=GitRepositoryModel(
                    remote_url="git@codebase.helmholtz.cloud:hmc/hmc-public/unhide/development/devops/data-pipeline.git",
                ),
                env_vars=DataPipelineEnvVars(),
            )
        else:
            self.config = config

    def get_config_section(self) -> Dict[str, Any]:
        """Get the default configuration section for this component."""
        assert isinstance(self.config.env_vars, BaseEnvVars)
        return {
            "name": self.name,
            "enabled": True,
            "env_vars": self.config.env_vars.model_dump(exclude_none=True),
        }

    def validate_config(self, config: TOMLDocument) -> None:
        """Validate the component's configuration section."""
        pass

    def get_docker_services(self, config: TOMLDocument) -> Dict:
        """Get the docker services configuration for this component."""
        return {}

    def get_docker_volumes(self, config: TOMLDocument) -> Dict:
        """Get the docker volumes configuration for this component."""
        return {}

    def create_env_file(self) -> None:
        """Create the .env file for the component."""
        pass
