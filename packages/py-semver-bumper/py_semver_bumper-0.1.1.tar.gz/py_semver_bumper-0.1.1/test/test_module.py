# ruff: noqa: S101 D100 S603 ANN201 ANN001
import subprocess
import sys


def test_module_patch_bump_pyproject(temp_pyproject, monkeypatch):
    """Test the main module with a basic patch bump."""
    temp_dir = temp_pyproject(version="1.2.3")
    monkeypatch.chdir(temp_dir)

    # Test the module by running it as a subprocess
    result = subprocess.run(
        [sys.executable, "-m", "py_semver_bumper", "patch"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "1.2.4" in result.stdout


def test_module_minor_bump_pyproject(temp_pyproject, monkeypatch):
    """Test the main module with a custom version from pyproject.toml."""
    temp_dir = temp_pyproject(version="1.2.3")
    monkeypatch.chdir(temp_dir)

    result = subprocess.run(
        [sys.executable, "-m", "py_semver_bumper", "minor"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "1.3.0" in result.stdout


def test_module_major_bump_pyproject(temp_pyproject, monkeypatch):
    """Test the main module with a custom version from pyproject.toml."""
    temp_dir = temp_pyproject(version="1.2.3")
    monkeypatch.chdir(temp_dir)

    result = subprocess.run(
        [sys.executable, "-m", "py_semver_bumper", "major"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "2.0.0" in result.stdout


def test_module_patch_bump_version_arg():
    """Test the main module with explicit version argument."""
    result = subprocess.run(
        [sys.executable, "-m", "py_semver_bumper", "patch", "--version", "2.1.3"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "2.1.4" in result.stdout


def test_module_invalid_bump_type():
    """Test the main module with invalid bump type."""
    result = subprocess.run(
        [sys.executable, "-m", "py_semver_bumper", "invalid", "--version", "1.0.0"],
        capture_output=True,
        text=True,
    )

    # argparse returns 2 for invalid arguments
    assert result.returncode == 2
    assert "invalid choice: 'invalid'" in result.stderr
