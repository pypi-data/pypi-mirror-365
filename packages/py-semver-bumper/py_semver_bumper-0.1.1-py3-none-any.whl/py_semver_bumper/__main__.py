#!/usr/bin/env python3
"""Command-line interface for py-semver-bumper.

Usage:
    python -m py_semver_bumper [patch|minor|major|prerelease] [options]

Examples:
    python -m py_semver_bumper patch
    python -m py_semver_bumper minor --update
    python -m py_semver_bumper major -v 1.2.3

"""

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from pyproject_parser import PyProject

from . import SemverBumper


def parse_args() -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        help=(
            "The version to bump. If not provided, the version in "
            "pyproject.toml will be used"
        ),
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Update the pyproject.toml file with the new version",
    )
    parser.add_argument(
        "bump_type",
        help="The type of bump to perform",
        choices=["patch", "minor", "major", "prerelease"],
    )
    return parser.parse_args()


def get_pyproject_path(base_path: Path | None = None) -> Path | None:
    """Find pyproject.toml file in current or parent directories."""
    if base_path is None:
        base_path = Path.cwd()

    if base_path == Path("/"):
        return None
    if Path(base_path, "pyproject.toml").exists():
        return Path(base_path, "pyproject.toml")
    return get_pyproject_path(base_path.parent)


def calculate_version(current: str, bump_type: str) -> str:
    """Calculate the new version based on the current version and the bump type."""
    try:
        bumper = SemverBumper(current)

        match bump_type:
            case "patch":
                result = bumper.patch()
            case "minor":
                result = bumper.minor()
            case "major":
                result = bumper.major()
            case "prerelease":
                result = bumper.prerelease()
            case _:
                print(f"Error: Unknown bump type '{bump_type}'", file=sys.stderr)
                print(
                    "Valid bump types: patch, minor, major, prerelease", file=sys.stderr
                )
                sys.exit(1)

        return str(result)

    except (ValueError, NotImplementedError) as e:
        print(f"Failed to calculate version: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Entrypoint."""
    args = parse_args()

    # If the version is not provided, try to load the version from pyproject.toml
    if args.version is None:
        pyproject_path = get_pyproject_path()
        if pyproject_path is not None:
            try:
                pyproject = PyProject.load(pyproject_path)
                current_version = str(pyproject.project["version"])
            except (ValueError, KeyError, FileNotFoundError) as e:
                print(f"Failed to load pyproject.toml: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(
                "Error: No pyproject.toml found and no version provided",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        current_version = args.version

    bump_type = args.bump_type.lower()

    new_version = calculate_version(current_version, bump_type)

    if args.update:
        pyproject.project["version"] = new_version
        pyproject.dump(pyproject_path)

    print(new_version)


if __name__ == "__main__":
    main()
