# ruff: noqa: D103 D100 ANN201 S101
from py_semver_bumper import SemverBumper


def test_semver_bumper_basic():
    bumper = SemverBumper("1.0.0")
    assert str(bumper.patch()) == "1.0.1"
    assert str(bumper.minor()) == "1.1.0"
    assert str(bumper.major()) == "2.0.0"
