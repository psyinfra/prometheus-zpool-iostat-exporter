from dataclasses import dataclass, fields
from typing import ClassVar

from . import logger, EXPORTER_PREFIX


@dataclass
class Metric:
    pool: str
    value: int
    name: ClassVar[str] = 'test'
    doc: ClassVar[str] = 'test'

    def _convert_field_types(self):
        for field in fields(self):
            # Account for missing values
            if getattr(self, field.name) == '-' or \
                    getattr(self, field.name) is None:
                setattr(self, field.name, 'NaN')
                continue

            try:
                setattr(
                    self, field.name, field.type(getattr(self, field.name)))
            except ValueError as exc:
                logger.error(
                    f"Failed to convert {self.name}{{pool='{self.pool}'}} "
                    f"{self.value} to {field.type}: {exc}")
                setattr(self, field.name, None)

    def __post_init__(self):
        self._convert_field_types()


@dataclass
class IntMetric(Metric):
    value: int


@dataclass
class FloatMetric(Metric):
    value: float


@dataclass
class RatioMetric(FloatMetric):
    def __post_init__(self):
        """Convert percentage to ratio"""
        self.value = float(self.value)/100
        super().__post_init__()


@dataclass
class StateMetric(Metric):
    """
    Standard input value is a string that will be converted to an integer and
    type-enforced, hence why the type of value is integer. Changing this to
    Union[str, int] causes issues when enforcing the expected type. It should,
    after post-initialization conversion, in all cases be an integer or a
    missing value (NoneType).
    """
    value: int

    def __post_init__(self):
        """Convert state-string to state-number"""
        state = {
            'ONLINE': 0, 'DEGRADED': 1, 'FAULTED': 2, 'OFFLINE': 3,
            'UNAVAIL': 4, 'REMOVED': 5}
        self.value = state.get(self.value, None)
        super().__post_init__()


@dataclass
class TimeMetric(FloatMetric):
    def __post_init__(self):
        """Convert nanoseconds to seconds"""
        self.value = float(self.value)*1e-9
        super().__post_init__()


"""
Parsed output from `zpool list -H -p`
"""


