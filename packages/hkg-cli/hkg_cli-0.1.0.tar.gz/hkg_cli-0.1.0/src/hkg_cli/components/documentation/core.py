from hkg_cli.components.base import BaseComponent
from hkg_cli.components.models import ComponentConfig, BaseEnvVars
from typing import Dict, Any, Optional
from tomlkit import TOMLDocument
from pathlib import Path
from hkg_cli.git.models import GitRepositoryModel
from hkg_cli.components.documentation.models import DocumentationEnvVars


class DocumentationComponent(BaseComponent):
    """Documentation component."""

    name = "documentation"

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
                    remote_url="https://codebase.helmholtz.cloud/hmc/hmc-public/unhide/documentation.git",
                    branch="dev",
                ),
                env_vars=DocumentationEnvVars(server_url="http://localhost:3000"),
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
            self.config.env_vars = DocumentationEnvVars(**component_config["env_vars"])

    def get_docker_services(self, config: TOMLDocument) -> Dict:
        assert isinstance(self.config.env_vars, DocumentationEnvVars)
        env_vars = self.config.env_vars.model_dump()
        component_dir = self.name.replace("-", "_")

        # Docker environment variables must be strings
        docker_env_vars = {k: str(v) for k, v in env_vars.items() if v is not None}

        return {
            "documentation": {
                "build": {
                    "context": f"./{component_dir}",
                    "dockerfile": "Dockerfile",
                    "args": {
                        "SERVER_URL": docker_env_vars.get("server_url"),
                        "NODE_ENV": docker_env_vars.get("node_env"),
                    },
                },
                "ports": ["3000:80"],
            },
        }

    def get_docker_volumes(self, config: TOMLDocument) -> Dict:
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
