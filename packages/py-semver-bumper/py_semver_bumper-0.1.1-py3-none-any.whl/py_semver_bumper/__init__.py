"""Semantic versioning bumper package."""

import re
from dataclasses import dataclass


@dataclass
class Semver:
    """Semantic version data structure."""

    major: int
    minor: int
    patch: int
    prerelease: str = ""
    buildmetadata: str = ""

    def __str__(self) -> str:
        """Return string representation of semantic version."""
        return (
            f"{self.major}.{self.minor}.{self.patch}"
            f"{'-' if self.prerelease else ''}{self.prerelease}"
            f"{'+' if self.buildmetadata else ''}{self.buildmetadata}"
        )

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"Semver(major={self.major}, minor={self.minor}, "
            f"patch={self.patch}, prerelease={self.prerelease}, "
            f"buildmetadata={self.buildmetadata})"
        )


class SemverBumper:
    """Bump semantic versioning.

    Works with minor, major, and patch bumps.

    Pre-release bumps are not implemented.
    """

    def __init__(self, version: str | Semver) -> None:
        """Initialize with a version string or Semver object."""
        if isinstance(version, Semver):
            self.semver = version
            return

        split = re.split(
            r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$",
            version,
        )
        self.semver = Semver(
            major=int(split[1]),
            minor=int(split[2]),
            patch=int(split[3]),
            prerelease=split[4] or "",
            buildmetadata=split[5] or "",
        )

    def patch(self) -> Semver:
        """Bump patch version."""
        s = self.semver
        s.patch += 1
        self.semver = s
        return s

    def minor(self) -> Semver:
        """Bump minor version."""
        s = self.semver
        s.minor += 1
        s.patch = 0
        self.semver = s
        return s

    def major(self) -> Semver:
        """Bump major version."""
        s = self.semver
        s.major += 1
        s.minor = 0
        s.patch = 0
        self.semver = s
        return s

    def prerelease(self) -> Semver:
        """Bump prerelease version.

        Not implemented.
        """
        msg = "Pre-release bumping is not implemented"
        raise NotImplementedError(msg)
