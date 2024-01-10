# prometheus-zpool-iostat-exporter
A Python-based Prometheus exporter for logical I/O statistics for ZFS storage pools.
Output from the [zpool-iostat](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-iostat.8.html) 
utility is exported via the Prometheus client.

## Installation
```commandline
git clone git@github.com:psyinfra/prometheus-zpool-iostat-exporter.git
cd prometheus-zpool-iostat-exporter
pip install .
```

## Usage

    usage: prometheus_zpool_iostat_exporter [-h] [-w LISTEN_ADDRESS] [--latency] [--queue] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
    
    A Python-based Prometheus exporter for logical I/O statistics for ZFS storage pools
    
    options:
      -h, --help            show this help message and exit
      -w LISTEN_ADDRESS, --web.listen-address LISTEN_ADDRESS
                            Address and port to listen on (default = :10007)
      --latency             Include average latency statistics (see: zpool iostat -l)
      --queue               Include active queue statistics (see: zpool iostat -q)
      -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Specify logging level

### Example
```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007
```

This command exports the output from `zpool list -H -p` and 
`zpool iostat -H -p` with the following output:

```text
# HELP zpool_iostat_size_bytes Byte size of a pool
# TYPE zpool_iostat_size_bytes gauge
zpool_iostat_size_bytes{pool="bpool"} 1.00663296e+09
zpool_iostat_size_bytes{pool="rpool"} 1.855425871872e+012
# HELP zpool_iostat_allocated_bytes Bytes allocated in a pool
# TYPE zpool_iostat_allocated_bytes gauge
zpool_iostat_allocated_bytes{pool="bpool"} 1.26230528e+08
zpool_iostat_allocated_bytes{pool="rpool"} 7.8993768448e+010
# HELP zpool_iostat_free_bytes Bytes free in a pool
# TYPE zpool_iostat_free_bytes gauge
zpool_iostat_free_bytes{pool="bpool"} 8.80402432e+08
zpool_iostat_free_bytes{pool="rpool"} 1.776432103424e+012
# HELP zpool_iostat_checkpoint_bytes Bytes allocated to a checkpoint in a pool
# TYPE zpool_iostat_checkpoint_bytes gauge
zpool_iostat_checkpoint_bytes{pool="bpool"} NaN
zpool_iostat_checkpoint_bytes{pool="rpool"} NaN
# HELP zpool_iostat_expandsize_bytes Unused capacity that can be expanded into when resizing disks
# TYPE zpool_iostat_expandsize_bytes gauge
zpool_iostat_expandsize_bytes{pool="bpool"} NaN
zpool_iostat_expandsize_bytes{pool="rpool"} 3.4359738368e+010
# HELP zpool_iostat_fragmentation_ratio Ratio of fragmentation of the free space in a pool
# TYPE zpool_iostat_fragmentation_ratio gauge
zpool_iostat_fragmentation_ratio{pool="bpool"} 0.03
zpool_iostat_fragmentation_ratio{pool="rpool"} 0.02
# HELP zpool_iostat_capacity_ratio Capacity of a pool expressed as a ratio of allocated_bytes:size_bytes
# TYPE zpool_iostat_capacity_ratio gauge
zpool_iostat_capacity_ratio{pool="bpool"} 0.12
zpool_iostat_capacity_ratio{pool="rpool"} 0.04
# HELP zpool_iostat_dedup_ratio Indicator of how much deduplication has occurred as a ratio of referenced-bytes:logical-bytes
# TYPE zpool_iostat_dedup_ratio gauge
zpool_iostat_dedup_ratio{pool="bpool"} 1.0
zpool_iostat_dedup_ratio{pool="rpool"} 1.0
# HELP zpool_iostat_health_info Pool health (0=ONLINE, 1=DEGRADED, 2=FAULTED, 3=OFFLINE, 4=UNAVAIL, 5=REMOVED)
# TYPE zpool_iostat_health_info gauge
zpool_iostat_health_info{pool="bpool"} 0.0
zpool_iostat_health_info{pool="rpool"} 0.0
# HELP zpool_iostat_capacity_allocated_bytes Amount of data currently stored in the pool
# TYPE zpool_iostat_capacity_allocated_bytes gauge
zpool_iostat_capacity_allocated_bytes{pool="bpool"} 1.26230528e+08
zpool_iostat_capacity_allocated_bytes{pool="rpool"} 7.8993768448e+010
# HELP zpool_iostat_capacity_free_bytes Amount of disk space available in the pool
# TYPE zpool_iostat_capacity_free_bytes gauge
zpool_iostat_capacity_free_bytes{pool="bpool"} 8.80402432e+08
zpool_iostat_capacity_free_bytes{pool="rpool"} 1.776432103424e+012
# HELP zpool_iostat_operations_read_count Number of read I/O operations sent to the pool, including metadata requests
# TYPE zpool_iostat_operations_read_count gauge
zpool_iostat_operations_read_count{pool="bpool"} 0.0
zpool_iostat_operations_read_count{pool="rpool"} 4.0
# HELP zpool_iostat_operations_write_count Number of write I/O operations sent to the pool
# TYPE zpool_iostat_operations_write_count gauge
zpool_iostat_operations_write_count{pool="bpool"} 0.0
zpool_iostat_operations_write_count{pool="rpool"} 82.0
# HELP zpool_iostat_bandwidth_read_count Bandwidth of all read operations (including metadata) as units per second
# TYPE zpool_iostat_bandwidth_read_count gauge
zpool_iostat_bandwidth_read_count{pool="bpool"} 110.0
zpool_iostat_bandwidth_read_count{pool="rpool"} 65426.0
# HELP zpool_iostat_bandwidth_write_count Bandwidth of all write operations as units per second
# TYPE zpool_iostat_bandwidth_write_count gauge
zpool_iostat_bandwidth_write_count{pool="bpool"} 183.0
zpool_iostat_bandwidth_write_count{pool="rpool"} 1.445709e+06
```

