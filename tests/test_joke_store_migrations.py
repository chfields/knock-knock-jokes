"""Tests for built-in catalogue migration declarations."""

from knockknock.joke_store import BUILTIN_JOKE_MIGRATIONS


def test_builtin_joke_migrations_include_nacho():
    assert ("2026-11-06-add-nacho", ("nacho",)) in BUILTIN_JOKE_MIGRATIONS
