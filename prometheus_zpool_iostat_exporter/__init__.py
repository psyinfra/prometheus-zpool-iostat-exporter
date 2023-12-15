import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger('prometheus_zpool_iostat_exporter')

VERSION = '0.1.0'  # Project version
DEFAULT_PORT = 10007  # Default port used by the zpool-iostat-exporter
EXPORTER_PREFIX = 'zpool_iostat'  # Name prefix for exported metrics

__all__ = [logger, DEFAULT_PORT, EXPORTER_PREFIX, VERSION]