### Example including average latency statistics
```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007 --latency
```

This command exports the output from `zpool list -H -p` and 
`zpool iostat -H -p -l` with the following additional output:

```text
# HELP zpool_iostat_total_wait_read_seconds Average total read I/O time (queuing + disk I/O time)
# TYPE zpool_iostat_total_wait_read_seconds gauge
zpool_iostat_total_wait_read_seconds{pool="bpool"} 0.012749970000000001
zpool_iostat_total_wait_read_seconds{pool="rpool"} 0.0011742970000000001
# HELP zpool_iostat_total_wait_write_seconds Average total write I/O time (queuing + disk I/O time)
# TYPE zpool_iostat_total_wait_write_seconds gauge
zpool_iostat_total_wait_write_seconds{pool="bpool"} 0.0005088870000000001
zpool_iostat_total_wait_write_seconds{pool="rpool"} 0.00036034500000000003
# HELP zpool_iostat_disk_wait_read_seconds Average disk read I/O time (time reading the disk)
# TYPE zpool_iostat_disk_wait_read_seconds gauge
zpool_iostat_disk_wait_read_seconds{pool="bpool"} 0.000365384
zpool_iostat_disk_wait_read_seconds{pool="rpool"} 0.00015183700000000002
# HELP zpool_iostat_disk_wait_write_seconds Average disk write I/O time (time writing to the disk)
# TYPE zpool_iostat_disk_wait_write_seconds gauge
zpool_iostat_disk_wait_write_seconds{pool="bpool"} 9.599200000000001e-05
zpool_iostat_disk_wait_write_seconds{pool="rpool"} 5.9162e-05
# HELP zpool_iostat_syncq_wait_read_seconds Average amount of time read I/O spent in synchronous priority queues. Does not include disk time
# TYPE zpool_iostat_syncq_wait_read_seconds gauge
zpool_iostat_syncq_wait_read_seconds{pool="bpool"} 1.216e-06
zpool_iostat_syncq_wait_read_seconds{pool="rpool"} 1.8820000000000001e-06
# HELP zpool_iostat_syncq_wait_write_seconds Average amount of time write I/O spent in synchronous priority queues. Does not include disk time
# TYPE zpool_iostat_syncq_wait_write_seconds gauge
zpool_iostat_syncq_wait_write_seconds{pool="bpool"} 0.000516597
zpool_iostat_syncq_wait_write_seconds{pool="rpool"} 0.000113864
# HELP zpool_iostat_asyncq_wait_read_seconds Average amount of time read I/O spent in asynchronous priority queues. Does not include disk time
# TYPE zpool_iostat_asyncq_wait_read_seconds gauge
zpool_iostat_asyncq_wait_read_seconds{pool="bpool"} 3.456e-06
zpool_iostat_asyncq_wait_read_seconds{pool="rpool"} 2.379e-06
# HELP zpool_iostat_asyncq_wait_write_seconds Average amount of time write I/O spent in asynchronous priority queues. Does not include disk time
# TYPE zpool_iostat_asyncq_wait_write_seconds gauge
zpool_iostat_asyncq_wait_write_seconds{pool="bpool"} 0.00039714700000000004
zpool_iostat_asyncq_wait_write_seconds{pool="rpool"} 0.000385818
# HELP zpool_iostat_scrub_seconds Average queuing time in scrub queue. Does not include disk time
# TYPE zpool_iostat_scrub_seconds gauge
zpool_iostat_scrub_seconds{pool="bpool"} 0.012788063
zpool_iostat_scrub_seconds{pool="rpool"} 0.0068696830000000006
# HELP zpool_iostat_trim_seconds Average queuing time in trim queue. Does not include disk time
# TYPE zpool_iostat_trim_seconds gauge
zpool_iostat_trim_seconds{pool="bpool"} 0.00047730900000000003
zpool_iostat_trim_seconds{pool="rpool"} 0.0011173720000000002
```

