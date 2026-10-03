"""Health checks for optional local services."""

import os
import socket
from urllib.parse import urlparse

import pytest


def _read_redis_response(connection):
    """Read a complete Redis response, failing if the peer closes early."""
    response = b""
    while not response.endswith(b"\r\n"):
        chunk = connection.recv(1024)
        if not chunk:
            pytest.fail("Redis closed the connection before sending PONG")
        response += chunk
    return response


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
        assert _read_redis_response(connection) == b"+PONG\r\n"


def test_read_redis_response_fails_when_peer_closes_early():
    """A truncated Redis response fails instead of looping forever."""

    class EarlyClosingSocket:
        def __init__(self):
            self.recv_sizes = []
            self.responses = iter((b"+PO", b""))

        def recv(self, size):
            self.recv_sizes.append(size)
            return next(self.responses)

    connection = EarlyClosingSocket()

    with pytest.raises(
        pytest.fail.Exception,
        match="Redis closed the connection before sending PONG",
    ):
        _read_redis_response(connection)

    assert connection.recv_sizes == [1024, 1024]
