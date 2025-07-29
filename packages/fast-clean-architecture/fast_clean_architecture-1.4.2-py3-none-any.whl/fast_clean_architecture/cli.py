"""Command-line interface for fast-clean-architecture."""

import shutil
import subprocess  # nosec B404 # Subprocess used for secure package management operations
import sys
from pathlib import Path
from typing import Annotated, NoReturn, Optional, cast

import click
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from .analytics import track_component_creation
from .config import Config
from .error_tracking import track_error
from .exceptions import FastCleanArchitectureError, ValidationError
from .generators import ConfigUpdater, PackageGenerator
from .generators.generator_factory import create_generator_factory
from .health import log_startup_health
from .logging_config import configure_logging, get_logger
from .utils import sanitize_name, validate_python_identifier

# Configure structured logging
configure_logging()
logger = get_logger(__name__)

# Log startup health
log_startup_health()

# Create the main Typer app
app = typer.Typer(
    name="fca-scaffold",
    help="""[bold blue]Fast Clean Architecture - Complete Guide[/bold blue]

[bold yellow]📖 Key Definitions:[/bold yellow]

[yellow]System:[/yellow]
  A bounded context representing a major business domain.
  Examples: admin, customer, settings

[yellow]Module:[/yellow]
  A functional area within a system that groups related components.
  Examples: auth, billing, notifications, reporting

[yellow]Component:[/yellow]
  Individual code artifacts within Clean Architecture layers:

    [dim]Domain:[/dim]
      - entities (business entities)
      - events (domain events)
      - exceptions (domain-specific exceptions)
      - interfaces (domain contracts/ports)
      - value_objects (immutable value objects)

    [dim]Application:[/dim]
      - dtos (Data Transfer Objects)
      - services (application services)
      - use_cases/commands (command handlers for writes)
      - use_cases/queries (query handlers for reads)

    [dim]Infrastructure:[/dim]
      - config (configuration management)
      - database/migrations (database migrations)
      - database/models (database models/schemas)
      - database/repositories (repository implementations)
      - external (external service integrations)

    [dim]Presentation:[/dim]
      - controllers (API controllers)
      - middleware (request/response middleware)
      - routes (route definitions)
      - schemas (API schemas/validation)

[bold yellow]🚀 Quick Start Workflow:[/bold yellow]
1. [cyan]fca-scaffold init my-project[/cyan] - Initialize project
2. [cyan]fca-scaffold create-system-context admin[/cyan] - Create system
3. [cyan]fca-scaffold create-module admin auth[/cyan] - Create module
4. [cyan]fca-scaffold create-component admin/auth/domain/entities AdminUser[/cyan] - Create any component type

[bold yellow]💡 Pro Tips:[/bold yellow]
• Use [cyan]--dry-run[/cyan] to preview changes
• Use [cyan]--help[/cyan] with any command for detailed info
• Check [cyan]fca-scaffold status[/cyan] to see project structure
• Validate config with [cyan]fca-scaffold config validate[/cyan]

[bold yellow]📖 For detailed help on any command:[/bold yellow]
[cyan]fca-scaffold [COMMAND] --help[/cyan]
    """,
    rich_markup_mode="rich",
)

# Create console for rich output
console = Console()

# Global options
DRY_RUN_OPTION = typer.Option(
    False,
    "--dry-run",
    "-d",
    help="Show what would be created without actually creating files",
)
FORCE_OPTION = typer.Option(
    False, "--force", "-f", help="Overwrite existing files without confirmation"
)
VERBOSE_OPTION = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
CONFIG_PATH_OPTION = typer.Option(
    "fca_config.yaml", "--config", "-c", help="Path to configuration file"
)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def get_config_path(config_file: str) -> Path:
    """Get the full path to the configuration file."""
    config_path = Path(config_file)
    if not config_path.is_absolute():
        config_path = get_project_root() / config_path
    return config_path


def handle_error(error: Exception, verbose: bool = False) -> NoReturn:
    """Handle and display errors consistently."""
    if isinstance(error, FastCleanArchitectureError):
        console.print(f"[red]Error:[/red] {error}")
    else:
        console.print(f"[red]Unexpected error:[/red] {error}")

    if verbose:
        console.print_exception()

    sys.exit(1)


