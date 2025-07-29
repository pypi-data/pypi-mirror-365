from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from tomlkit import TOMLDocument
from .models import ComponentConfig


class BaseComponent(ABC):
    """Base class for all HKG components."""

    name: str
    is_private: bool = False
    is_devops: bool = False

    def __init__(
        self,
        project_root: Optional[Path] = None,
        config: Optional[ComponentConfig] = None,
    ):
        self.project_root = project_root or Path.cwd()
        self.config = config

    @abstractmethod
    def get_config_section(self) -> Dict[str, Any]:
        """Get the default configuration section for this component."""
        pass

    @abstractmethod
    def validate_config(self, config: TOMLDocument) -> None:
        """Validate the component's configuration section."""
        pass

    @abstractmethod
    def get_docker_services(self, config: TOMLDocument) -> Dict:
        """Get the docker services configuration for this component."""
        pass

    @abstractmethod
    def get_docker_volumes(self, config: TOMLDocument) -> Dict:
        """Get the docker volumes configuration for this component."""
        pass

    @abstractmethod
    def create_env_file(self) -> None:
        """Create the .env file for the component."""
        pass
