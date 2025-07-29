"""Component configuration models."""

from typing import Dict, Optional
from pydantic import BaseModel
from hkg_cli.git.models import GitRepositoryModel


class BaseEnvVars(BaseModel):
    """Base model for component environment variables."""

    def to_env_file(self) -> str:
        """Generate the content for a .env file."""
        lines = []
        for key, value in self.model_dump().items():
            if value is not None:
                lines.append(f"{key.upper()}={value}")
        return "\n".join(lines)


class ComponentConfig(BaseModel):
    """Configuration for a component."""

    enabled: bool = True
    name: str
    env_vars: BaseEnvVars
    repository: Optional[GitRepositoryModel] = None


class ProjectConfig(BaseModel):
    """Project configuration."""

    components: Dict[str, ComponentConfig] = {}
    private: bool = False
    devops: bool = False
