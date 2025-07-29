from hkg_cli.components.base import BaseComponent
from hkg_cli.components.models import ComponentConfig, BaseEnvVars
from typing import Dict, Any, Optional
from tomlkit import TOMLDocument
from pathlib import Path
from hkg_cli.git.models import GitRepositoryModel
from hkg_cli.components.data_storage_api.models import DataStorageAPIEnvVars


class DataStorageAPIComponent(BaseComponent):
    """Data Storage API component."""

    name = "data-storage-api"

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
                    remote_url="https://gitlab.hzdr.de/hmc/hmc-public/unhide/development/data_storage_api.git",
                ),
                env_vars=DataStorageAPIEnvVars(),
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
            self.config.env_vars = DataStorageAPIEnvVars(**component_config["env_vars"])

    def get_docker_services(self, config: TOMLDocument) -> Dict:
        assert isinstance(self.config.env_vars, BaseEnvVars)
        env_vars = self.config.env_vars.model_dump()
        component_dir = self.name.replace("-", "_")

        # Docker environment variables must be strings
        docker_env_vars = {k: str(v) for k, v in env_vars.items() if v is not None}

        # Get the schema.sql path relative to the project root
        schema_path = (
            self.project_root
            / component_dir
            / "core"
            / "db"
            / "postgres"
            / "schema.sql"
        )
        if not schema_path.exists():
            raise ValueError(
                f"Schema file not found at {schema_path}. "
                "Make sure the repository is cloned correctly."
            )

        return {
            "postgresql": {
                "image": "postgres:17.5",
                "environment": {
                    "POSTGRES_DB": docker_env_vars["postgres_db"],
                    "POSTGRES_USER": docker_env_vars["postgres_user"],
                    "POSTGRES_PASSWORD": docker_env_vars["postgres_password"],
                    "PGDATA": "/var/lib/postgresql/data/pgdata",
                },
                "volumes": [
                    "data_storage_api_db_data:/var/lib/postgresql/data/pgdata",
                    f"./{component_dir}/core/db/postgres/schema.sql:/docker-entrypoint-initdb.d/init.sql",
                ],
                "ports": [f"{docker_env_vars['db_port']}:5432"],
                "healthcheck": {
                    "test": [
                        "CMD-SHELL",
                        f"pg_isready -U {docker_env_vars['postgres_user']}",
                    ],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5,
                },
            },
            "data_storage_api": {
                "build": {"context": f"./{component_dir}", "dockerfile": "Dockerfile"},
                "command": ["poetry", "run", "python", "main.py"],
                "environment": {
                    k.upper(): v
                    for k, v in docker_env_vars.items()
                    if k not in ["postgres_db", "postgres_user", "postgres_password"]
                },
                "ports": [f"{docker_env_vars['app_port']}:80"],
                "depends_on": {"postgresql": {"condition": "service_healthy"}},
            },
        }

    def get_docker_volumes(self, config: TOMLDocument) -> Dict:
        return {"data_storage_api_db_data": {"driver": "local"}}

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
