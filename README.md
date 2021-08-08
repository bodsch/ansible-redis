
# Ansible Role:  `redis`

Install and configure a redis server, or redis-cluster.

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/bodsch/ansible-icinga2/CI)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-redis)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-redis)][releases]

[ci]: https://github.com/bodsch/ansible-redis/actions
[issues]: https://github.com/bodsch/ansible-redis/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-redis/releases


## tested operating systems

* Debian 9 / 10
* Ubuntu 18.04 / 20.04
* CentOS 7 / 8
* Oracle Linux 7 / 8
* Arch Linux


## usage

### default configuration

see [defaults/main.yml](defaults/main.yml)

```yaml

redis_include_path: /etc/redis.d

redis_includes:
  - active_defragmentation.conf
  - clients.conf
  - cluster_docker_nat.conf
  - event_notification.conf
  - general.conf
  - latency_monitor.conf
  - lua_scripting.conf
  - memory_management.conf
  - network.conf
  - redis_cluster.conf
  - security.conf
  - slow_log.conf
  - snapshotting.conf

# general
redis_general_loglevel: notice
redis_general_logfile: /var/log/redis/redis-server.log
redis_general_databases: 16
redis_general_show_logo: true
redis_general_daemonize: true
redis_general_supervised: auto

# append_only
redis_append_only: false
redis_append_filename: appendonly.aof
redis_append_fsync: everysec

# memory_management
redis_memory_maxmemory: 0
redis_memory_maxmemory_policy: "noeviction"
redis_memory_maxmemory_samples: 5

# network
redis_network_port: 6379
redis_network_bind: 127.0.0.1
redis_network_unixsocket: ''
redis_network_unixsocket_perm: 0700
redis_network_timeout: 300
redis_network_tcp_timeout: 300

# replication
redis_replication_master_ip: ""
redis_replication_master_port: 6379

# security
redis_security_requirepass: ""
redis_security_disabled_command: []

# snapshotting
# Set to an empty set to disable persistence (saving the DB to disk).
redis_snapshot_save:
  - 900 1
  - 300 10
  - 60 10000

redis_snapshot_dbfilename: dump.rdb
redis_snapshot_rdbcompression: false
redis_snapshot_dbdir: /var/lib/redis
```
