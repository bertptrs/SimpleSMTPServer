#!/usr/bin/env python3
import argparse
import socketserver
import signal
import sys

import handlers
from util import eprint


def get_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--port", "-p", help="Local port to bind to", default=2525, type=int)
    parser.add_argument("--host", help="Hostname to bind to", default="localhost")

    return parser.parse_args()


def main():
    args = get_arguments()

    # Enable socket reuse for quicker testing
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.ThreadingTCPServer((args.host, args.port), handlers.SMTPHandler) as server:

        def close_handler(signal, frame):
            eprint("Shutdown requested")
            server.server_close()
            eprint("Shutting down")
            sys.exit(0)
        signal.signal(signal.SIGINT, close_handler)

        server.serve_forever()


if __name__ == '__main__':
    main()
