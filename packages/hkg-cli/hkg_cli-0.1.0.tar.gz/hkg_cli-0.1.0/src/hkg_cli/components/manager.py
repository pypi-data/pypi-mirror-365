"""Component manager for handling project components."""

from pathlib import Path
from typing import Dict, Type
import yaml
import tomlkit
from hkg_cli.components.base import BaseComponent
from hkg_cli.components.data_storage_api import DataStorageAPIComponent
from hkg_cli.components.data_harvesting import DataHarvestingComponent
from hkg_cli.components.models import ProjectConfig, BaseEnvVars
from hkg_cli.components.data_storage_api.models import DataStorageAPIEnvVars
from hkg_cli.components.data_harvesting.models import DataHarvestingEnvVars
from hkg_cli.components.api_connector import ApiConnectorComponent
from hkg_cli.components.documentation import DocumentationComponent
from hkg_cli.components.api_connector.models import ApiConnectorEnvVars
from hkg_cli.components.documentation.models import DocumentationEnvVars
from hkg_cli.components.mapping import MappingComponent
from hkg_cli.components.mapping.models import MappingEnvVars
from hkg_cli.components.data_pipeline import DataPipelineComponent
from hkg_cli.components.data_pipeline.models import DataPipelineEnvVars
from hkg_cli.components.data_storage_api_manifests import (
    DataStorageApiManifestsComponent,
)
from hkg_cli.components.data_storage_api_manifests.models import (
    DataStorageApiManifestsEnvVars,
)
from hkg_cli.components.documentation_manifests import DocumentationManifestsComponent
from hkg_cli.components.documentation_manifests.models import (
    DocumentationManifestsEnvVars,
)
from hkg_cli.components.internal_data_model import InternalDataModelComponent
from hkg_cli.components.internal_data_model.models import InternalDataModelEnvVars


COMPONENT_CLASSES: Dict[str, Type[BaseComponent]] = {
    "data-storage-api": DataStorageAPIComponent,
    "data-harvesting": DataHarvestingComponent,
    "apiconnector": ApiConnectorComponent,
    "documentation": DocumentationComponent,
    "mapping": MappingComponent,
    "data-pipeline": DataPipelineComponent,
    "data-storage-api-manifests": DataStorageApiManifestsComponent,
    "documentation-manifests": DocumentationManifestsComponent,
    "internal-data-model": InternalDataModelComponent,
}

ENV_VARS_MODELS: Dict[str, Type[BaseEnvVars]] = {
    "data-storage-api": DataStorageAPIEnvVars,
    "data-harvesting": DataHarvestingEnvVars,
    "apiconnector": ApiConnectorEnvVars,
    "documentation": DocumentationEnvVars,
    "mapping": MappingEnvVars,
    "data-pipeline": DataPipelineEnvVars,
    "data-storage-api-manifests": DataStorageApiManifestsEnvVars,
    "documentation-manifests": DocumentationManifestsEnvVars,
    "internal-data-model": InternalDataModelEnvVars,
}


