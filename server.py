#!/usr/bin/env python3
from argparse import ArgumentParser
from app.main import serve


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8080)

    args = parser.parse_args()

    serve(args.host, args.port, args.debug)