@app.command()
def init(
    name: Optional[str] = typer.Argument(
        None, help="Project name (will be sanitized for Python compatibility)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="Project description for documentation"
    ),
    version: Optional[str] = typer.Option(
        "0.1.0", "--version", help="Initial project version (semantic versioning)"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Initialize a new Fast Clean Architecture project.

    Creates a new FCA project with configuration file and basic directory structure.
    If no name is provided, you'll be prompted to enter one.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold init[/cyan]                                    # Interactive mode
      [cyan]fca-scaffold init my-api[/cyan]                            # With project name
      [cyan]fca-scaffold init my-api --desc "User management API"[/cyan]  # With description
      [cyan]fca-scaffold init my-api --version 1.0.0 --force[/cyan]       # Overwrite existing

    [bold]What it creates:[/bold]
      • [dim]fca_config.yaml[/dim] - Project configuration file
      • [dim]systems/[/dim] - Directory for system contexts
    """
    try:
        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Safety check: Prevent creating projects in FCA package root
        fca_indicators = ["fast_clean_architecture", "pyproject.toml", "poetry.lock"]
        if any((project_root / indicator).exists() for indicator in fca_indicators):
            if not force:
                console.print(
                    "[red]⚠️  Warning: You're in the Fast Clean Architecture package directory![/red]\n"
                    "[yellow]For testing, please use a separate directory like 'package-testing'.[/yellow]\n"
                    "[dim]Use --force to override this safety check.[/dim]"
                )
                return
            else:
                console.print(
                    "[yellow]⚠️  Force mode: Creating project in FCA package directory.[/yellow]"
                )

        # Check if config already exists
        if config_path.exists() and not force:
            if not Confirm.ask(
                f"Configuration file {config_path} already exists. Overwrite?"
            ):
                console.print("[yellow]Initialization cancelled.[/yellow]")
                return

        # Get project name if not provided
        if not name:
            name = Prompt.ask("Project name", default=project_root.name)

        # Sanitize project name
        sanitized_name = sanitize_name(name)
        if not validate_python_identifier(sanitized_name):
            raise ValidationError(f"Invalid project name: {name}")

        # Get description if not provided
        if not description:
            description = Prompt.ask("Project description", default="")

        # Create configuration
        config = Config.create_default()
        config.project.name = sanitized_name
        config.project.description = description
        config.project.version = version or "0.1.0"

        # Save configuration
        config.save_to_file(config_path)

        # Create basic project structure
        systems_dir = project_root / "systems"
        systems_dir.mkdir(exist_ok=True)

        console.print(
            Panel.fit(
                f"[green]✅ Project '{sanitized_name}' initialized successfully![/green]\n"
                f"Configuration saved to: {config_path}\n"
                f"Systems directory created: {systems_dir}",
                title="Project Initialized",
            )
        )

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def create_system_context(
    name: str = typer.Argument(
        ..., help="System context name (e.g., admin, customer, settings)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="Description of what this system handles"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a new system context.

    A system context represents a bounded context in your domain, containing related
    business functionality or aimed at different operational context such as admin, customer, settings. Each system can contain multiple modules.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold create-system-context admin[/cyan]
      [cyan]fca-scaffold create-system-context customer --desc "Customer System"[/cyan]
      [cyan]fca-scaffold create-system-context settings --dry-run[/cyan]  # Preview only

    [bold]What it creates:[/bold]
      • [dim]systems/[SYSTEM_NAME]/[/dim] - System directory
      • [dim]systems/[SYSTEM_NAME]/__init__.py[/dim] - Python package file
      • Updates [dim]fca_config.yaml[/dim] with system information

    [bold]Next steps:[/bold]
      Create modules with: [cyan]fca-scaffold create-module [SYSTEM_NAME] [MODULE_NAME][/cyan]
    """
    try:
        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Sanitize system name
        sanitized_name = sanitize_name(name)
        if not validate_python_identifier(sanitized_name):
            raise ValidationError(f"Invalid system name: {name}")

        # Initialize generators
        config_updater = ConfigUpdater(config_path, console)
        package_generator = PackageGenerator(console)

        # Create system structure
        package_generator.create_system_structure(
            base_path=project_root,
            system_name=sanitized_name,
            dry_run=dry_run,
        )

        if not dry_run:
            # Update configuration
            config_updater.add_system(sanitized_name, description)

        console.print(
            f"[green]✅ System context '{sanitized_name}' created successfully![/green]"
        )

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def create_module(
    system_name: str = typer.Argument(..., help="Existing system context name"),
    module_name: str = typer.Argument(
        ..., help="Module name (e.g., authentication, user_profile)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="Description of module functionality"
    ),
    api_version: Optional[str] = typer.Option(
        None,
        "--api-version",
        "-av",
        help="API version for presentation layer (e.g., v1, v2, v3)",
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a new module within a system context.

    Modules organize related functionality within a system context, following
    Clean Architecture layers (domain, application, infrastructure, presentation).

    The presentation layer can be created with version-specific directories when
    --api-version is specified, enabling API versioning support.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold create-module admin authentication[/cyan]                    # Create module
      [cyan]fca-scaffold create-module admin auth --desc "Authentication logic"[/cyan]  # With description
      [cyan]fca-scaffold create-module customer payment --desc "Payment logic"[/cyan]  # With description
      [cyan]fca-scaffold create-module user profile --api-version v1[/cyan]         # With API versioning
      [cyan]fca-scaffold create-module settings notifications --dry-run[/cyan]      # Preview only

    [bold]What it creates:[/bold]
      • [dim]systems/[SYSTEM_NAME]/[MODULE_NAME]/[/dim] - Module directory
      • [dim]systems/[SYSTEM_NAME]/[MODULE_NAME]/__init__.py[/dim] - Package file
      • [dim]systems/[SYSTEM_NAME]/[MODULE_NAME]/[MODULE_NAME]_module_api.py[/dim] - Module API file
      • [dim]systems/[SYSTEM_NAME]/[MODULE_NAME]/domain/[/dim] - Domain layer (entities, interfaces, value_objects, events, exceptions)
      • [dim]systems/[SYSTEM_NAME]/[MODULE_NAME]/application/[/dim] - Application layer (use_cases/commands, use_cases/queries, services, dtos)
      • [dim]systems/[SYSTEM_NAME]/[MODULE_NAME]/infrastructure/[/dim] - Infrastructure layer (database, external, config)
      • [dim]systems/[SYSTEM_NAME]/[MODULE_NAME]/presentation/[/dim] - Presentation layer (routes, controllers, schemas, middleware)
      • [dim]systems/[SYSTEM_NAME]/[MODULE_NAME]/presentation/*/[VERSION]/[/dim] - Version-specific directories (when --api-version is used)
      • Updates [dim]fca_config.yaml[/dim] with module information

    [bold]Next steps:[/bold]
      Create components with: [cyan]fca-scaffold create-component [SYSTEM_NAME]/[MODULE_NAME]/[LAYER]/[TYPE] [COMPONENT_NAME][/cyan]
    """
    try:
        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Sanitize names
        sanitized_system = sanitize_name(system_name)
        sanitized_module = sanitize_name(module_name)

        if not validate_python_identifier(sanitized_system):
            raise ValidationError(f"Invalid system name: {system_name}")
        if not validate_python_identifier(sanitized_module):
            raise ValidationError(f"Invalid module name: {module_name}")

        # Module type is now always 'advanced' since simple modules are no longer supported

        # Validate API version format if provided
        if api_version and not api_version.startswith("v"):
            raise ValidationError(
                f"API version must start with 'v' (e.g., v1, v2, v3). Got: {api_version}"
            )

        # API versioning is supported for all modules
        # (No additional validation needed)

        # Initialize config updater for validation
        config_updater = ConfigUpdater(config_path, console)

        # Validate system exists BEFORE creating any directory structure
        if sanitized_system not in config_updater.config.project.systems:
            raise ValidationError(
                f"System '{sanitized_system}' not found.\n\n"
                f"To create the module, first create the system:\n"
                f'  fca-scaffold create-system-context {sanitized_system} --description "[SYSTEM_DESCRIPTION]"\n\n'
                f"Then create your module:\n"
                f"  fca-scaffold create-module {sanitized_system} {sanitized_module}"
            )

        # Create module structure
        package_generator = PackageGenerator(console)
        package_generator.create_module_structure(
            base_path=project_root,
            system_name=sanitized_system,
            module_name=sanitized_module,
            api_version=api_version,
            dry_run=dry_run,
        )

        if not dry_run:
            # Update configuration
            is_new_module = config_updater.add_module(
                sanitized_system,
                sanitized_module,
                description=description or "",
                api_version=api_version,
            )

            # Provide appropriate feedback based on whether module was new or updated
            if is_new_module:
                version_info = f" with API version {api_version}" if api_version else ""
                console.print(
                    f"[green]✅ Module '{sanitized_module}' created in system '{sanitized_system}'{version_info}![/green]"
                )
            else:
                version_info = f" to API version {api_version}" if api_version else ""
                console.print(
                    f"[yellow]ℹ️  Module '{sanitized_module}' already exists in system '{sanitized_system}'. Updated presentation layers{version_info}.[/yellow]"
                )
        else:
            # For dry run, just show what would be created
            version_info = f" with API version {api_version}" if api_version else ""
            console.print(
                f"[green]✅ Module '{sanitized_module}' would be created in system '{sanitized_system}'{version_info}![/green]"
            )

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def migrate_to_api_versioning(
    system_name: str = typer.Argument(..., help="Existing system context name"),
    module_name: str = typer.Argument(
        ..., help="Module name to migrate (e.g., authentication, user_profile)"
    ),
    target_version: str = typer.Option(
        "v1", "--target-version", "-tv", help="Target API version (e.g., v1, v2, v3)"
    ),
    components: Optional[str] = typer.Option(
        None,
        "--components",
        "-comp",
        help="Comma-separated list of components to migrate (controllers,routes,schemas). If not specified, migrates all.",
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Migrate existing unversioned presentation layer files to API versioning.

    This command helps migrate modules that were created without API versioning
    to use versioned directory structures. It moves existing files from the root
    presentation layer directories into version-specific subdirectories.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold migrate-to-api-versioning user_management preferences --target-version v1[/cyan]
      [cyan]fca-scaffold migrate-to-api-versioning admin auth --target-version v2 --components controllers,routes[/cyan]
      [cyan]fca-scaffold migrate-to-api-versioning customer payment --dry-run[/cyan]  # Preview changes

    [bold]What it does:[/bold]
      • Scans presentation layer for unversioned .py files (excluding __init__.py)
      • Creates version-specific directories (e.g., v1/, v2/)
      • Moves existing files into versioned directories
      • Updates import statements within moved files
      • Creates backup before migration
      • Preserves middleware/ directory (version-agnostic)

    [bold]Before migration:[/bold]
      [dim]presentation/[/dim]
      [dim]├── controllers/[/dim]
      [dim]│   ├── __init__.py[/dim]
      [dim]│   └── user_controller.py[/dim]  ← Will be moved
      [dim]└── routes/[/dim]
      [dim]    ├── __init__.py[/dim]
      [dim]    └── user_routes.py[/dim]      ← Will be moved

    [bold]After migration:[/bold]
      [dim]presentation/[/dim]
      [dim]├── controllers/[/dim]
      [dim]│   ├── __init__.py[/dim]
      [dim]│   └── v1/[/dim]
      [dim]│       ├── __init__.py[/dim]
      [dim]│       └── user_controller.py[/dim]  ← Moved here
      [dim]└── routes/[/dim]
      [dim]    ├── __init__.py[/dim]
      [dim]    └── v1/[/dim]
      [dim]        ├── __init__.py[/dim]
      [dim]        └── user_routes.py[/dim]      ← Moved here

    [bold]Safety features:[/bold]
      • Automatic backup creation before migration
      • Dry-run mode to preview changes
      • Validation to prevent conflicts with existing versioned directories
      • Selective component migration
    """
    try:
        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Sanitize names
        sanitized_system = sanitize_name(system_name)
        sanitized_module = sanitize_name(module_name)

        if not validate_python_identifier(sanitized_system):
            raise ValidationError(f"Invalid system name: {system_name}")
        if not validate_python_identifier(sanitized_module):
            raise ValidationError(f"Invalid module name: {module_name}")

        # Validate API version format
        if not target_version.startswith("v"):
            raise ValidationError(
                f"API version must start with 'v' (e.g., v1, v2, v3). Got: {target_version}"
            )

        # Initialize config updater for validation
        config_updater = ConfigUpdater(config_path, console)

        # Validate system exists
        if sanitized_system not in config_updater.config.project.systems:
            raise ValidationError(
                f"System '{sanitized_system}' not found.\n\n"
                f"Available systems: {', '.join(config_updater.config.project.systems.keys())}"
            )

        # Validate module exists
        system_modules = config_updater.config.project.systems[sanitized_system].modules
        if sanitized_module not in system_modules:
            raise ValidationError(
                f"Module '{sanitized_module}' not found in system '{sanitized_system}'.\n\n"
                f"Available modules: {', '.join(system_modules.keys())}"
            )

        # Parse components to migrate
        components_to_migrate = ["controllers", "routes", "schemas"]  # Default
        if components:
            components_to_migrate = [comp.strip() for comp in components.split(",")]
            # Validate component names
            valid_components = ["controllers", "routes", "schemas"]
            invalid_components = [
                comp for comp in components_to_migrate if comp not in valid_components
            ]
            if invalid_components:
                raise ValidationError(
                    f"Invalid component(s): {', '.join(invalid_components)}. "
                    f"Valid components: {', '.join(valid_components)}"
                )

        # Initialize package generator
        package_generator = PackageGenerator(console)

        # Perform migration
        package_generator.migrate_to_api_versioning(
            base_path=project_root,
            system_name=sanitized_system,
            module_name=sanitized_module,
            target_version=target_version,
            components=components_to_migrate,
            dry_run=dry_run,
            force=force,
        )

        if not dry_run:
            # Update configuration to include the new API version
            config_updater.add_module(
                sanitized_system, sanitized_module, api_version=target_version
            )

            console.print(
                f"[green]✅ Successfully migrated module '{sanitized_module}' in system '{sanitized_system}' to API version {target_version}![/green]"
            )
        else:
            console.print(
                f"[yellow]DRY RUN:[/yellow] Would migrate module '{sanitized_module}' in system '{sanitized_system}' to API version {target_version}"
            )

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def create_component(
    location: str = typer.Argument(
        ...,
        help="Component location: system/module/layer/type (e.g., user_management/auth/domain/entities)",
    ),
    name: str = typer.Argument(
        ..., help="Component name (e.g., User, AuthService, UserRepository)"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a new component.

    Creates components following Clean Architecture patterns. Components are generated
    from templates and placed in the appropriate layer directory.

    [bold]Location format:[/bold] [cyan]system_name/module_name/layer/component_type[/cyan]

    [bold]Available layers and component types:[/bold]
      [yellow]domain/[/yellow]
        • [cyan]entities[/cyan] - Domain entities (business objects)
        • [cyan]value_objects[/cyan] - Value objects (immutable data)
        • [cyan]repositories[/cyan] - Repository interfaces (domain/interfaces)
        • [cyan]services[/cyan] - Domain services

      [yellow]application/[/yellow]
        • [cyan]commands[/cyan] - Command handlers (CQRS)
        • [cyan]queries[/cyan] - Query handlers (CQRS)
        • [cyan]services[/cyan] - Application services

      [yellow]infrastructure/[/yellow]
        • [cyan]models[/cyan] - Database models and schemas
        • [cyan]repositories[/cyan] - Repository implementations
        • [cyan]external[/cyan] - External service adapters

      [yellow]presentation/[/yellow]
        • [cyan]api[/cyan] - API endpoints/controllers
        • [cyan]schemas[/cyan] - Request/response schemas

    [bold]Examples:[/bold]
      [cyan]fca-scaffold create-component admin/auth/domain/entities User[/cyan]
      [cyan]fca-scaffold create-component admin/auth/application/use_cases/commands CreateUser[/cyan]
      [cyan]fca-scaffold create-component customer/payment_processing/infrastructure/database/repositories PaymentProcessingRepository[/cyan]
      [cyan]fca-scaffold create-component settings/notification_settings/presentation/controllers/v1 NotificationSettingsController[/cyan]

    [bold]What it creates:[/bold]
      • Python file with component implementation
      • Imports and dependencies based on component type
      • Updates [dim]fca_config.yaml[/dim] with component information
    """
    try:
        # Log CLI command start
        logger.info(
            "CLI create_component command started",
            operation="cli_create_component",
            location=location,
            name=name,
            dry_run=dry_run,
            force=force,
        )

        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Parse location
        location_parts = location.split("/")
        if len(location_parts) != 4:
            raise ValidationError(
                "Location must be in format: system_name/module_name/layer/component_type"
            )

        system_name, module_name, layer, component_type = location_parts

        # Sanitize names
        sanitized_system = sanitize_name(system_name)
        sanitized_module = sanitize_name(module_name)
        sanitized_name = sanitize_name(name)

        if not all(
            [
                validate_python_identifier(sanitized_system),
                validate_python_identifier(sanitized_module),
                validate_python_identifier(sanitized_name),
            ]
        ):
            raise ValidationError("Invalid names provided")

        # Initialize generators using factory pattern
        config_updater = ConfigUpdater(config_path, console)
        generator_factory = create_generator_factory(config_updater.config, console)
        component_generator = generator_factory.create_generator("component")

        # Cast to ComponentGeneratorProtocol for type safety
        from .generators import ComponentGeneratorProtocol

        component_gen = cast(ComponentGeneratorProtocol, component_generator)

        # Create component
        file_path = component_gen.create_component(
            base_path=project_root,
            system_name=sanitized_system,
            module_name=sanitized_module,
            layer=layer,
            component_type=component_type,
            component_name=sanitized_name,
            dry_run=dry_run,
            force=force,
        )

        if not dry_run:
            # Update configuration
            config_updater.add_component(
                system_name=sanitized_system,
                module_name=sanitized_module,
                layer=layer,
                component_type=component_type,
                component_name=sanitized_name,
                file_path=file_path,
            )

        console.print(
            f"[green]✅ Component '{sanitized_name}' created at {location}![/green]"
        )

        # Log successful completion
        logger.info(
            "CLI create_component command completed successfully",
            operation="cli_create_component",
            component_name=sanitized_name,
            location=location,
            file_path=str(file_path) if not dry_run else None,
        )

        # Track component creation for analytics
        if not dry_run:
            track_component_creation(
                system_name=sanitized_system,
                module_name=sanitized_module,
                layer=layer,
                component_type=component_type,
                component_name=sanitized_name,
            )

    except Exception as e:
        # Log CLI error and track it
        logger.error(
            "CLI create_component command failed",
            operation="cli_create_component",
            error=str(e),
            error_type=type(e).__name__,
            location=location,
            name=name,
        )

        # Track the error for analytics
        track_error(
            error=e,
            context={
                "command": "create_component",
                "location": location,
                "name": name,
                "dry_run": dry_run,
                "force": force,
            },
            operation="cli_create_component",
        )

        handle_error(e, verbose)


@app.command()
def batch_create(
    spec_file: str = typer.Argument(
        ..., help="Path to YAML specification file (see examples/components_spec.yaml)"
    ),
    config_file: str = CONFIG_PATH_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create multiple components from a YAML specification file.

    Batch creation allows you to define multiple systems, modules, and components
    in a single YAML file and create them all at once.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold batch-create components_spec.yaml[/cyan]
      [cyan]fca-scaffold batch-create my-spec.yaml --dry-run[/cyan]  # Preview only

    [bold]Specification file format:[/bold]
      [dim]systems:[/dim]
      [dim]  - name: admin[/dim]
      [dim]    modules:[/dim]
      [dim]      - name: authentication[/dim]
      [dim]        components:[/dim]
      [dim]          domain:[/dim]
      [dim]            entities: [AdminUser, AdminRole][/dim]
      [dim]            value_objects: [AdminEmail, AdminPassword][/dim]
      [dim]            repositories: [AdminUserRepository][/dim]
      [dim]          application:[/dim]
      [dim]            commands: [CreateAdminUser, UpdateAdminUser][/dim]

    [bold]See also:[/bold]
      Check [cyan]examples/components_spec.yaml[/cyan] for a complete example
    """
    try:
        import yaml

        project_root = get_project_root()
        config_path = get_config_path(config_file)
        spec_path = Path(spec_file)

        if not spec_path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_file}")

        # Load specification
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)

        # Initialize generators using factory pattern
        config_updater = ConfigUpdater(config_path, console)
        generator_factory = create_generator_factory(config_updater.config, console)
        component_generator = generator_factory.create_generator("component")

        # Process specification
        for system_spec in spec.get("systems", []):
            system_name = system_spec["name"]

            for module_spec in system_spec.get("modules", []):
                module_name = module_spec["name"]
                components_spec = module_spec.get("components", {})

                # Cast to ComponentGeneratorProtocol for type safety
                from .protocols import ComponentGeneratorProtocol

                component_gen = cast(ComponentGeneratorProtocol, component_generator)

                # Create components
                component_gen.create_multiple_components(
                    base_path=project_root,
                    system_name=system_name,
                    module_name=module_name,
                    components_spec=components_spec,
                    dry_run=dry_run,
                    force=force,
                )

        console.print("[green]✅ Batch creation completed![/green]")

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def status(
    config_file: str = CONFIG_PATH_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Show project status and configuration summary.

    Displays an overview of your FCA project including systems, modules,
    and recent activity. Useful for understanding project structure.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold status[/cyan]                    # Show project overview
      [cyan]fca-scaffold status --verbose[/cyan]         # Detailed information
      [cyan]fca-scaffold status -c my-config.yaml[/cyan] # Custom config file

    [bold]Information shown:[/bold]
      • Project name, version, and timestamps
      • Systems and module counts
      • Recent creation/update dates
      • Configuration file location
    """
    try:
        config_path = get_config_path(config_file)

        if not config_path.exists():
            console.print(
                "[yellow]No configuration file found. Run 'fca-scaffold init' first.[/yellow]"
            )
            return

        # Load configuration
        config_updater = ConfigUpdater(config_path, console)
        summary = config_updater.get_config_summary()

        # Display project info
        project_info = summary["project"]
        console.print(
            Panel.fit(
                f"[bold]Name:[/bold] {project_info['name']}\n"
                f"[bold]Version:[/bold] {project_info['version']}\n"
                f"[bold]Created:[/bold] {project_info['created_at']}\n"
                f"[bold]Updated:[/bold] {project_info['updated_at']}",
                title="Project Information",
            )
        )

        # Display systems table
        if summary["systems"]:
            table = Table(title="Systems Overview")
            table.add_column("System", style="cyan")
            table.add_column("Modules", style="green")
            table.add_column("Created", style="yellow")
            table.add_column("Updated", style="magenta")

            for system_name, system_info in summary["systems"].items():
                table.add_row(
                    system_name,
                    str(len(system_info["modules"])),
                    system_info["created_at"][:10],  # Show date only
                    system_info["updated_at"][:10],
                )

            console.print(table)
        else:
            console.print("[yellow]No systems found.[/yellow]")

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def config(
    action: str = typer.Argument(..., help="Action to perform: show, edit, validate"),
    config_file: str = CONFIG_PATH_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Manage project configuration.

    Provides tools to view, edit, and validate your FCA project configuration.
    The configuration file tracks all systems, modules, and components.

    [bold]Available actions:[/bold]
      [cyan]show[/cyan]     - Display configuration file contents with syntax highlighting
      [cyan]edit[/cyan]     - Get instructions for editing the configuration
      [cyan]validate[/cyan] - Check if configuration file is valid YAML and structure

    [bold]Examples:[/bold]
      [cyan]fca-scaffold config show[/cyan]                    # View current config
      [cyan]fca-scaffold config validate[/cyan]               # Check config validity
      [cyan]fca-scaffold config show -c my-config.yaml[/cyan] # Custom config file

    [bold]Configuration structure:[/bold]
      • [dim]project[/dim] - Project metadata (name, version, description)
      • [dim]systems[/dim] - System contexts and their modules
      • [dim]components[/dim] - Generated components and their locations
      • [dim]timestamps[/dim] - Creation and modification dates
    """
    try:
        config_path = get_config_path(config_file)

        if action == "show":
            if not config_path.exists():
                console.print("[yellow]No configuration file found.[/yellow]")
                return

            # Display configuration content
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

            syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Configuration: {config_path}"))

        elif action == "validate":
            if not config_path.exists():
                console.print("[red]Configuration file not found.[/red]")
                return

            try:
                Config.load_from_file(config_path)
                console.print("[green]✅ Configuration is valid![/green]")
            except Exception as e:
                console.print(f"[red]❌ Configuration is invalid: {e}[/red]")

        elif action == "edit":
            console.print(
                f"[yellow]Please edit the configuration file manually: {config_path}[/yellow]"
            )

        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            console.print("Available actions: show, edit, validate")

    except Exception as e:
        handle_error(e, verbose)


# Removed help_guide command - content merged into main --help


@app.command()
def create_scalable_baseline(
    name: str = typer.Argument(
        ..., help="Project name (will be sanitized for Python compatibility)"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "--desc", help="Project description for documentation"
    ),
    version: Optional[str] = typer.Option(
        "0.1.0", "--version", help="Initial project version (semantic versioning)"
    ),
    dependency_manager: Annotated[
        str,
        typer.Option(
            "--dependency-manager",
            "--deps",
            help="Dependency manager to use (poetry or pip)",
            click_type=click.Choice(["poetry", "pip"], case_sensitive=False),
        ),
    ] = "poetry",
    config_file: str = CONFIG_PATH_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Create a scalable FastAPI project structure with Clean Architecture.

    This command creates a complete FastAPI project with Clean Architecture,
    including all production-ready features for immediate development.

    [bold]Examples:[/bold]
      [cyan]fca-scaffold create-scalable-baseline my-api[/cyan]
      [cyan]fca-scaffold create-scalable-baseline my-api --desc "User management API"[/cyan]
      [cyan]fca-scaffold create-scalable-baseline my-api --deps pip[/cyan]
      [cyan]fca-scaffold create-scalable-baseline my-api --version 1.0.0 --deps poetry[/cyan]

    [bold]Features:[/bold]
      • Complete FastAPI project structure with Clean Architecture
      • Configuration files (pyproject.toml/requirements.txt, .env, etc.)
      • Docker setup for development and production
      • Database configuration and migrations
      • Authentication and authorization setup
      • API documentation and testing setup
      • CI/CD pipeline configuration

    [bold]Dependency Management:[/bold]
      • [cyan]--deps poetry[/cyan] (default): Uses Poetry for modern dependency management
      • [cyan]--deps pip[/cyan]: Uses traditional pip with requirements.txt
    """
    try:
        from .generators.package_generator import PackageGenerator

        project_root = get_project_root()

        # Safety check: Prevent creating projects in FCA package root
        fca_indicators = ["fast_clean_architecture", "pyproject.toml", "poetry.lock"]
        if any((project_root / indicator).exists() for indicator in fca_indicators):
            if not force:
                console.print(
                    "[red]⚠️  Warning: You're in the Fast Clean Architecture package directory![/red]\n"
                    "[yellow]For testing, please use a separate directory like 'package-testing'.[/yellow]\n"
                    "[dim]Use --force to override this safety check.[/dim]"
                )
                return
            else:
                console.print(
                    "[yellow]⚠️  Force mode: Creating project in FCA package directory.[/yellow]"
                )

        # Sanitize project name
        sanitized_name = sanitize_name(name)
        if not validate_python_identifier(sanitized_name):
            raise ValidationError(f"Invalid project name: {name}")

        # Create advanced baseline structure
        package_generator = PackageGenerator(console)

        # Determine project directory - use current directory if it matches project name
        current_dir_name = project_root.name
        if current_dir_name == sanitized_name or current_dir_name == name:
            # Use current directory as project root
            project_dir = project_root
            console.print(
                f"[blue]ℹ️  Using current directory '{current_dir_name}' as project root.[/blue]"
            )
        else:
            # Create new subdirectory
            project_dir = project_root / sanitized_name

        if project_dir.exists() and project_dir != project_root and not force:
            if not Confirm.ask(
                f"Directory '{sanitized_name}' already exists. Overwrite?"
            ):
                console.print("[yellow]Project creation cancelled.[/yellow]")
                return

        # Create complete project structure
        package_generator.create_base_project_structure(
            base_path=project_dir,
            project_name=sanitized_name,
            description=description or f"FastAPI project: {sanitized_name}",
            version=version or "0.1.0",
            dependency_manager=dependency_manager.lower(),
            dry_run=False,
        )

        # Run poetry lock if using poetry to ensure dependency resolution
        if dependency_manager.lower() == "poetry":
            try:
                console.print(
                    "[blue]🔒 Running poetry lock to resolve dependencies...[/blue]"
                )
                # Validate poetry executable exists
                poetry_path = shutil.which("poetry")
                if not poetry_path:
                    raise FileNotFoundError("Poetry executable not found in PATH")

                subprocess.run(  # nosec B603 # Controlled subprocess call with validated executable
                    [poetry_path, "lock"],
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                console.print("[green]✅ Poetry lock completed successfully.[/green]")
            except subprocess.CalledProcessError as e:
                console.print(
                    f"[yellow]⚠️  Warning: Poetry lock failed: {e.stderr}[/yellow]"
                )
                console.print(
                    "[dim]You may need to run 'poetry lock' manually after project creation.[/dim]"
                )
            except FileNotFoundError:
                console.print("[yellow]⚠️  Warning: Poetry not found in PATH.[/yellow]")
                console.print(
                    "[dim]Please ensure Poetry is installed and run 'poetry lock' manually.[/dim]"
                )

        # Generate dynamic next steps based on dependency manager and project location
        # Advanced baseline - include cd step if project was created in subdirectory
        cd_step = (
            ""
            if project_dir == project_root
            else f"1. [cyan]cd {sanitized_name}[/cyan]\n"
        )
        step_offset = 0 if project_dir == project_root else 1

        if dependency_manager.lower() == "poetry":
            next_steps = (
                f"{cd_step}"
                f"{step_offset + 1}. [cyan]poetry install[/cyan]\n"
                f"{step_offset + 2}. [cyan]cp .env.example .env[/cyan]\n"
                f"{step_offset + 3}. [cyan]poetry shell[/cyan]\n"
                f"{step_offset + 4}. [cyan]poetry run python core/main.py[/cyan]"
            )
            config_file = "pyproject.toml"
        else:  # pip
            next_steps = (
                f"{cd_step}"
                f"{step_offset + 1}. [cyan]python -m venv venv[/cyan]\n"
                f"{step_offset + 2}. [cyan]source venv/bin/activate[/cyan] (Linux/Mac) or [cyan]venv\\Scripts\\activate[/cyan] (Windows)\n"
                f"{step_offset + 3}. [cyan]pip install -r requirements.txt[/cyan]\n"
                f"{step_offset + 4}. [cyan]cp .env.example .env[/cyan]\n"
                f"{step_offset + 5}. [cyan]python core/main.py[/cyan]"
            )
            config_file = "requirements.txt"

        console.print(
            Panel.fit(
                f"[green]✅ Scalable FastAPI project '{sanitized_name}' created successfully![/green]\n\n"
                "[bold yellow]📁 Project Structure:[/bold yellow]\n"
                "• Complete FastAPI application with Clean Architecture\n"
                "• Database models and migrations\n"
                "• Authentication and authorization\n"
                "• API documentation and testing\n"
                f"• Dependency management with {dependency_manager} ({config_file})\n\n"
                "[bold yellow]🚀 Next Steps:[/bold yellow]\n"
                f"{next_steps}\n\n"
                f"[dim]Project created at: {project_dir}[/dim]",
                title="🎉 Project Created",
            )
        )

    except Exception as e:
        handle_error(e, verbose)


@app.command()
def update_package(
    version: Optional[str] = typer.Argument(
        None,
        help="Specific version to update to (e.g., '1.3.0'), or leave empty for latest",
    ),
    test_pypi: bool = typer.Option(
        False,
        "--test-pypi",
        "-t",
        help="Update from TestPyPI instead of main PyPI (for testing pre-release versions)",
    ),
    dry_run: bool = DRY_RUN_OPTION,
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Update the fast-clean-architecture package to a newer version.

    Updates the fast-clean-architecture package in your current project using poetry.
    This command is designed to be run from within your project directory (not the
    fast-clean-architecture workspace itself).

    [bold]Examples:[/bold]
      [cyan]fca-scaffold update-package[/cyan]              # Update to latest version
      [cyan]fca-scaffold update-package 1.3.0[/cyan]       # Update to specific version
      [cyan]fca-scaffold update-package --test-pypi[/cyan]  # Update from TestPyPI
      [cyan]fca-scaffold update-package 1.3.0 --test-pypi[/cyan] # Specific version from TestPyPI
      [cyan]fca-scaffold update-package --dry-run[/cyan]    # Preview what would be updated

    [bold]What it does:[/bold]
      • Checks if you're in a poetry project
      • Updates fast-clean-architecture package using poetry
      • Supports both PyPI and TestPyPI repositories
      • Automatically configures TestPyPI source when needed
      • Shows before/after version comparison
      • Verifies the update was successful
      • Provides helpful error messages for common issues

    [bold]TestPyPI Usage:[/bold]
      Use --test-pypi to install pre-release or development versions.
      TestPyPI is useful for testing new features before they're released.
    """
    import shutil
    import subprocess  # nosec B404 # Subprocess used for secure package management operations

    # Initialize source_info early to ensure it's available in exception handler
    source_info = "TestPyPI" if test_pypi else "PyPI"

    try:
        project_root = get_project_root()
        pyproject_path = project_root / "pyproject.toml"

        # Check if we're in the FCA package directory itself
        fca_indicators = ["fast_clean_architecture", "poetry.lock"]
        if any((project_root / indicator).exists() for indicator in fca_indicators):
            # Additional check: see if this is the FCA package itself
            if (project_root / "fast_clean_architecture" / "__init__.py").exists():
                console.print(
                    "[red]Error:[/red] You're in the fast-clean-architecture package directory."
                )
                console.print(
                    "[yellow]This command is for updating the package in your own projects.[/yellow]"
                )
                console.print(
                    "[dim]To update the package version itself, use the development workflow.[/dim]"
                )
                return

        # Check if we're in a poetry project
        if not pyproject_path.exists():
            console.print(
                "[red]Error:[/red] pyproject.toml not found. This command requires a Poetry project."
            )
            console.print(
                "[yellow]Make sure you're in a project directory that uses Poetry.[/yellow]"
            )
            return

        # Get current version of fast-clean-architecture
        try:
            # Validate poetry executable exists
            poetry_path = shutil.which("poetry")
            if not poetry_path:
                raise FileNotFoundError("Poetry executable not found in PATH")

            result = subprocess.run(  # nosec B603 # Controlled subprocess call with validated executable
                [poetry_path, "show", "fast-clean-architecture"],
                capture_output=True,
                text=True,
                cwd=project_root,
                check=True,
            )

            # Parse current version from poetry show output
            lines = result.stdout.strip().split("\n")
            current_version = None
            for line in lines:
                if line.startswith("version"):
                    current_version = line.split(":")[1].strip()
                    break

            if not current_version:
                console.print(
                    "[red]Error:[/red] fast-clean-architecture package not found in this project."
                )
                console.print(
                    "[yellow]Install it first with:[/yellow] poetry add fast-clean-architecture"
                )
                return

        except subprocess.CalledProcessError:
            console.print(
                "[red]Error:[/red] fast-clean-architecture package not found in this project."
            )
            console.print(
                "[yellow]Install it first with:[/yellow] poetry add fast-clean-architecture"
            )
            return
        except FileNotFoundError:
            console.print(
                "[red]Error:[/red] Poetry not found. Please install poetry first."
            )
            return
        console.print(
            f"[blue]Current fast-clean-architecture version:[/blue] {current_version}"
        )
        if test_pypi:
            console.print(
                "[yellow]ℹ️  Using TestPyPI source for pre-release versions[/yellow]"
            )

        # Prepare update command
        if test_pypi:
            # Configure TestPyPI source if not already configured
            try:
                # Validate poetry executable exists
                poetry_path = shutil.which("poetry")
                if poetry_path:
                    subprocess.run(  # nosec B603 # Controlled subprocess call with validated executable
                        [
                            poetry_path,
                            "source",
                            "add",
                            "--priority=explicit",
                            "test-pypi",
                            "https://test.pypi.org/simple/",
                        ],
                        capture_output=True,
                        text=True,
                        cwd=project_root,
                        check=False,  # Don't fail if source already exists
                    )
                else:
                    console.print("[yellow]Warning: Poetry not found in PATH[/yellow]")
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Could not configure TestPyPI source: {e}[/yellow]"
                )

            # Validate poetry executable exists for update commands
            poetry_path = shutil.which("poetry")
            if not poetry_path:
                raise FileNotFoundError("Poetry executable not found in PATH")

            if version:
                update_cmd = [
                    poetry_path,
                    "add",
                    "--source",
                    "test-pypi",
                    f"fast-clean-architecture=={version}",
                ]
                action_desc = f"update to version {version} from TestPyPI"
            else:
                update_cmd = [
                    poetry_path,
                    "add",
                    "--source",
                    "test-pypi",
                    "fast-clean-architecture@latest",
                ]
                action_desc = "update to latest version from TestPyPI"
        else:
            # Validate poetry executable exists for update commands
            poetry_path = shutil.which("poetry")
            if not poetry_path:
                raise FileNotFoundError("Poetry executable not found in PATH")

            if version:
                update_cmd = [poetry_path, "add", f"fast-clean-architecture=={version}"]
                action_desc = f"update to version {version}"
            else:
                update_cmd = [poetry_path, "update", "fast-clean-architecture"]
                action_desc = "update to latest version"

        if dry_run:
            console.print(
                f"[yellow]Dry run:[/yellow] Would {action_desc} using '{' '.join(update_cmd)}'"
            )
            if test_pypi:
                console.print(
                    "[dim]Note: TestPyPI source will be configured automatically if needed[/dim]"
                )
            return

        # Update the package
        try:
            if test_pypi:
                console.print(
                    "[blue]Configuring TestPyPI source and updating fast-clean-architecture...[/blue]"
                )
            else:
                console.print("[blue]Updating fast-clean-architecture...[/blue]")
            result = subprocess.run(  # nosec B603 # Controlled subprocess call with validated executable
                update_cmd, capture_output=True, text=True, cwd=project_root, check=True
            )

            # Get new version
            # poetry_path already validated above
            result = subprocess.run(  # nosec B603 # Controlled subprocess call with validated executable
                [poetry_path, "show", "fast-clean-architecture"],
                capture_output=True,
                text=True,
                cwd=project_root,
                check=True,
            )

            lines = result.stdout.strip().split("\n")
            new_version = None
            for line in lines:
                if line.startswith("version"):
                    new_version = line.split(":")[1].strip()
                    break

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout or "Unknown error"
            if test_pypi and "not found" in error_msg.lower():
                console.print(
                    "[red]Error:[/red] Package version not found on TestPyPI."
                )
                console.print(
                    "[yellow]Tip:[/yellow] TestPyPI may not have all versions. Try without --test-pypi for stable releases."
                )
            else:
                console.print(
                    f"[red]Error:[/red] Failed to update package: {error_msg}"
                )
            return

        if new_version and new_version != current_version:
            console.print(
                f"[green]✅ Package updated:[/green] {current_version} → {new_version}"
            )
        elif new_version == current_version:
            console.print(f"[yellow]ℹ️  Already up to date:[/yellow] {current_version}")
        else:
            console.print(
                "[green]✅ Package updated successfully[/green] (version detection unavailable)"
            )

        # Verify the update works
        try:
            # Validate python executable exists
            python_path = shutil.which("python") or shutil.which("python3")
            if not python_path:
                raise FileNotFoundError("Python executable not found in PATH")

            result = subprocess.run(  # nosec B603 # Controlled subprocess call with validated executable
                [
                    python_path,
                    "-c",
                    "import fast_clean_architecture; print(f'Version: {fast_clean_architecture.__version__}')",
                ],
                capture_output=True,
                text=True,
                cwd=project_root,
                check=True,
            )

            loaded_version = result.stdout.strip().split(": ")[1]
            console.print(
                f"[green]✅ Package import verified:[/green] {loaded_version}"
            )

        except Exception as e:
            console.print(f"[yellow]⚠️  Could not verify package import:[/yellow] {e}")

        if verbose:
            console.print(f"[dim]Updated in project: {project_root}[/dim]")

        # Log the package update
        logger.info(
            "Package updated successfully",
            operation="cli_update_package",
            old_version=current_version,
            new_version=new_version or "unknown",
            target_version=version or "latest",
            source=source_info.lower(),
        )

    except Exception as e:
        logger.error(
            "Package update failed",
            operation="cli_update_package",
            error=str(e),
            error_type=type(e).__name__,
            source=source_info.lower(),
        )
        handle_error(e, verbose)


@app.command()
def sync_config(
    systems: Optional[str] = typer.Option(
        None,
        "--systems",
        "-s",
        help="Comma-separated list of systems to sync (e.g., 'user_management,payment')",
    ),
    dry_run: bool = DRY_RUN_OPTION,
    force: bool = FORCE_OPTION,
    verbose: bool = VERBOSE_OPTION,
    config_file: str = CONFIG_PATH_OPTION,
) -> None:
    """Synchronize fca-config.yaml with filesystem structure.

    Scans the project filesystem for FCA-structured components, modules, and systems
    that exist but are not tracked in the configuration file. This is useful when:

    • Files were manually copied into the project
    • Components were created outside of FCA commands
    • Configuration file was lost or corrupted
    • Migrating existing code to FCA structure

    [bold]Examples:[/bold]
      [cyan]fca-scaffold sync-config[/cyan]                           # Sync entire project
      [cyan]fca-scaffold sync-config --dry-run[/cyan]                # Preview changes
      [cyan]fca-scaffold sync-config --systems user_management[/cyan] # Sync specific system
      [cyan]fca-scaffold sync-config --force --verbose[/cyan]        # Force overwrite with details

    [bold]What it does:[/bold]
      • Scans systems/ directory for FCA structure
      • Identifies untracked systems, modules, and components
      • Updates fca-config.yaml with discovered items
      • Creates automatic backups before changes
      • Validates naming conventions and structure

    [bold]Safety features:[/bold]
      • Dry-run mode to preview changes
      • Automatic configuration backups
      • Input validation and sanitization
      • Detailed error reporting
    """
    try:
        project_root = get_project_root()
        config_path = get_config_path(config_file)

        # Check if config file exists
        if not config_path.exists():
            console.print(
                f"[red]Error:[/red] Configuration file not found: {config_path}"
            )
            console.print(
                "[yellow]Hint:[/yellow] Run 'fca-scaffold init' to create a new project"
            )
            raise typer.Exit(1)

        # Parse systems filter
        systems_filter = None
        if systems:
            systems_filter = [s.strip() for s in systems.split(",") if s.strip()]
            if verbose:
                console.print(
                    f"[blue]Filtering systems:[/blue] {', '.join(systems_filter)}"
                )

        # Initialize config updater
        config_updater = ConfigUpdater(config_path)

        # Show initial status
        if verbose:
            console.print(f"[blue]Project root:[/blue] {project_root}")
            console.print(f"[blue]Config file:[/blue] {config_path}")
            console.print(
                f"[blue]Mode:[/blue] {'Dry run' if dry_run else 'Live update'}"
            )

        console.print("\n[bold blue]🔍 Scanning project structure...[/bold blue]")

        # Perform sync
        sync_results = config_updater.sync_config(
            project_root=project_root,
            dry_run=dry_run,
            systems_filter=systems_filter,
            force=force,
            verbose=verbose,
        )

        # Display results
        console.print("\n[bold green]📊 Sync Results[/bold green]")

        if sync_results["errors"]:
            console.print("\n[bold red]❌ Errors:[/bold red]")
            for error in sync_results["errors"]:
                console.print(f"  • {error}")

        if sync_results["changes"]:
            console.print(
                f"\n[bold yellow]{'📋 Planned Changes:' if dry_run else '✅ Changes Made:'}[/bold yellow]"
            )
            for change in sync_results["changes"]:
                console.print(f"  • {change}")
        else:
            console.print(
                "\n[green]✅ No changes needed - configuration is up to date[/green]"
            )

        if sync_results["skipped"]:
            console.print("\n[bold yellow]⏭️  Skipped (already exists):[/bold yellow]")
            for skipped in sync_results["skipped"]:
                console.print(f"  • {skipped}")

        # Summary statistics
        console.print("\n[bold blue]📈 Summary:[/bold blue]")
        console.print(
            f"  • Systems {'would be ' if dry_run else ''}added: {sync_results['systems_added']}"
        )
        console.print(
            f"  • Modules {'would be ' if dry_run else ''}added: {sync_results['modules_added']}"
        )
        console.print(
            f"  • Components {'would be ' if dry_run else ''}added: {sync_results['components_added']}"
        )
        console.print(f"  • Errors encountered: {len(sync_results['errors'])}")

        if dry_run and (
            sync_results["systems_added"] > 0
            or sync_results["modules_added"] > 0
            or sync_results["components_added"] > 0
        ):
            console.print(
                "\n[yellow]💡 Run without --dry-run to apply these changes[/yellow]"
            )

        if not dry_run and (
            sync_results["systems_added"] > 0
            or sync_results["modules_added"] > 0
            or sync_results["components_added"] > 0
        ):
            console.print(
                "\n[green]✅ Configuration synchronized successfully![/green]"
            )
            console.print("[dim]💾 Automatic backup created before changes[/dim]")

        # Log the sync operation
        logger.info(
            "Config sync completed",
            operation="cli_sync_config",
            dry_run=dry_run,
            systems_filter=systems_filter,
            force=force,
            systems_added=sync_results["systems_added"],
            modules_added=sync_results["modules_added"],
            components_added=sync_results["components_added"],
            errors_count=len(sync_results["errors"]),
        )

    except Exception as e:
        logger.error(
            "Config sync failed",
            operation="cli_sync_config",
            error=str(e),
            error_type=type(e).__name__,
        )
        handle_error(e, verbose)


@app.command()
def version() -> None:
    """Show version information.

    Displays the current version of Fast Clean Architecture scaffolding tool
    along with author information.

    [bold]Example:[/bold]
      [cyan]fca-scaffold version[/cyan]

    [bold]Useful for:[/bold]
      • Checking which version you're running
      • Bug reports and support requests
      • Ensuring compatibility with documentation
    """
    from . import __author__, __version__

    console.print(
        Panel.fit(
            f"[bold]Fast Clean Architecture[/bold]\n"
            f"Version: {__version__}\n"
            f"Author: {__author__}",
            title="Version Information",
        )
    )


@app.command()
def system_status(
    verbose: bool = VERBOSE_OPTION,
) -> None:
    """Show system status, health, and usage analytics.

    Displays comprehensive information about:
    - System health and resource usage
    - Error tracking summary
    - Usage analytics and productivity metrics

    [bold]Examples:[/bold]
      [cyan]fca-scaffold system-status[/cyan]
      [cyan]fca-scaffold system-status --verbose[/cyan]
    """
    try:
        from .analytics import get_analytics
        from .error_tracking import get_error_tracker
        from .health import get_health_monitor

        console.print("\n[bold blue]📊 Fast Clean Architecture Status[/bold blue]\n")

        # FCA System Health
        console.print("[bold yellow]🏥 FCA System Health[/bold yellow]")
        health_monitor = get_health_monitor()
        health_data = health_monitor.get_system_health()

        if "error" in health_data:
            console.print(f"[red]❌ Health check failed: {health_data['error']}[/red]")
        else:
            process_data = health_data.get("process", {})

            console.print(
                f"  • Memory Usage: {process_data.get('memory_rss_mb', 0):.1f} MB ({process_data.get('memory_percent', 0):.1f}%)"
            )
            console.print(f"  • CPU Usage: {process_data.get('cpu_percent', 0):.1f}%")
            console.print(
                f"  • Session Duration: {health_data.get('uptime_seconds', 0):.1f} seconds"
            )

        # Error Tracking
        console.print("\n[bold yellow]🐛 Error Tracking[/bold yellow]")
        error_tracker = get_error_tracker()
        error_summary = error_tracker.get_error_summary()

        console.print(f"  • Total Errors: {error_summary.get('total_errors', 0)}")
        console.print(f"  • Unique Errors: {error_summary.get('unique_errors', 0)}")

        if error_summary.get("most_common_errors"):
            console.print("  • Most Common Errors:")
            for error_info in error_summary["most_common_errors"][:3]:
                console.print(
                    f"    - {error_info['signature']}: {error_info['count']} times"
                )

        # Usage Analytics
        console.print("\n[bold yellow]📈 Usage Analytics[/bold yellow]")
        analytics = get_analytics()
        usage_summary = analytics.get_usage_summary()
        productivity = analytics.get_productivity_metrics()

        session_data = usage_summary.get("session", {})
        console.print(
            f"  • Session Duration: {session_data.get('duration_seconds', 0):.1f} seconds"
        )
        console.print(f"  • Total Commands: {session_data.get('total_commands', 0)}")
        console.print(
            f"  • Components Created: {productivity.get('components_created', 0)}"
        )
        console.print(
            f"  • Components/Hour: {productivity.get('components_per_hour', 0):.1f}"
        )

        if usage_summary.get("commands"):
            console.print("  • Command Usage:")
            for command, count in list(usage_summary["commands"].items())[:3]:
                console.print(f"    - {command}: {count} times")

        if usage_summary.get("component_types"):
            console.print("  • Popular Component Types:")
            for comp_type, count in list(usage_summary["component_types"].items())[:3]:
                console.print(f"    - {comp_type}: {count} times")

        if verbose:
            # Show detailed information
            console.print("\n[bold yellow]🔍 Detailed Information[/bold yellow]")

            if usage_summary.get("layers"):
                console.print("  • Layer Usage:")
                for layer, count in usage_summary["layers"].items():
                    console.print(f"    - {layer}: {count} times")

            if usage_summary.get("systems"):
                console.print("  • System Usage:")
                for system, count in usage_summary["systems"].items():
                    console.print(f"    - {system}: {count} times")

            if usage_summary.get("performance"):
                console.print("  • Performance Metrics:")
                for command, perf in usage_summary["performance"].items():
                    console.print(
                        f"    - {command}: avg {perf['average_ms']}ms (min: {perf['min_ms']}ms, max: {perf['max_ms']}ms)"
                    )

        console.print("\n[green]✅ Status check completed[/green]")

        # Log the status check
        logger.info(
            "System status command executed",
            operation="cli_system_status",
            verbose=verbose,
        )

    except Exception as e:
        logger.error(
            "System status command failed",
            operation="cli_system_status",
            error=str(e),
            error_type=type(e).__name__,
        )
        handle_error(e, verbose)


if __name__ == "__main__":
    # Ensure logging is configured
    configure_logging()
    app()
