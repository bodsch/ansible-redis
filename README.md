
# Ansible Role:  `redis`

Install and configure a redis server, or redis-cluster.

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/bodsch/ansible-redis/CI)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-redis)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-redis)][releases]

[ci]: https://github.com/bodsch/ansible-redis/actions
[issues]: https://github.com/bodsch/ansible-redis/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-redis/releases


## tested operating systems

Tested on

* ArchLinux
* ArtixLinux
* Debian based
    - Debian 10 / 11
    - Ubuntu 20.04
* RedHat based
    - Alma Linux 8
    - Rocky Linux 8
    - OracleLinux 8


## usage

### default configuration

see [defaults/main.yml](defaults/main.yml)

```yaml
redis_include_path: /etc/redis.d
redis_data_dir: /var/lib/redis

redis_includes:
  - active_defragmentation.conf
  # - advanced_config.conf
  # - append_only.conf
  - clients.conf
  - cluster_docker_nat.conf
  - event_notification.conf
  - general.conf
  - latency_monitor.conf
  # - lazy_freeing.conf
  - lua_scripting.conf
  - memory_management.conf
  - network.conf
  - redis_cluster.conf
  # - replication.conf
  - security.conf
  - slow_log.conf
  - snapshotting.conf

# general
redis_general:
  loglevel: notice
  logfile: /var/log/redis/redis-server.log
  databases: 16
  show_logo: true
  daemonize: true
  supervised: auto

# append_only
redis_append:
  only: false
  filename: appendonly.aof
  fsync: everysec

# memory_management
redis_memory:
  maxmemory: 0
  maxmemory_policy: noeviction
  maxmemory_samples: 5
  replica_ignore_maxmemory: true

# network
redis_network:
  bind: 127.0.0.1
  port: 6379
  tcp_backlog: 511
  unixsocket: ''
  unixsocket_perm: 0700
  timeout: 300
  tcp_keepalive: 300

# replication
redis_replication:
  master_ip: ""
  master_port: 6379

# security
redis_security:
  requirepass: ""
  rename_commands: {}

# snapshotting
redis_snapshot:
  # Set to an empty set to disable persistence (saving the DB to disk).
  save:
    - 900 1
    - 300 10
    - 60 10000
  dbfilename: dump.rdb
  rdbcompression: false
  dbdir: "{{ redis_data_dir }}"

redis_sentinel:
  enabled: false
  state: started
  bind: "127.0.0.1"
  port: 26379
  protected_mode: false
  daemonize: false
  logfile: /var/log/redis/redis-sentinel.log
  cluster_name: redis_cluster
  master: ''
  announce_ip: ''
```

---

## Author

- Bodo Schulz

## License

[Apache](LICENSE)

`FREE SOFTWARE, HELL YEAH!`
