import argparse
import logging
import time
import urllib.parse

from prometheus_client import start_http_server, REGISTRY

from . import logger, DEFAULT_PORT
from .exporter import ZPoolIOStatExporter


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            'A Python-based Prometheus exporter for logical I/O statistics '
            'for ZFS storage pools'))
    parser.add_argument(
        '-w', '--web.listen-address',
        dest='listen_address',
        required=False,
        type=str,
        default=f':{DEFAULT_PORT}',
        help=f'Address and port to listen on (default = :{DEFAULT_PORT})')
    parser.add_argument(
        '--latency',
        dest='latency',
        default=False,
        action='store_true',
        help='Include average latency statistics (see: zpool iostat -l)')
    parser.add_argument(
        '--queue',
        dest='queue',
        default=False,
        action='store_true',
        help='Include active queue statistics (see: zpool iostat -q)')
    parser.add_argument(
        '-l', '--log',
        dest='log_level',
        required=False,
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='WARNING',
        help='Specify logging level')
    return parser.parse_args()


def main():
    args = parse_args()
    logger.setLevel(args.log_level)
    logger.info(f'Log level: {logging.getLevelName(logger.level)}')

    try:
        listen_addr = urllib.parse.urlsplit(f'//{args.listen_address}')
        addr = listen_addr.hostname if listen_addr.hostname else '0.0.0.0'
        port = listen_addr.port if listen_addr.port else DEFAULT_PORT
        REGISTRY.register(ZPoolIOStatExporter(
            latency=args.latency,
            queue=args.queue))
        start_http_server(port, addr=addr)
        logger.info(f'Listening on {listen_addr.netloc}')
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
        exit(0)
    except Exception as exc:
        logger.error(exc)
        logger.critical(
            'Exporter shut down due while starting the server. Please contact '
            'your administrator.')
        exit(1)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
        exit(0)
    except Exception as exc:
        logger.error(exc)
        logger.critical(
            'Exporter shut down unexpectedly. Please contact your '
            'administrator.')
        exit(1)