class ComponentManager:
    """Manager for HKG components."""

    _component_classes: Dict[str, Type[BaseComponent]] = COMPONENT_CLASSES
    _env_vars_models: Dict[str, Type[BaseEnvVars]] = ENV_VARS_MODELS

    def __init__(
        self,
        config: ProjectConfig,
        project_root: Path,
    ):
        self.config = config
        self.project_root = project_root
        self.components: Dict[str, BaseComponent] = {}
        self.config_file = project_root / "hkg-config.toml"

    def initialize_components(self):
        """Initialize all enabled components."""
        for name, component_config in self.config.components.items():
            if component_config.enabled and name in self._component_classes:
                component_class = self._component_classes[name]
                component_instance = component_class()
                if component_instance.is_private and not self.config.private:
                    continue
                if component_instance.is_devops and not self.config.devops:
                    continue

                component = component_class(
                    project_root=self.project_root, config=component_config
                )
                self.components[name] = component
                component.create_env_file()

    def generate_docker_compose(self) -> Dict:
        """Generate docker-compose configuration from all components."""
        services = {
            "hkg-opensearch-node-1": {
                "image": "opensearchproject/opensearch:2.11.1",
                "container_name": "hkg-opensearch-node-1",
                "environment": [
                    "cluster.name=opensearch-cluster",
                    "node.name=hkg-opensearch-node-1",
                    "discovery.seed_hosts=hkg-opensearch-node-1,hkg-opensearch-node-2",
                    "cluster.initial_cluster_manager_nodes=hkg-opensearch-node-1,hkg-opensearch-node-2",
                    "bootstrap.memory_lock=true",
                    "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m",
                    "OPENSEARCH_INITIAL_ADMIN_PASSWORD=admin",
                    "plugins.security.ssl.http.enabled=false",
                    "plugins.security.allow_default_init_securityindex=true",
                ],
                "ulimits": {
                    "memlock": {"soft": -1, "hard": -1},
                    "nofile": {"soft": 65536, "hard": 65536},
                },
                "volumes": ["opensearch-data1:/usr/share/opensearch/data"],
                "ports": ["9200:9200", "9600:9600"],
            },
            "hkg-opensearch-node-2": {
                "image": "opensearchproject/opensearch:2.11.1",
                "container_name": "hkg-opensearch-node-2",
                "environment": [
                    "cluster.name=opensearch-cluster",
                    "node.name=hkg-opensearch-node-2",
                    "discovery.seed_hosts=hkg-opensearch-node-1,hkg-opensearch-node-2",
                    "cluster.initial_cluster_manager_nodes=hkg-opensearch-node-1,hkg-opensearch-node-2",
                    "bootstrap.memory_lock=true",
                    "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m",
                    "OPENSEARCH_INITIAL_ADMIN_PASSWORD=admin",
                    "plugins.security.ssl.http.enabled=false",
                    "plugins.security.allow_default_init_securityindex=true",
                ],
                "ulimits": {
                    "memlock": {"soft": -1, "hard": -1},
                    "nofile": {"soft": 65536, "hard": 65536},
                },
                "volumes": ["opensearch-data2:/usr/share/opseensearch/data"],
            },
            "hkg-opensearch-dashboards": {
                "image": "opensearchproject/opensearch-dashboards:2.11.1",
                "container_name": "hkg-opensearch-dashboards",
                "ports": ["5601:5601"],
                "expose": ["5601"],
                "environment": {
                    "OPENSEARCH_HOSTS": '["http://hkg-opensearch-node-1:9200","http://hkg-opensearch-node-2:9200"]',
                    "OPENSEARCH_SSL_VERIFICATION_MODE": "none",
                    "OPENSEARCH_USERNAME": "admin",
                    "OPENSEARCH_PASSWORD": "admin",
                },
            },
        }
        volumes = {
            "opensearch-data1": None,
            "opensearch-data2": None,
        }

        # TODO: add virtuoso component directly as a service

        for name, component in self.components.items():
            component_config = self.config.components[name]
            component_config_dict = component_config.model_dump()
            services.update(component.get_docker_services(component_config_dict))
            volumes.update(component.get_docker_volumes(component_config_dict))

        return {"services": services, "volumes": volumes}

    def save_docker_compose(self) -> Path:
        """Save the generated docker-compose configuration to a file.

        Returns:
            Path: Path to the saved docker-compose file
        """
        compose_config = self.generate_docker_compose()
        compose_file = self.project_root / "docker-compose.yml"

        with open(compose_file, "w") as f:
            yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)

        return compose_file

    def load_config(self) -> ProjectConfig:
        """Load configuration from TOML file."""
        if not self.config_file.exists():
            return ProjectConfig()

        with open(self.config_file, "r") as f:
            config_data = tomlkit.load(f).unwrap()

        # Pre-process the raw dict to instantiate the correct EnvVars models
        processed_components = {}
        for name, component_data in config_data.get("components", {}).items():
            if name in self._env_vars_models:
                env_vars_class = self._env_vars_models[name]
                env_vars_data = component_data.get("env_vars", {})
                component_data["env_vars"] = env_vars_class(**env_vars_data)
            processed_components[name] = component_data

        config_data["components"] = processed_components
        return ProjectConfig(**config_data)

    def save_config(self) -> None:
        """Save the current configuration to the config file."""
        toml_data = tomlkit.document()
        toml_data["private"] = self.config.private
        toml_data["devops"] = self.config.devops
        components_table = tomlkit.table()

        for name, component in self.config.components.items():
            component_table = tomlkit.table()
            component_table["enabled"] = component.enabled
            component_table["name"] = component.name

            # Add environment variables if they exist
            if component.env_vars is not None:
                env_vars_table = tomlkit.table()
                if hasattr(component.env_vars, "model_dump"):
                    env_vars = component.env_vars.model_dump()
                else:
                    env_vars = component.env_vars
                for var_name, var_value in env_vars.items():
                    if var_value is not None:
                        env_vars_table[var_name] = var_value
                if env_vars_table:
                    component_table["env_vars"] = env_vars_table

            # Add repository information if it exists
            if component.repository:
                repo_table = tomlkit.table()
                for key, value in component.repository.model_dump().items():
                    if value is not None:
                        repo_table[key] = str(value)
                component_table["repository"] = repo_table

            components_table[name] = component_table

        toml_data["components"] = components_table

        with open(self.config_file, "w") as f:
            f.write(tomlkit.dumps(toml_data))

        # Update docker-compose after config change
        self.save_docker_compose()

    def update_component_config(
        self, component_name: str, config_updates: Dict
    ) -> None:
        """Update configuration for a specific component.

        Args:
            component_name: Name of the component to update
            config_updates: Dictionary of configuration updates
        """
        if component_name not in self.config.components:
            raise ValueError(f"Component {component_name} not found")

        current_config = self.config.components[component_name]
        updated_config = current_config.model_copy(update=config_updates)
        self.config.components[component_name] = updated_config

        # Save changes and update docker-compose
        self.save_config()
