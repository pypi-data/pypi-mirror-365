# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

### Security

## [1.4.2]

### Changed
- **CLI Simplification**: Removed `help-guide` command and merged its comprehensive help content into the main `--help` command for better user experience
- Updated Python version requirement from 3.8+ to 3.9+ across all documentation
- Enhanced main help output with detailed command descriptions and examples

### Fixed
- Resolved failing test `test_help_guide_command` by updating it to `test_main_help_command` to reflect CLI changes
- Updated CLI reference documentation to remove obsolete `help-guide` command references

## [1.4.1]

### Added
- **sync-config command**: New `sync-config` command to synchronize `fca_config.yaml` with filesystem structure
  - Scans project filesystem for FCA-structured components, modules, and systems
  - Identifies untracked items that exist but aren't in configuration
  - Updates configuration with discovered items automatically
  - Supports selective syncing with `--systems` option
  - Includes dry-run mode for previewing changes
  - Creates automatic backups before making changes
  - Validates naming conventions and structure during sync
- Enhanced CLI help system with comprehensive `help-guide` command
- Improved project monitoring with detailed `system-status` command
- Advanced configuration management with `config show` and `config validate` subcommands

### Changed
- Updated CLI reference documentation to include all available commands
- Enhanced error handling and validation across all commands
- Improved template validation and security features

### Fixed
- Configuration synchronization issues when files are manually created
- Missing documentation for several CLI commands
- Template validation edge cases

### Security
- Enhanced path validation in sync operations
- Improved input sanitization for configuration management

## [1.3.0]

### Added
- Introduced the create-scalable-baseline command to the Fast Clean Architecture (FCA) CLI tool, enabling developers to generate complete FastAPI projects with Clean Architecture principles from a single command.

### Changed
- Upgraded pytest-asyncio from ^0.21.0 to ^0.23.0 for better async test support and configuration compatibility

### Fixed
- Fixed recurring PytestConfigWarning for "Unknown config option: asyncio_default_fixture_loop_scope" by upgrading pytest-asyncio to version 0.23.0 which supports this configuration option
- Resolved "yo-yo" behavior in pytest-asyncio configuration where the asyncio_default_fixture_loop_scope option was alternately recognized and unrecognized
- Added proper asyncio_default_fixture_loop_scope = "function" configuration in pyproject.toml for consistent async test fixture behavior

## [1.2.0]

### Added
- **Dependency Manager Choice**: New `--dependency-manager` (`--deps`) option for `create-scalable-baseline` command
  - Support for Poetry (default) and Pip dependency managers
  - Generates appropriate configuration files (pyproject.toml for Poetry, requirements.txt for Pip)
  - Dynamic README templates with manager-specific setup instructions
- New `migrate-to-api-versioning` command for migrating existing modules to versioned API structure
- Enhanced folder structure with API versioning support (v1, v2, v3 directories)
- Additional organizational folders: events, exceptions, interfaces, dtos, use_cases, config, database, middleware, migrations
- Module API entry point files (`{module_name}_module_api.py`) for better module organization
### Changed
- **BREAKING**: Updated folder structure to support API versioning in presentation layer
- Presentation layer now includes versioned controllers, routes, and schemas directories
- Application layer restructured with separate dtos and use_cases folders
- Infrastructure layer enhanced with config and database subdirectories
- Domain layer expanded with events, exceptions, and interfaces folders
### Fixed
- Fixed TOML parse error in pyproject.toml template caused by invalid escape sequence in Black configuration
- Improved error handling for dependency manager validation
### Security

## [1.1.2]

### Added
- Comprehensive template validation system
- Robust error handling with rollback mechanisms
- Timestamped configuration backups with cleanup
- Enhanced template variables for better code generation
- Security tools integration (bandit, safety)
- Improved entity and service templates with validation
- Type hints and metadata in generated code
- Atomic file operations for configuration management
- Analytics and error tracking modules
- Health monitoring and metrics collection
- Structured logging with configurable levels
- File locking mechanisms for concurrent operations
- Enhanced CLI commands (batch-create, help-guide, system-status)

