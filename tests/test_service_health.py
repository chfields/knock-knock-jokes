"""Health checks for optional local services."""

import os
import socket
from urllib.parse import urlparse

import pytest


def test_postgres_health_check():
    """PostgreSQL accepts a simple query when it is configured."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is not set")

    import psycopg

    with psycopg.connect(database_url) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)


def test_redis_health_check():
    """Redis responds to PING when it is configured."""
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        pytest.skip("REDIS_URL is not set")

    parsed_url = urlparse(redis_url)
    with socket.create_connection((parsed_url.hostname, parsed_url.port or 6379)) as connection:
        connection.sendall(b"*1\r\n$4\r\nPING\r\n")
        assert connection.recv(7) == b"+PONG\r\n"
