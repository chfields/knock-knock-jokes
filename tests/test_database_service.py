"""The coding run's PostgreSQL service answers where DATABASE_URL points."""

import os
import socket
import struct
from urllib.parse import urlparse

import pytest

pytestmark = pytest.mark.skipif("DATABASE_URL" not in os.environ, reason="no database service here")


def test_database_url_reaches_postgres():
    url = urlparse(os.environ["DATABASE_URL"])
    assert url.scheme in ("postgres", "postgresql")
    with socket.create_connection((url.hostname, url.port or 5432), timeout=5) as conn:
        # SSLRequest: a real PostgreSQL server answers with a single byte, S or N.
        conn.sendall(struct.pack("!ii", 8, 80877103))
        assert conn.recv(1) in (b"S", b"N")
