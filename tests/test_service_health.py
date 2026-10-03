"""Integration health checks for the services used by the test environment."""

import os
import socket
from urllib.parse import urlsplit

import pytest


def test_postgres_health():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is not set")

    psycopg = pytest.importorskip("psycopg")
    with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)


def test_redis_health():
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        pytest.skip("REDIS_URL is not set")

    parsed_url = urlsplit(redis_url)
    with socket.create_connection((parsed_url.hostname, parsed_url.port or 6379), timeout=5) as connection:
        connection.sendall(b"*1\r\n$4\r\nPING\r\n")
        response = b""
        while not response.endswith(b"\r\n"):
            response += connection.recv(1)
        assert response == b"+PONG\r\n"
