"""Packaging compatibility tests."""

from importlib.metadata import metadata
from pathlib import Path


def test_postgres_test_dependencies_keep_python_39_compatible_bounds():
    """Python 3.9 must not resolve PostgreSQL releases that require Python 3.10."""
    dependencies = metadata("knock-knock-jokes").get_all("Requires-Dist") or []

    for package in ("psycopg[binary]", "psycopg-pool"):
        assert any(
            dependency.startswith(package)
            and ">=3.2" in dependency
            and "<3.3" in dependency
            and 'python_version < "3.10"' in dependency
            for dependency in dependencies
        )


def test_vercel_requirements_match_python_39_postgres_bounds():
    """Vercel's PostgreSQL dependencies must support the declared Python floor."""
    requirements = Path("requirements.txt").read_text(encoding="utf-8")

    for package in ("psycopg[binary]", "psycopg-pool"):
        assert f"{package}>=3.2,<3.3 ; python_version < '3.10'" in requirements