@dataclass
class Size(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_size_bytes'
    doc: ClassVar[str] = 'Byte size of a pool'


@dataclass
class Alloc(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_allocated_bytes'
    doc: ClassVar[str] = 'Bytes allocated in a pool'


@dataclass
class Free(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_free_bytes'
    doc: ClassVar[str] = 'Bytes free in a pool'


@dataclass
class CkPoint(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_checkpoint_bytes'
    doc: ClassVar[str] = 'Bytes allocated to a checkpoint in a pool'


@dataclass
class ExpandSz(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_expandsize_bytes'
    doc: ClassVar[str] = (
            'Unused capacity that can be expanded into when resizing disks')


@dataclass
class Frag(RatioMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_fragmentation_ratio'
    doc: ClassVar[str] = 'Ratio of fragmentation of the free space in a pool'


@dataclass
class Cap(RatioMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_capacity_ratio'
    doc: ClassVar[str] = (
            'Capacity of a pool expressed as a ratio of '
            'allocated_bytes:size_bytes')


@dataclass
class Dedup(FloatMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_dedup_ratio'
    doc: ClassVar[str] = (
            'Indicator of how much deduplication has occurred as a ratio of '
            'referenced-bytes:logical-bytes')


@dataclass
class Health(StateMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_health_info'
    doc: ClassVar[str] = (
            'Pool health (0=ONLINE, 1=DEGRADED, 2=FAULTED, 3=OFFLINE, '
            '4=UNAVAIL, 5=REMOVED)')


"""
Parsed output from `zpool iostat -H -p`
"""


@dataclass
class CapacityAlloc(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_capacity_allocated_bytes'
    doc: ClassVar[str] = 'Amount of data currently stored in the pool'


@dataclass
class CapacityFree(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_capacity_free_bytes'
    doc: ClassVar[str] = 'Amount of disk space available in the pool'


@dataclass
class OperationsRead(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_operations_read_count'
    doc: ClassVar[str] = (
            'Number of read I/O operations sent to the pool, including '
            'metadata requests')


@dataclass
class OperationsWrite(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_operations_write_count'
    doc: ClassVar[str] = 'Number of write I/O operations sent to the pool'


@dataclass
class BandwidthRead(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_bandwidth_read_count'
    doc: ClassVar[str] = (
            'Bandwidth of all read operations (including metadata) as units '
            'per second')


@dataclass
class BandwidthWrite(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_bandwidth_write_count'
    doc: ClassVar[str] = (
            'Bandwidth of all write operations as units per second')


"""
Parsed average latency output from `zpool iostat -H -p -l`
"""


@dataclass
class TotalWaitRead(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_total_wait_read_seconds'
    doc: ClassVar[str] = (
            'Average total read I/O time (queuing + disk I/O time)')


@dataclass
class TotalWaitWrite(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_total_wait_write_seconds'
    doc: ClassVar[str] = (
            'Average total write I/O time (queuing + disk I/O time)')


@dataclass
class DiskWaitRead(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_disk_wait_read_seconds'
    doc: ClassVar[str] = 'Average disk read I/O time (time reading the disk)'


@dataclass
class DiskWaitWrite(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_disk_wait_write_seconds'
    doc: ClassVar[str] = (
            'Average disk write I/O time (time writing to the disk)')


@dataclass
class SyncQWaitRead(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_syncq_wait_read_seconds'
    doc: ClassVar[str] = (
            'Average amount of time read I/O spent in synchronous priority '
            'queues. Does not include disk time')


@dataclass
class SyncQWaitWrite(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_syncq_wait_write_seconds'
    doc: ClassVar[str] = (
            'Average amount of time write I/O spent in synchronous priority '
            'queues. Does not include disk time')


@dataclass
class AsyncQWaitRead(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_asyncq_wait_read_seconds'
    doc: ClassVar[str] = (
            'Average amount of time read I/O spent in asynchronous priority '
            'queues. Does not include disk time')


@dataclass
class AsyncQWaitWrite(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_asyncq_wait_write_seconds'
    doc: ClassVar[str] = (
            'Average amount of time write I/O spent in asynchronous priority '
            'queues. Does not include disk time')


@dataclass
class Scrub(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_scrub_seconds'
    doc: ClassVar[str] = (
            'Average queuing time in scrub queue. Does not include disk time')


@dataclass
class Trim(TimeMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_trim_seconds'
    doc: ClassVar[str] = (
        'Average queuing time in trim queue. Does not include disk time')


"""
Parsed average latency output from `zpool iostat -H -p -q`
"""


@dataclass
class SyncQReadPend(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_syncq_read_pending_count'
    doc: ClassVar[str] = (
            'Current number of pending read entries in synchronous priority '
            'queues')


@dataclass
class SyncQReadActiv(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_syncq_read_active_count'
    doc: ClassVar[str] = (
            'Current number of active read entries in synchronous priority '
            'queues')


@dataclass
class SyncQWritePend(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_syncq_write_pending_count'
    doc: ClassVar[str] = (
            'Current number of pending write entries in synchronous priority '
            'queues')


@dataclass
class SyncQWriteActiv(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_syncq_write_active_count'
    doc: ClassVar[str] = (
            'Current number of active write entries in synchronous priority '
            'queues')


@dataclass
class ASyncQReadPend(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_asyncq_read_pending_count'
    doc: ClassVar[str] = (
        'Current number of pending read entries in asynchronous priority '
        'queues')


@dataclass
class ASyncQReadActiv(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_asyncq_read_active_count'
    doc: ClassVar[str] = (
        'Current number of active read entries in asynchronous priority '
        'queues')


@dataclass
class ASyncQWritePend(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_asyncq_write_pending_count'
    doc: ClassVar[str] = (
        'Current number of pending write entries in asynchronous priority '
        'queues')


@dataclass
class ASyncQWriteActiv(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_asyncq_wrote_active_count'
    doc: ClassVar[str] = (
        'Current number of active write entries in asynchronous priority '
        'queues')


@dataclass
class ScrubQPending(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_scrubq_pending_count'
    doc: ClassVar[str] = 'Current number of pending entries in scrub queue.'


@dataclass
class ScrubQActiv(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_scrubq_active_count'
    doc: ClassVar[str] = 'Current number of active entries in scrub queue.'


@dataclass
class TrimQPend(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_trimq_pending_count'
    doc: ClassVar[str] = 'Current number of pending entries in trim queue.'


@dataclass
class TrimQActiv(IntMetric):
    name: ClassVar[str] = f'{EXPORTER_PREFIX}_trimq_active_count'
    doc: ClassVar[str] = 'Current number of active entries in trim queue.'
