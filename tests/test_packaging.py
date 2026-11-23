"""Packaging compatibility tests."""

import sys
from importlib.metadata import metadata, version
from pathlib import Path

import pytest
from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.version import Version

PYTHON_39 = Version("3.9")
FIRST_SUPPORTED_PSYCOPG_VERSION = Version("3.2")
FIRST_UNSUPPORTED_PSYCOPG_VERSION = Version("3.3")
LAST_SUPPORTED_PSYCOPG_VERSION = Version("3.2.13")


def python_39_postgres_requirements(requirements, extra=None):
    """Return PostgreSQL requirements selected for Python 3.9."""
    environment = default_environment()
    environment["python_version"] = "3.9"
    environment["python_full_version"] = "3.9.0"
    if extra is not None:
        environment["extra"] = extra

    return [
        requirement
        for requirement in map(Requirement, (line for line in requirements if not line.startswith("#")))
        if requirement.name in {"psycopg", "psycopg-pool"}
        and (requirement.marker is None or requirement.marker.evaluate(environment))
    ]


def assert_python_39_compatible(requirements):
    """Assert requirements select the last Python-3.9-compatible psycopg line."""
    assert {requirement.name for requirement in requirements} == {"psycopg", "psycopg-pool"}

    for requirement in requirements:
        assert FIRST_SUPPORTED_PSYCOPG_VERSION in requirement.specifier
        assert LAST_SUPPORTED_PSYCOPG_VERSION in requirement.specifier
        assert FIRST_UNSUPPORTED_PSYCOPG_VERSION not in requirement.specifier


def test_postgres_test_dependencies_keep_python_39_compatible_bounds():
    """Python 3.9 must not resolve PostgreSQL releases that require Python 3.10."""
    dependencies = metadata("knock-knock-jokes").get_all("Requires-Dist") or []

    assert_python_39_compatible(python_39_postgres_requirements(dependencies, extra="test"))


def test_vercel_requirements_match_python_39_postgres_bounds():
    """Vercel's PostgreSQL dependencies must support the declared Python floor."""
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()

    assert_python_39_compatible(python_39_postgres_requirements(requirements))


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="Exercises the Python 3.9 CI installation")
def test_installed_postgres_dependencies_support_running_python():
    """The packages installed by the Python 3.9 test job support that interpreter."""
    running_python = Version(".".join(map(str, sys.version_info[:2])))

    for package in ("psycopg", "psycopg-pool"):
        package_metadata = metadata(package)
        assert running_python in Requirement(f"{package}{package_metadata['Requires-Python']}").specifier
        assert PYTHON_39 <= Version(version(package)) < FIRST_UNSUPPORTED_PSYCOPG_VERSION
