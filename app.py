"""Vercel entrypoint: the web app configured from the environment."""

import os

from knockknock.web import create_app

if not os.environ.get("KNOCKKNOCK_SECRET_KEY"):
    raise RuntimeError("Set KNOCKKNOCK_SECRET_KEY before serving the deployed web app.")

app = create_app()
