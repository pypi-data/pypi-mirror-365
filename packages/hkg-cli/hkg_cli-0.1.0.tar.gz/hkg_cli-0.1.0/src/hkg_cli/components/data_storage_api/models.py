from pydantic import Field
from typing import Optional
from hkg_cli.components.models import BaseEnvVars


class DataStorageAPIEnvVars(BaseEnvVars):
    """Environment variables for the Data Storage API component."""

    db_type: Optional[str] = Field(default="postgres", description="Database type")
    db_user: Optional[str] = Field(
        default="hkg_data_storage", description="Database user"
    )
    db_pass: Optional[str] = Field(
        default="hkg_data_storage_pass", description="Database password"
    )
    db_host: Optional[str] = Field(default="postgresql", description="Database host")
    db_name: Optional[str] = Field(
        default="hkg_data_storage", description="Database name"
    )
    db_port: Optional[int] = Field(default=5432, description="Database port")
    db_pool_min_count: Optional[int] = Field(
        default=2, description="Minimum database connection pool size"
    )
    db_pool_max_count: Optional[int] = Field(
        default=20, description="Maximum database connection pool size"
    )
    app_workers: Optional[int] = Field(
        default=5, description="Number of application workers"
    )
    app_port: Optional[int] = Field(default=80, description="Application port")
    app_host: Optional[str] = Field(default="0.0.0.0", description="Application host")
    entity_max_limit: Optional[int] = Field(
        default=100000, description="Maximum number of entities to return"
    )
    postgres_db: Optional[str] = Field(
        default="hkg_data_storage", description="PostgreSQL database name"
    )
    postgres_user: Optional[str] = Field(
        default="hkg_data_storage", description="PostgreSQL user"
    )
    postgres_password: Optional[str] = Field(
        default="hkg_data_storage_pass", description="PostgreSQL password"
    )
