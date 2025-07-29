from pydantic import Field
from typing import Optional
from hkg_cli.components.models import BaseEnvVars


class DocumentationEnvVars(BaseEnvVars):
    """Environment variables for the Documentation component."""

    server_url: Optional[str] = Field(
        default="http://localhost:8000",
        description="The URL of the server where the documentation is hosted.",
        env="SERVER_URL",
    )
    node_env: Optional[str] = Field(
        default="dev",
        description="The node environment for the documentation build.",
        env="NODE_ENV",
    )
