import itertools
import subprocess
from typing import Type

from prometheus_client import Summary
from prometheus_client.core import (
    CounterMetricFamily, GaugeMetricFamily, HistogramMetricFamily)

from . import iostat, logger, EXPORTER_PREFIX

# Measure collection time
REQUEST_TIME = Summary(
    f'{EXPORTER_PREFIX}_collector_collect_seconds',
    'Time spent to collect metrics from the NTP server')


class ZPoolIOStatExporter:
    def __init__(self,
                 pools: list = None,
                 latency: bool = False,
                 queue: bool = False,
                 latency_histogram: bool = False,
                 request_size_histogram: bool = False):
        self.pools = pools if pools is not None else []
        self.latency = latency
        self.queue = queue
        self.latency_histogram = latency_histogram
        self.request_size_histogram = request_size_histogram

    @staticmethod
    def run_cmd(command: list[str]) -> str:
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
        except Exception as exc:
            logger.error(f"'{' '.join(command)}' failed: {exc}")
            return ''

        if stderr:
            # Something is wrong with the command that won't resolve itself
            #   over time.
            raise Exception(
                f"'{' '.join(command)}' failed: "
                f"{stderr.decode('utf-8').strip()}")

        return stdout.decode('utf-8').strip()

    @staticmethod
    def format_output(data: str,
                      metrics: list[Type[iostat.Metric]]
                      ) -> dict[Type[iostat.Metric], list[iostat.Metric]]:
        if not data:
            return {}

        data = [pool.split('\t') for pool in data.split('\n')]
        return {m: [m(d[0], d[i+1]) for d in data]
                for i, m in enumerate(metrics)}

    @staticmethod
    def format_histogram(data: str,
                         metrics: list[Type[iostat.Metric]]
                         ) -> dict[Type[iostat.HistogramMetric],
                                   list[iostat.HistogramMetric]]:
        """
        Parse histogram data by splitting it into pools, transposing the
        histogram table such that each row represents a different metric,
        and outputting them in a structured dataclass.
        """
        if not data:
            return {}

        histograms = {m: [] for m in metrics}

        for pool in data.split('\n\n'):
            lines = list(map(list, itertools.zip_longest(
                *[line.split('\t') for line in pool.split('\n')[1:]],
                fillvalue='NaN')))

            for m, v in zip(metrics, lines[1:]):
                data = m(pool=pool.split('\n')[0], value=v, buckets=lines[0])
                histograms[m].append(data)

        return histograms

    def zpool_list(self) -> dict[Type[iostat.Metric], list[iostat.Metric]]:
        """
        Lists all pools along with a health status and space usage.

        -H: scripted mode; -p: displays numbers in (exact) values. The last
        given property is 'altroot', which is ignored.
        """
        command = ['zpool', 'list', '-H', '-p', *self.pools]
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
        return self.format_output(self.run_cmd(command), metrics)

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
        command = ['zpool', 'iostat', '-H', '-p', *self.pools]
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

        return self.format_output(self.run_cmd(command), metrics)

    def zpool_iostat_latency_histogram(self
                                       ) -> dict[Type[iostat.HistogramMetric],
                                                 list[iostat.HistogramMetric]]:
        """
        Request a list of pools and their latency histogram metrics

        -w: display latency histograms; -p: displays numbers in (exact) values;
        -H: scripted mode.
        """
        command = ['zpool', 'iostat', '-w', '-p', '-H', *self.pools]
        metrics = [
            iostat.LatencyTotalWaitRead,
            iostat.LatencyTotalWaitWrite,
            iostat.LatencyDiskWaitRead,
            iostat.LatencyDiskWaitWrite,
            iostat.LatencySyncQWaitRead,
            iostat.LatencySyncQWaitWrite,
            iostat.LatencyAsyncQWaitRead,
            iostat.LatencyAsyncQWaitWrite,
            iostat.LatencyScrub,
            iostat.LatencyTrim]

        return self.format_histogram(self.run_cmd(command), metrics)

    def zpool_iostat_request_size_histogram(
            self) -> dict[Type[iostat.HistogramMetric],
                          list[iostat.HistogramMetric]]:
        """
        Request a list of pools and their latency histogram metrics

        -r: display request size histograms for leaf vdev's I/O; -p: displays
        numbers in (exact) values; -H: scripted mode.
        """
        command = ['zpool', 'iostat', '-r', '-p', '-H', *self.pools]
        metrics = [
            iostat.RequestSizeSyncReadIndividual,
            iostat.RequestSizeSyncReadAggregate,
            iostat.RequestSizeSyncWriteIndividual,
            iostat.RequestSizeSyncWriteAggregate,
            iostat.RequestSizeASyncReadIndividual,
            iostat.RequestSizeASyncReadAggregate,
            iostat.RequestSizeASyncWriteIndividual,
            iostat.RequestSizeASyncWriteAggregate,
            iostat.RequestSizeScrubIndividual,
            iostat.RequestSizeScrubAggregate,
            iostat.RequestSizeTrimIndividual,
            iostat.RequestSizeTrimAggregate]

        return self.format_histogram(self.run_cmd(command), metrics)

    @REQUEST_TIME.time()
    def collect(self):
        data = self.zpool_list() | self.zpool_iostat(self.latency, self.queue)

        if any([self.latency_histogram, self.request_size_histogram]):
            data |= (
                self.zpool_iostat_latency_histogram() |
                self.zpool_iostat_request_size_histogram())

        for base, metrics in data.items():
            m = base.family(
                name=base.name,
                labels=['pool'],
                documentation=base.doc)

            for metric in metrics:
                if metric.value is None:
                    continue

                if base.family in (CounterMetricFamily, GaugeMetricFamily):
                    m.add_metric([metric.pool], metric.value)
                elif base.family == HistogramMetricFamily:
                    m.add_metric(
                        labels=[metric.pool],
                        buckets=list(zip(metric.buckets, metric.value)),
                        sum_value=sum(metric.value))

            yield m
