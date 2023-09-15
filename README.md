
# Ansible Role:  `redis`

Install and configure a *redis  .

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-redis/main.yml?branch=main)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-redis)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-redis)][releases]
[![Ansible Quality Score](https://img.shields.io/ansible/quality/50067?label=role%20quality)][quality]

[ci]: https://github.com/bodsch/ansible-redis/actions
[issues]: https://github.com/bodsch/ansible-redis/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-redis/releases
[quality]: https://galaxy.ansible.com/bodsch/redis

## Requirements & Dependencies

Ansible Collections

- [bodsch.core](https://github.com/bodsch/ansible-collection-core)

```bash
ansible-galaxy collection install bodsch.core
```
or
```bash
ansible-galaxy collection install --requirements-file collections.yml
```


## tested operating systems

Tested on

* ArchLinux
* ArtixLinux
* Debian based
    - Debian 11
    - Ubuntu 20.04

## usage

### default configuration

see [defaults/main.yml](defaults/main.yml)

```yaml
redis_include_path: /etc/redis.d
redis_data_dir: /var/lib/redis

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
  bind:
    - 127.0.0.1
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

**FREE SOFTWARE, HELL YEAH!**
