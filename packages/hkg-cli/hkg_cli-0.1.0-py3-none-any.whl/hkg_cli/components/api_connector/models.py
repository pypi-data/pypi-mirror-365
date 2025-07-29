from pydantic import Field
from typing import Optional
from hkg_cli.components.models import BaseEnvVars


class ApiConnectorEnvVars(BaseEnvVars):
    """Environment variables for the Api Connector component."""

    debug: Optional[bool] = Field(default=False, description="Debug mode")
    storage_api_url: Optional[str] = Field(
        default="http://localhost", description="Data Storage API URL"
    )
    api_max_retries: Optional[int] = Field(
        default=1, description="Maximum number of retries for the Data Storage API"
    )
    package_size_api_send: Optional[int] = Field(
        default=1, description="Package size for the Data Storage API"
    )
    max_threads: Optional[int] = Field(
        default=1, description="Maximum number of harvesting threads."
    )
    max_api_threads: Optional[int] = Field(
        default=1, description="Maximum number of threads for the API"
    )
    api_retry_waiting_time: Optional[int] = Field(
        default=1,
        description="Waiting time between retries for the Data Storage API in seconds",
    )
    api_queue_size: Optional[int] = Field(
        default=48, description="Queue size for the Data Storage API"
    )
    api_error_queue_size: Optional[int] = Field(
        default=48, description="Error queue size for the Data Storage API"
    )
    api_queue_timeout: Optional[int] = Field(
        default=60, description="Queue timeout for the Data Storage API in seconds"
    )
    api_connection_timeout: Optional[int] = Field(
        default=10,
        description="Connection timeout for the Data Storage API in seconds",
    )
    api_read_timeout: Optional[int] = Field(
        default=100, description="Read timeout for the Data Storage API in seconds"
    )