### Changed
- Repository templates now use proper abstract base classes
- Enhanced dependency version constraints for security
- Improved template variable consistency across components
- Better error messages and validation feedback
- Updated documentation with comprehensive examples
- Python version requirement updated to >=3.9
- Improved project structure with better separation of concerns

### Fixed
- Template rendering validation issues
- File system permission checks
- Configuration backup and restore mechanisms
- Import path generation in templates
- Timestamp format validation
- **create-module command**: Implemented fail-fast validation to prevent creating modules in non-existent systems, avoiding inconsistent state between file system and configuration
- Version synchronization across project files

### Security
- Added dependency vulnerability scanning
- Implemented secure file operations
- Enhanced input validation and sanitization
- **CRITICAL**: Fixed 3 security vulnerabilities in dependencies:
  - Updated black to ^24.3.0 to fix CVE-2024-21503 (ReDoS vulnerability)
  - Added pip ^25.0 constraint to fix PVE-2025-75180 (malicious wheel execution)
  - Added setuptools ^78.1.1 constraint to fix CVE-2025-47273 (path traversal)
- Resolved all Bandit security warnings with proper fixes and suppressions
- Replaced MD5 hashing with SHA256 for error ID generation
- Enabled Jinja2 autoescape to prevent XSS vulnerabilities
- Replaced assert statements with proper exception handling
- Implemented secure template validation and sanitization

## [1.1.1]

### Fixed
- Minor bug fixes and stability improvements
- Documentation updates

## [1.1.0]

### Added
- Enhanced template system with validation
- Improved error handling mechanisms
- Additional CLI functionality

### Changed
- Performance optimizations
- Code quality improvements

## [1.0.0]

### Added
- Production-ready release
- Comprehensive test coverage
- Full documentation
- Stable API

### Changed
- Upgraded from beta to stable release
- Enhanced reliability and performance

## [0.1.0]

### Added
- Initial release of Fast Clean Architecture
- CLI tool for scaffolding clean architecture projects
- Support for system contexts and modules
- Component generation for all architecture layers:
  - Domain: entities, repositories, value objects
  - Application: services, commands, queries
  - Infrastructure: models, repository implementations, external services
  - Presentation: API routers, schemas
- YAML-based project configuration management
- Jinja2 template system for code generation
- Rich CLI interface with progress indicators
- Comprehensive test suite
- Type hints throughout the codebase
- Documentation and examples

### Features
- **Project Initialization**: Create new clean architecture projects
- **System Contexts**: Organize code into logical bounded contexts
- **Module Management**: Create modules within system contexts
- **Component Generation**: Generate boilerplate code for all layers
- **Configuration Tracking**: Track project structure in `fca-config.yaml`
- **Template Customization**: Customize generated code templates
- **Validation**: Input validation and conflict detection
- **Dry Run Mode**: Preview changes before applying them
- **Force Mode**: Overwrite existing files when needed

### Technical Details
- Built with Python 3.9+ support
- Uses Typer for CLI interface
- Pydantic for configuration validation
- Jinja2 for template rendering
- Rich for beautiful terminal output
- Comprehensive error handling
- Full type annotations
- Extensive test coverage

### Documentation
- Comprehensive README with examples
- API documentation in docstrings
- CLI help system
- Architecture guidelines
- Template customization guide

[Unreleased]: https://github.com/alden-technologies/fast-clean-architecture/compare/v1.4.2...HEAD
[1.4.2]: https://github.com/alden-technologies/fast-clean-architecture/compare/v1.4.1...v1.4.2
[1.4.1]: https://github.com/alden-technologies/fast-clean-architecture/compare/v1.3.0...v1.4.1
[1.3.0]: https://github.com/alden-technologies/fast-clean-architecture/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/alden-technologies/fast-clean-architecture/compare/v1.1.2...v1.2.0
[1.1.2]: https://github.com/alden-technologies/fast-clean-architecture/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/alden-technologies/fast-clean-architecture/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/alden-technologies/fast-clean-architecture/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/alden-technologies/fast-clean-architecture/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/alden-technologies/fast-clean-architecture/releases/tag/v0.1.0