#!/usr/bin/env python3
from aiohttp import web

from .routes import setup_routes


def serve(host, port, debug=True):
    app = web.Application(debug=debug)
    setup_routes(app)
    web.run_app(app, host=host, port=port)
