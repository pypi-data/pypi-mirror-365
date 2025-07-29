from pydantic import Field
from typing import Optional
from hkg_cli.components.models import BaseEnvVars


class MappingEnvVars(BaseEnvVars):
    """Environment variables for the Mapping component."""

    max_threads: Optional[int] = Field(
        default=1, description="Maximum number of threads for data uplifting."
    )
    storage_api: Optional[str] = Field(
        default="http://localhost", description="Data Storage API URL."
    )
    package_size_api_get: Optional[int] = Field(
        default=100,
        description="Package size for getting data from the Data Storage API.",
    )
    max_retries_api: Optional[int] = Field(
        default=1,
        description="Maximum number of retries for requests to the Data Storage API.",
    )
    opensearch_host: Optional[str] = Field(
        default="http://localhost:9200", description="OpenSearch host URL."
    )
    debug: Optional[bool] = Field(
        default=False, description="Enable debug mode for verbose logging."
    )
