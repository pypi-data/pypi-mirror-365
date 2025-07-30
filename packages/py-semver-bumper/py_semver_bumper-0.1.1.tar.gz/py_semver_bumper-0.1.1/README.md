# py-semver-bumper

A Python command-line tool for bumping semantic versions with support for patch, minor, and major version increments.

## Features

- **Semantic Versioning Support**: Handles standard semver format (`MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`)
- **Multiple Bump Types**: Support for patch, minor and major bumps
- **pyproject.toml Integration**: Automatically reads and updates version from `pyproject.toml`
- **Command Line Interface**: Easy-to-use CLI with clear options

## Installation

### From PyPI (Recommended)

```bash
# Install using pip
pip install py-semver-bumper

# Or using uv
uv add py-semver-bumper
```

## Usage

### Command Line Interface

The tool can be used as a module or installed as a command-line tool.

#### Basic Usage

```bash
# Bump patch version (reads from pyproject.toml)
py-semver-bumper patch

# Bump minor version with specific version
py-semver-bumper minor -v 1.2.3

# Bump major version and update pyproject.toml
py-semver-bumper major --update
```

#### Options

- `-v, --version`: Specify the version to bump (if not provided, reads from pyproject.toml)
- `-u, --update`: Update the pyproject.toml file with the new version
- `bump_type`: The type of bump to perform (patch, minor, major, prerelease)

#### Examples

```bash
# Output new version without updating files
py-semver-bumper patch
# Output: 1.0.1

# Update pyproject.toml with new version
py-semver-bumper minor --update
# Output: 1.1.0

# Use specific version
py-semver-bumper major -v 2.1.0
# Output: 3.0.0
```

### Programmatic Usage

```python
from py_semver_bumper import SemverBumper

# Create bumper with version string
bumper = SemverBumper("1.2.3")

# Bump versions
new_patch = bumper.patch()    # 1.2.4
new_minor = bumper.minor()    # 1.3.0
new_major = bumper.major()    # 2.0.0

# Convert to string
print(str(new_patch))  # "1.2.4"
```

### Automating Releases with GitHub CLI

You can automate the release process using GitHub CLI. Here are some examples:

#### Simple Release Script

```bash
#!/bin/bash

BUMP_TYPE=${1:-patch}  # Default to patch if no argument provided

# Bump version and update pyproject.toml
NEW_VERSION=$(py-semver-bumper $BUMP_TYPE --update)

# Commit the version bump
git add pyproject.toml
git commit -m "Bump version to $NEW_VERSION"

# Push to remote
git push origin main

# Create GitHub release
gh release create $NEW_VERSION --title "Release $NEW_VERSION" --generate-notes
```

#### One-liner for Quick Releases

```bash
# Bump patch version, commit, push, and create release
NEW_VERSION=$(py-semver-bumper patch --update) && \
git add pyproject.toml && \
git commit -m "Bump version to $NEW_VERSION" && \
git push origin main && \
gh release create $NEW_VERSION --title "Release $NEW_VERSION" --generate-notes
```

#### Just command

You can add this to your `justfile` to automate the release process.

```text
release bump='patch':
    #!/bin/sh
    export NEW_VERSION=$(py-semver-bumper {{ bump }} --update)
    git add pyproject.toml
    git commit -m "Bump version to $NEW_VERSION"
    git push origin main
    gh release create $NEW_VERSION --title "Release $NEW_VERSION" --generate-notes
```

## Development

This project uses [Just](https://github.com/astral-sh/just) for task management. Run `just` to see all available commands.

The project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting and [Ty](https://github.com/astral-sh/ty) for type checking:

- **Lint**: `just lint`
- **Format**: `just format`
- **Type Check**: `just typecheck`

Tests are written using [pytest](https://pytest.org/):

- **Run Unit Tests**: `just pytest`

## Roadmap

- [ ] Implement prerelease version bumping
- [ ] Add support for build metadata
- [ ] Add validation for semver format
- [ ] Add support for other version file formats (setup.py, etc.)
- [ ] Add dry-run mode
- [ ] Add interactive mode for version selection
