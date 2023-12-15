import subprocess
from typing import Type

from prometheus_client import Summary
from prometheus_client.core import GaugeMetricFamily

from . import iostat, logger, EXPORTER_PREFIX

# Measure collection time
REQUEST_TIME = Summary(
    f'{EXPORTER_PREFIX}_collector_collect_seconds',
    'Time spent to collect metrics from the NTP server')


class ZPoolIOStatExporter:
    def __init__(self, latency: bool = False, queue: bool = False):
        self.latency = latency
        self.queue = queue

    @staticmethod
    def _execute(command: list[str],
                 metrics: list[Type[iostat.Metric]]
                 ) -> dict[Type[iostat.Metric], list[iostat.Metric]]:
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
        except Exception as exc:
            logger.error(f"'{' '.join(command)}' failed: {exc}")
            return {}

        data = stdout.decode('utf-8').strip()
        data = [pool.split('\t') for pool in data.split('\n')]
        return {m: [m(d[0], d[i+1]) for d in data]
                for i, m in enumerate(metrics)}

    def zpool_list(self) -> dict[Type[iostat.Metric], list[iostat.Metric]]:
        """
        Lists all pools along with a health status and space usage.

        -H: scripted mode; -p: displays numbers in (exact) values. The last
        given property is 'altroot', which is ignored.
        """
        command = ['zpool', 'list', '-H', '-p']
        metrics = [
            iostat.Size,
            iostat.Alloc,
            iostat.Free,
            iostat.CkPoint,
            iostat.ExpandSz,
            iostat.Frag,
            iostat.Cap,
            iostat.Dedup,
            iostat.Health]
        return self._execute(command, metrics)

    def zpool_iostat(self,
                     latency: bool = False,
                     queue: bool = False
                     ) -> dict[Type[iostat.Metric], list[iostat.Metric]]:
        """
        Request a list of pools and their associated properties.

        -H: scripted mode; -p: displays numbers in (exact) values. The last
        given property is 'altroot', which is ignored. If `include_latency` is
        True, then the -l argument is added to include average latency
        statistics.
        """
        command = ['zpool', 'iostat', '-H', '-p']
        metrics = [
            iostat.CapacityAlloc,
            iostat.CapacityFree,
            iostat.OperationsRead,
            iostat.OperationsWrite,
            iostat.BandwidthRead,
            iostat.BandwidthWrite]

        if latency:
            command.append('-l')
            metrics.extend([
                iostat.TotalWaitRead,
                iostat.TotalWaitWrite,
                iostat.DiskWaitRead,
                iostat.DiskWaitWrite,
                iostat.SyncQWaitRead,
                iostat.SyncQWaitWrite,
                iostat.AsyncQWaitRead,
                iostat.AsyncQWaitWrite,
                iostat.Scrub,
                iostat.Trim])

        if queue:
            command.append('-q')
            metrics.extend([
                iostat.SyncQReadPend,
                iostat.SyncQReadActiv,
                iostat.SyncQWritePend,
                iostat.SyncQWriteActiv,
                iostat.ASyncQReadPend,
                iostat.ASyncQReadActiv,
                iostat.ASyncQWritePend,
                iostat.ASyncQWriteActiv,
                iostat.ScrubQPending,
                iostat.ScrubQActiv,
                iostat.TrimQPend,
                iostat.TrimQActiv])

        return self._execute(command, metrics)

    @REQUEST_TIME.time()
    def collect(self):
        data = self.zpool_list() | self.zpool_iostat(self.latency, self.queue)

        for family, metrics in data.items():
            g = GaugeMetricFamily(
                name=family.name,
                labels=['pool'],
                documentation=family.doc)

            for metric in metrics:
                if metric.value is not None:
                    g.add_metric([metric.pool], metric.value)

            yield g
