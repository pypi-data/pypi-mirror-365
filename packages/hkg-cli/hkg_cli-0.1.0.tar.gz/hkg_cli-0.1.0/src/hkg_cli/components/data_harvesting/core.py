from hkg_cli.components.base import BaseComponent
from hkg_cli.components.models import ComponentConfig, BaseEnvVars
from typing import Dict, Any, Optional
from tomlkit import TOMLDocument
from pathlib import Path
from hkg_cli.git.models import GitRepositoryModel
from hkg_cli.components.data_harvesting.models import DataHarvestingEnvVars


class DataHarvestingComponent(BaseComponent):
    """Data Harvesting component."""

    name = "data-harvesting"

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
                    remote_url="https://codebase.helmholtz.cloud/hmc/hmc-public/unhide/development/data_harvesting.git",
                ),
                env_vars=DataHarvestingEnvVars(),
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
        if "components" not in config:
            raise ValueError("No components section found in config")

        component_key = self.name
        if component_key not in config.get("components", {}):
            raise ValueError(f"No {component_key} component found in config")

        component_config = config["components"][component_key]
        if "env_vars" in component_config:
            self.config.env_vars = DataHarvestingEnvVars(**component_config["env_vars"])

    def get_docker_services(self, config: TOMLDocument) -> Dict:
        """Get the docker services configuration for this component."""
        return {}

    def get_docker_volumes(self, config: TOMLDocument) -> Dict:
        """Get the docker volumes configuration for this component."""
        return {}

    def create_env_file(self) -> None:
        """Create the .env file for the component."""
        assert isinstance(self.config.env_vars, BaseEnvVars)
        if self.config.env_vars:
            env_content = self.config.env_vars.to_env_file()
            component_dir = self.name.replace("-", "_")
            env_file_path = self.project_root / component_dir / ".env"
            env_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(env_file_path, "w") as f:
                f.write(env_content)