### Example including active queue statistics
```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007 --queue
```

This command exports the output from `zpool list -H -p` and 
`zpool iostat -H -p -q` with the following additional output:

```text
# HELP zpool_iostat_syncq_read_pending_count Current number of pending read entries in synchronous priority queues
# TYPE zpool_iostat_syncq_read_pending_count gauge
zpool_iostat_syncq_read_pending_count{pool="bpool"} 0.0
zpool_iostat_syncq_read_pending_count{pool="rpool"} 0.0
# HELP zpool_iostat_syncq_read_active_count Current number of active read entries in synchronous priority queues
# TYPE zpool_iostat_syncq_read_active_count gauge
zpool_iostat_syncq_read_active_count{pool="bpool"} 0.0
zpool_iostat_syncq_read_active_count{pool="rpool"} 0.0
# HELP zpool_iostat_syncq_write_pending_count Current number of pending write entries in synchronous priority queues
# TYPE zpool_iostat_syncq_write_pending_count gauge
zpool_iostat_syncq_write_pending_count{pool="bpool"} 0.0
zpool_iostat_syncq_write_pending_count{pool="rpool"} 0.0
# HELP zpool_iostat_syncq_write_active_count Current number of active write entries in synchronous priority queues
# TYPE zpool_iostat_syncq_write_active_count gauge
zpool_iostat_syncq_write_active_count{pool="bpool"} 0.0
zpool_iostat_syncq_write_active_count{pool="rpool"} 0.0
# HELP zpool_iostat_asyncq_read_pending_count Current number of pending read entries in asynchronous priority queues
# TYPE zpool_iostat_asyncq_read_pending_count gauge
zpool_iostat_asyncq_read_pending_count{pool="bpool"} 0.0
zpool_iostat_asyncq_read_pending_count{pool="rpool"} 0.0
# HELP zpool_iostat_asyncq_read_active_count Current number of active read entries in asynchronous priority queues
# TYPE zpool_iostat_asyncq_read_active_count gauge
zpool_iostat_asyncq_read_active_count{pool="bpool"} 0.0
zpool_iostat_asyncq_read_active_count{pool="rpool"} 0.0
# HELP zpool_iostat_asyncq_write_pending_count Current number of pending write entries in asynchronous priority queues
# TYPE zpool_iostat_asyncq_write_pending_count gauge
zpool_iostat_asyncq_write_pending_count{pool="bpool"} 0.0
zpool_iostat_asyncq_write_pending_count{pool="rpool"} 0.0
# HELP zpool_iostat_asyncq_wrote_active_count Current number of active write entries in asynchronous priority queues
# TYPE zpool_iostat_asyncq_wrote_active_count gauge
zpool_iostat_asyncq_wrote_active_count{pool="bpool"} 0.0
zpool_iostat_asyncq_wrote_active_count{pool="rpool"} 0.0
# HELP zpool_iostat_scrubq_pending_count Current number of pending entries in scrub queue.
# TYPE zpool_iostat_scrubq_pending_count gauge
zpool_iostat_scrubq_pending_count{pool="bpool"} 0.0
zpool_iostat_scrubq_pending_count{pool="rpool"} 0.0
# HELP zpool_iostat_scrubq_active_count Current number of active entries in scrub queue.
# TYPE zpool_iostat_scrubq_active_count gauge
zpool_iostat_scrubq_active_count{pool="bpool"} 0.0
zpool_iostat_scrubq_active_count{pool="rpool"} 0.0
# HELP zpool_iostat_trimq_pending_count Current number of pending entries in trim queue.
# TYPE zpool_iostat_trimq_pending_count gauge
zpool_iostat_trimq_pending_count{pool="bpool"} 0.0
zpool_iostat_trimq_pending_count{pool="rpool"} 0.0
# HELP zpool_iostat_trimq_active_count Current number of active entries in trim queue.
# TYPE zpool_iostat_trimq_active_count gauge
zpool_iostat_trimq_active_count{pool="bpool"} 0.0
zpool_iostat_trimq_active_count{pool="rpool"} 0.0
```

### Example including histograms
```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007 --latency-histogram
```

Exports the output from `zpool list -H -p` and `zpool iostat -w -p -H`.

```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007 --latency-histogram
```
Exports the output from `zpool list -H -p` and `zpool iostat -r -p -H`.

The output is too large for an example, as each of the metrics (e.g., 
individual and aggregate (a)synchronous read and write I/O request size, as 
well as total, disk, (a)sychronous queue read and write latency) returns 
numerous buckets.

