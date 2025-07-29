from pydantic import Field
from typing import Optional
from hkg_cli.components.models import BaseEnvVars


class DataHarvestingEnvVars(BaseEnvVars):
    """Environment variables for the Data Harvesting component."""

    debug: Optional[bool] = Field(default=False, description="Debug mode")
    storage_api: Optional[str] = Field(
        default="http://localhost/api/v1/raw/entities",
        description="Data Storage API URL",
    )
    max_retries_api: Optional[int] = Field(
        default=2, description="Maximum number of retries for the Data Storage API"
    )
    package_size_api_send: Optional[int] = Field(
        default=100, description="Package size for the Data Storage API"
    )
    max_threads: Optional[int] = Field(
        default=10, description="Maximum number of threads"
    )
