"""Commands for initializing a new Helmholtz Knowledge Graph instance."""

import typer
from hkg_cli.subcommands.utils import wrap_exceptions
from hkg_cli.components import (
    ProjectConfig,
    ComponentConfig,
    ComponentManager,
    COMPONENT_CLASSES,
)
from hkg_cli.git.commands import clone_and_checkout
from hkg_cli.git.models import GitRepositoryModel
from pathlib import Path
from typing import Dict, Any

app = typer.Typer()


def initialize_component(
    component_name: str, project_path: Path, config: Dict[str, Any] = None
) -> ComponentConfig:
    """Initialize a component with its configuration.

    Args:
        component_name: Name of the component to initialize
        project_path: Path to the project root
        config: Optional configuration to use instead of defaults

    Returns:
        ComponentConfig: The initialized component's configuration
    """
    component_class = COMPONENT_CLASSES.get(component_name)
    if not component_class:
        raise ValueError(f"Unknown component: {component_name}")

    if config:
        # For update case - use provided config
        if "name" not in config:
            config["name"] = component_name
        return ComponentConfig(**config)

    # For init case - use component's default config
    component = component_class(project_root=project_path)
    # The component __init__ creates a default config with a typed env_vars model
    return component.config


def clone_component_repositories(config: ProjectConfig, project_path: Path) -> None:
    """Clone repositories for all enabled components.

    Args:
        config: Project configuration containing component settings
        project_path: Path to the project root
    """
    for name, component_config in config.components.items():
        if component_config.enabled and component_config.repository:
            component_class = COMPONENT_CLASSES.get(name)
            if not component_class:
                continue

            component_instance = component_class()
            # Skip private repos if private flag is not set
            if component_instance.is_private and not config.private:
                continue
            # Skip devops repos if devops flag is not set
            if component_instance.is_devops and not config.devops:
                continue

            repo_model = GitRepositoryModel.model_validate(component_config.repository)
            repo_path = project_path / repo_model.repo_folder
            clone_and_checkout(repo_model, repo_path)


@app.command("init")
@wrap_exceptions
def initialize(
    folder_name: str = typer.Argument(
        ..., help="Name of the folder in which to initialize the project."
    ),
    private: bool = typer.Option(
        False,
        "--private",
        help="Use this flag to clone components with private repositories. You have to be able to access the private repositories with your SSH key.",
    ),
    devops: bool = typer.Option(
        False,
        "--devops",
        help="Use this flag to clone devops repositories. You have to be able to access the devops repositories with your SSH key.",
    ),
):
    """Initialize Helmholtz Knowledge Graph configuration with default values."""
    typer.echo("Initializing Helmholtz Knowledge Graph...")
    project_path = Path(folder_name)

    # If the folder name isn't absolute, resolve it relative to the current working directory.
    if not project_path.is_absolute():
        project_path = (Path.cwd() / project_path).resolve()

    if project_path.exists() and any(project_path.iterdir()):
        raise typer.Exit(
            f"Cannot initialize project in '{folder_name}': Directory exists and is not empty. "
            "Please choose a different directory or remove the existing one.",
            code=1,
        )
    else:
        project_path.mkdir(parents=True, exist_ok=True)
        typer.echo(f"Created folder '{folder_name}'.")

    # Initialize components with defaults
    components = {}
    for component_name in COMPONENT_CLASSES.keys():
        components[component_name] = initialize_component(component_name, project_path)

    # Initialize with default config
    config = ProjectConfig(components=components, private=private, devops=devops)

    # Clone repositories for enabled components first
    typer.echo("Cloning component repositories...")
    clone_component_repositories(config, project_path)

    # Initialize component manager
    manager = ComponentManager(config, project_path)
    manager.initialize_components()

    # Save configuration and generate docker-compose
    typer.echo("Saving configuration...")
    manager.save_config()
    typer.echo("Generating docker-compose file...")
    compose_file = manager.save_docker_compose()
    typer.echo(f"Configuration saved to {manager.config_file}")
    typer.echo(f"Docker compose file saved to {compose_file}")


@app.command("update")
@wrap_exceptions
def update():
    """Update the Helmholtz Knowledge Graph components according to the updated config file."""
    typer.echo(
        "Updating Helmholtz Knowledge Graph components according to updated config file..."
    )
    project_path = Path.cwd().resolve()

    # check if config file exists
    if not (project_path / "hkg-config.toml").exists():
        raise ValueError("Config file not found. Please run 'hkg init' first.")

    # Initialize component manager, load the config, and initialize components
    manager = ComponentManager(ProjectConfig(), project_path)
    config = manager.load_config()
    manager.config = config
    manager.initialize_components()

    # Clone/update repositories for enabled components
    typer.echo("Checking component repositories...")
    clone_component_repositories(config, project_path)

    # Update docker-compose
    typer.echo("Updating docker-compose file...")
    compose_file = manager.save_docker_compose()
    typer.echo(f"Update complete. Docker compose file updated at {compose_file}")
