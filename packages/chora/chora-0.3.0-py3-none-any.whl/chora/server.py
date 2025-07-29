#!/usr/bin/env python3
"""
chora server implementation.
"""

import atexit
import logging
from functools import partial
from http.server import HTTPServer
from pathlib import Path

from .handler import create_handler

logger = logging.getLogger(__name__)


def cleanup(server: HTTPServer) -> None:
    logger.info("Shutting down server...")
    try:
        server.shutdown()
    except Exception as e:
        logger.warning("Error during server shutdown: %s", e)

    try:
        server.server_close()
    except Exception as e:
        logger.warning("Error during server close: %s", e)


def start_server(root_path: Path, host: str, port: int) -> None:
    """Start the HTTP server with the given configuration.

    Args:
        root_path: Path to the root directory for mock responses
        host: Host to bind the server to
        port: Port to run the server on
    """
    handler = create_handler(root_path)
    server = HTTPServer((host, port), handler)

    atexit.register(partial(cleanup, server))

    server.serve_forever()
