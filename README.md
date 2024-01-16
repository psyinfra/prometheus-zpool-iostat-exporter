# prometheus-zpool-iostat-exporter
A Python-based Prometheus exporter for logical I/O statistics for ZFS storage pools.
Output from the [zpool-iostat](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-iostat.8.html) 
utility is exported via the Prometheus client.

After the removal of `/proc/spl/kstat/zfs/*/io` as of OpenZFS 
https://github.com/openzfs/zfs/commit/371f88d96fe0aeb46a72fec78f90e1d777493ee5, 
the node exporter skips over ZFS I/O stats (see, e.g., 
https://github.com/prometheus/node_exporter/issues/2068). This exporter uses 
the output from `zpool iostat` to fill this gap.

## Installation
```commandline
git clone git@github.com:psyinfra/prometheus-zpool-iostat-exporter.git
cd prometheus-zpool-iostat-exporter
pip install .
```

## Usage

    usage: prometheus_zpool_iostat_exporter [-h] [--web.listen-address LISTEN_ADDRESS] [--pools [POOLS ...]] [--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-l] [-q] [-w] [-r]
    
    A Python-based Prometheus exporter for logical I/O statistics for ZFS storage pools
    
    options:
      -h, --help            show this help message and exit
      --web.listen-address LISTEN_ADDRESS
                            Address and port to listen on (default = :10007)
      --pools [POOLS ...]   Specify pools to include in collection (default = all pools)
      --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Specify logging level
      -l                    Include average latency statistics (see: zpool iostat -l)
      -q                    Include active queue statistics (see: zpool iostat -q)
      -w                    Include latency histograms (see: zpool iostat -w)
      -r                    Include request size histograms for the leaf vdev's I/O (see: zpool iostat -r)

### Example: Default
```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007
```
Export output from `zpool list -Hp` and `zpool iostat -Hp`. Sample output:

```text
...
# HELP zpool_iostat_size_bytes Byte size of a pool
# TYPE zpool_iostat_size_bytes gauge
zpool_iostat_size_bytes{pool="tank"} 1.855425871872e+012
# HELP zpool_iostat_allocated_bytes Bytes allocated in a pool
# TYPE zpool_iostat_allocated_bytes gauge
zpool_iostat_allocated_bytes{pool="tank"} 1.21979650048e+011
# HELP zpool_iostat_free_bytes Bytes free in a pool
# TYPE zpool_iostat_free_bytes gauge
zpool_iostat_free_bytes{pool="tank"} 1.733446221824e+012
# HELP zpool_iostat_checkpoint_bytes Bytes allocated to a checkpoint in a pool
# TYPE zpool_iostat_checkpoint_bytes gauge
zpool_iostat_checkpoint_bytes{pool="tank"} NaN
# HELP zpool_iostat_expandsize_bytes Unused capacity that can be expanded into when resizing disks
# TYPE zpool_iostat_expandsize_bytes gauge
zpool_iostat_expandsize_bytes{pool="tank"} 3.4359738368e+010
# HELP zpool_iostat_fragmentation_ratio Ratio of fragmentation of the free space in a pool
# TYPE zpool_iostat_fragmentation_ratio gauge
zpool_iostat_fragmentation_ratio{pool="tank"} 0.03
# HELP zpool_iostat_capacity_ratio Capacity of a pool expressed as a ratio of allocated_bytes:size_bytes
# TYPE zpool_iostat_capacity_ratio gauge
zpool_iostat_capacity_ratio{pool="tank"} 0.06
# HELP zpool_iostat_dedup_ratio Indicator of how much deduplication has occurred as a ratio of referenced-bytes:logical-bytes
# TYPE zpool_iostat_dedup_ratio gauge
zpool_iostat_dedup_ratio{pool="tank"} 1.0
# HELP zpool_iostat_health_info Pool health (0=ONLINE, 1=DEGRADED, 2=FAULTED, 3=OFFLINE, 4=UNAVAIL, 5=REMOVED)
# TYPE zpool_iostat_health_info gauge
zpool_iostat_health_info{pool="tank"} 0.0
# HELP zpool_iostat_capacity_allocated_bytes Amount of data currently stored in the pool
# TYPE zpool_iostat_capacity_allocated_bytes gauge
zpool_iostat_capacity_allocated_bytes{pool="tank"} 1.21979650048e+011
# HELP zpool_iostat_capacity_free_bytes Amount of disk space available in the pool
# TYPE zpool_iostat_capacity_free_bytes gauge
zpool_iostat_capacity_free_bytes{pool="tank"} 1.733446221824e+012
# HELP zpool_iostat_operations_read_count_total Number of read I/O operations sent to the pool, including metadata requests
# TYPE zpool_iostat_operations_read_count_total counter
zpool_iostat_operations_read_count_total{pool="tank"} 6.0
# HELP zpool_iostat_operations_write_count_total Number of write I/O operations sent to the pool
# TYPE zpool_iostat_operations_write_count_total counter
zpool_iostat_operations_write_count_total{pool="tank"} 97.0
# HELP zpool_iostat_bandwidth_read_count_total Bandwidth of all read operations (including metadata) as units per second
# TYPE zpool_iostat_bandwidth_read_count_total counter
zpool_iostat_bandwidth_read_count_total{pool="tank"} 84847.0
# HELP zpool_iostat_bandwidth_write_count_total Bandwidth of all write operations as units per second
# TYPE zpool_iostat_bandwidth_write_count_total counter
zpool_iostat_bandwidth_write_count_total{pool="tank"} 1.536902e+06
```

### Example: Include average latency statistics
```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007 -l
```

In addition to the default output, add `zpool iostat -Hpl`. Sample additional 
output:

```text
# HELP zpool_iostat_total_wait_read_seconds Average total read I/O time (queuing + disk I/O time)
# TYPE zpool_iostat_total_wait_read_seconds gauge
zpool_iostat_total_wait_read_seconds{pool="tank"} 0.00096241
# HELP zpool_iostat_total_wait_write_seconds Average total write I/O time (queuing + disk I/O time)
# TYPE zpool_iostat_total_wait_write_seconds gauge
zpool_iostat_total_wait_write_seconds{pool="tank"} 0.00034349200000000004
# HELP zpool_iostat_disk_wait_read_seconds Average disk read I/O time (time reading the disk)
# TYPE zpool_iostat_disk_wait_read_seconds gauge
zpool_iostat_disk_wait_read_seconds{pool="tank"} 0.00015146200000000002
# HELP zpool_iostat_disk_wait_write_seconds Average disk write I/O time (time writing to the disk)
# TYPE zpool_iostat_disk_wait_write_seconds gauge
zpool_iostat_disk_wait_write_seconds{pool="tank"} 5.6038e-05
# HELP zpool_iostat_syncq_wait_read_seconds Average amount of time read I/O spent in synchronous priority queues. Does not include disk time
# TYPE zpool_iostat_syncq_wait_read_seconds gauge
zpool_iostat_syncq_wait_read_seconds{pool="tank"} 1.56e-06
# HELP zpool_iostat_syncq_wait_write_seconds Average amount of time write I/O spent in synchronous priority queues. Does not include disk time
# TYPE zpool_iostat_syncq_wait_write_seconds gauge
zpool_iostat_syncq_wait_write_seconds{pool="tank"} 0.00014177700000000002
# HELP zpool_iostat_asyncq_wait_read_seconds Average amount of time read I/O spent in asynchronous priority queues. Does not include disk time
# TYPE zpool_iostat_asyncq_wait_read_seconds gauge
zpool_iostat_asyncq_wait_read_seconds{pool="tank"} 2.616e-06
# HELP zpool_iostat_asyncq_wait_write_seconds Average amount of time write I/O spent in asynchronous priority queues. Does not include disk time
# TYPE zpool_iostat_asyncq_wait_write_seconds gauge
zpool_iostat_asyncq_wait_write_seconds{pool="tank"} 0.00038501400000000004
# HELP zpool_iostat_scrub_seconds Average queuing time in scrub queue. Does not include disk time
# TYPE zpool_iostat_scrub_seconds gauge
zpool_iostat_scrub_seconds{pool="tank"} 0.006383604
# HELP zpool_iostat_trim_seconds Average queuing time in trim queue. Does not include disk time
# TYPE zpool_iostat_trim_seconds gauge
zpool_iostat_trim_seconds{pool="tank"} 0.0011204650000000002
```

### Example: Include active queue statistics
```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007 -q
```

In addition to the default output, add `zpool iostat -Hpq`. Sample additional 
output:

```text
# HELP zpool_iostat_syncq_read_pending_count Current number of pending read entries in synchronous priority queues
# TYPE zpool_iostat_syncq_read_pending_count gauge
zpool_iostat_syncq_read_pending_count{pool="tank"} 0.0
# HELP zpool_iostat_syncq_read_active_count Current number of active read entries in synchronous priority queues
# TYPE zpool_iostat_syncq_read_active_count gauge
zpool_iostat_syncq_read_active_count{pool="tank"} 0.0
# HELP zpool_iostat_syncq_write_pending_count Current number of pending write entries in synchronous priority queues
# TYPE zpool_iostat_syncq_write_pending_count gauge
zpool_iostat_syncq_write_pending_count{pool="tank"} 0.0
# HELP zpool_iostat_syncq_write_active_count Current number of active write entries in synchronous priority queues
# TYPE zpool_iostat_syncq_write_active_count gauge
zpool_iostat_syncq_write_active_count{pool="tank"} 0.0
# HELP zpool_iostat_asyncq_read_pending_count Current number of pending read entries in asynchronous priority queues
# TYPE zpool_iostat_asyncq_read_pending_count gauge
zpool_iostat_asyncq_read_pending_count{pool="tank"} 0.0
# HELP zpool_iostat_asyncq_read_active_count Current number of active read entries in asynchronous priority queues
# TYPE zpool_iostat_asyncq_read_active_count gauge
zpool_iostat_asyncq_read_active_count{pool="tank"} 0.0
# HELP zpool_iostat_asyncq_write_pending_count Current number of pending write entries in asynchronous priority queues
# TYPE zpool_iostat_asyncq_write_pending_count gauge
zpool_iostat_asyncq_write_pending_count{pool="tank"} 0.0
# HELP zpool_iostat_asyncq_wrote_active_count Current number of active write entries in asynchronous priority queues
# TYPE zpool_iostat_asyncq_wrote_active_count gauge
zpool_iostat_asyncq_wrote_active_count{pool="tank"} 0.0
# HELP zpool_iostat_scrubq_pending_count Current number of pending entries in scrub queue.
# TYPE zpool_iostat_scrubq_pending_count gauge
zpool_iostat_scrubq_pending_count{pool="tank"} 0.0
# HELP zpool_iostat_scrubq_active_count Current number of active entries in scrub queue.
# TYPE zpool_iostat_scrubq_active_count gauge
zpool_iostat_scrubq_active_count{pool="tank"} 0.0
# HELP zpool_iostat_trimq_pending_count Current number of pending entries in trim queue.
# TYPE zpool_iostat_trimq_pending_count gauge
zpool_iostat_trimq_pending_count{pool="tank"} 0.0
# HELP zpool_iostat_trimq_active_count Current number of active entries in trim queue.
# TYPE zpool_iostat_trimq_active_count gauge
zpool_iostat_trimq_active_count{pool="tank"} 0.0
```

### Example: Include histograms
```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007 -w
```

In addition to the default output, add `zpool iostat -Hpq` to include latency 
histograms.

```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007 -r
```

In addition to the default output, add `zpool iostat -Hpr` to include request 
size histograms.

The histogram output is divided over buckets and thus too large to provide an 
overview of here. It contains individual and aggregate (a)synchronous read and 
write I/O request size when using `-r`, and total, disk, (a)synchronous queue 
read and write latency when using `-w`.

### Example: All additional output
```commandline
prometheus_zpool_iostat_exporter --web.listen-address :10007 -lqwr
```

Multiple arguments can be used to provide all or part of the additional 
output. Here all additional output is exported.
