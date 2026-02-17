from __future__ import annotations, unicode_literals

import os

import testinfra.utils.ansible_runner
from helper.molecule import get_vars, infra_hosts, local_facts

testinfra_hosts = infra_hosts(host_name="redis_sentinel_1")

# --- tests -----------------------------------------------------------------


def test_sentinel_config(host, get_vars):
    """ """
    bind_address = get_vars.get("redis_sentinel", {}).get("bind", "10.13.1.1")
    bind_port = get_vars.get("redis_sentinel", {}).get("port", "26379")
    announce_ip = get_vars.get("redis_sentinel", {}).get("announce_ip", "10.13.1.1")

    print(f"redis bind address        : {bind_address}")
    print(f"redis bind port           : {bind_port}")
    print(f"redis sentinel announce ip: {announce_ip}")

    sentinel_conf_file = get_vars.get(
        "redis_sentinel_config_file", "/etc/redis/sentinel.conf"
    )

    bind_string = f"bind {bind_address}"
    port_string = f"port {bind_port}"
    announce_string = f'sentinel announce-ip "{announce_ip}"'

    config_file = host.file(sentinel_conf_file)

    assert config_file.is_file

    assert bind_string in config_file.content_string
    assert port_string in config_file.content_string
    assert announce_string in config_file.content_string


def test_sentinel_service(host, get_vars):
    service_name = get_vars.get("redis_sentinel_daemon")

    print(f"redis sentinel daemon: {service_name}")

    service = host.service(service_name)
    assert service.is_enabled
    assert service.is_running


def test_open_port(host, get_vars):
    for i in host.socket.get_listening_sockets():
        print(i)

    sentinel_address = get_vars.get("redis_sentinel", {}).get(
        "announce_ip", "10.13.1.1"
    )
    sentinel_port = 26379

    sockets = [
        f"tcp://{sentinel_address}:{sentinel_port}",
    ]

    for socket in sockets:
        service = host.socket(socket)
        assert service.is_listening
