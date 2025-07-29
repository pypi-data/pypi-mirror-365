[
![Docs](https://img.shields.io/badge/read-docs-success)
](https://hmc.pages.hzdr.de/hmc-public/unhide/development/hkg-cli)
[
![Test Coverage](https://hmc.pages.hzdr.de/hmc-public/unhide/development/hkg-cli/main/coverage_badge.svg)
](https://hmc.pages.hzdr.de/hmc-public/unhide/development/hkg-cli/main/coverage)

<!-- --8<-- [start:abstract] -->

# hkg-cli

A command-line interface tool for setting up and managing Helmholtz Knowledge Graph (HKG) development environments. hkg-cli provides a streamlined way to initialize, configure, and run HKG components with minimal setup effort.

## Key Features

-   🚀 **Quick Setup**: Initialize a complete HKG development environment with a single command
-   🔧 **Configuration Management**: Easy configuration through TOML files
-   🐳 **Docker Integration**: Automated Docker Compose setup for all HKG components
-   🔄 **Component Updates**: Simple commands to update and manage HKG components
-   🛠️ **Development Tools**: Built-in utilities for common development tasks
-   🔒 **Private Components**: Support for private and devops repositories
-   📝 **Rich Logging**: Enhanced logging with debug options

## Why hkg-cli?

-   **Simplified Development**: Reduces the complexity of setting up HKG development environments
-   **Standardized Setup**: Ensures consistent development environments across teams
-   **Time Saving**: Automates repetitive setup tasks and configuration
-   **Easy Maintenance**: Streamlined process for updating and managing HKG components

<!-- --8<-- [end:abstract] -->
<!-- --8<-- [start:quickstart] -->

## Installation

This project works with Python > 3.9.

```bash
pip install git+ssh://git@codebase.helmholtz.cloud/hmc/hmc-public/unhide/development/hkg-cli.git
```

Or, you can install via pypi registry.

```bash
pip install hkg-cli
```

## Getting Started

1. Initialize a new HKG project:

```bash
hkg-cli setup init my-hkg-project [--private] [--devops]
```

The `my-hkg-project` folder will be created to hold all component repositories. This folder will contain:
- Individual component repositories as subdirectories with environment files
- Configuration file
- Docker compose files

!!! warning "SSH Key Requirements"
    To use private or devops repositories, you must:
    1. Have SSH access to the Helmholtz GitLab instance
    2. Have your SSH key properly configured
    3. Have access permissions to the private repositories
    4. Use the `--private` flag for private repositories
    5. Use the `--devops` flag for devops repositories

    If you don't have the required SSH access, the initialization will fail when trying to clone private repositories.

Options:
- `--private`: Enable cloning of private repositories (requires SSH access)
- `--devops`: Enable cloning of devops repositories (requires SSH access)

2. Start the development environment:

```bash
hkg-cli run
```

3. Stop the environment when done:

```bash
hkg-cli stop [--clear]
```

Options:
- `--clear`: Clear all volumes and networks in docker

4. Update components:

```bash
hkg-cli setup update
```

The update command will:
- Apply changes made in `hkg-config.toml` to the environment
- Update Docker compose file based on configuration changes
- Update environment variables for components
- Pull latest changes if repository versions/branches/commits are modified
- Disable components in Docker compose if `enabled=false` is set

!!! tip "Configuration Changes"
    You can modify the `hkg-config.toml` file to:
    - Change component versions/branches/commits
    - Enable/disable components (set `enabled=false` to disable)
    - Update environment variables
    - Modify component configurations

    Run `hkg-cli setup update` to apply these changes.

5. Show version:

```bash
hkg-cli --version
```

6. Enable debug logging:

```bash
hkg-cli --debug [command]
```

For more detailed usage instructions, please refer to our [documentation](https://hmc.pages.hzdr.de/hmc-public/unhide/development/hkg-cli/main).

## Troubleshooting

### When I try installing the package, I get an `IndexError: list index out of range`

Make sure you have `pip` > 21.2 (see `pip --version`), older versions have a bug causing
this problem. If the installed version is older, you can upgrade it with
`pip install --upgrade pip` and then try again to install the package.

### SSH Access Issues

If you encounter SSH-related errors during initialization:

1. Verify your SSH key is properly configured:
   ```bash
   ssh -T git@codebase.helmholtz.cloud
   ```

2. Ensure you have access to the required repositories:
   - Check your GitLab permissions
   - Contact your project administrator if needed

3. If using a custom SSH key, make sure it's added to your SSH agent:
   ```bash
   ssh-add ~/.ssh/your_private_key
   ```

**You can find more information on using and contributing to this repository in the
[documentation](https://hmc.pages.hzdr.de/hmc-public/unhide/development/hkg-cli/main).**

<!-- --8<-- [end:quickstart] -->
<!-- --8<-- [start:citation] -->

## How to Cite

If you want to cite this project in your scientific work,
please use the [citation file](https://citation-file-format.github.io/)
in the [repository](https://codebase.helmholtz.cloud/hmc/hmc-public/unhide/development/hkg-cli.git/blob/main/CITATION.cff).

<!-- --8<-- [end:citation] -->
<!-- --8<-- [start:acknowledgements] -->

## Acknowledgements

We kindly thank all
[authors and contributors](https://hmc.pages.hzdr.de/hmc-public/unhide/development/hkg-cli/latest/credits).

<div>
<img style="vertical-align: middle;" alt="HMC Logo" src="https://github.com/Materials-Data-Science-and-Informatics/Logos/raw/main/HMC/HMC_Logo_M.png" width=50% height=50% />
&nbsp;&nbsp;
<img style="vertical-align: middle;" alt="FZJ Logo" src="https://github.com/Materials-Data-Science-and-Informatics/Logos/raw/main/FZJ/FZJ.png" width=30% height=30% />
</div>
<br />

This project was developed at the Institute for Materials Data Science and Informatics
(IAS-9) of the Jülich Research Center and funded by the Helmholtz Metadata Collaboration
(HMC), an incubator-platform of the Helmholtz Association within the framework of the
Information and Data Science strategic initiative.

<!-- --8<-- [end:acknowledgements] -->
