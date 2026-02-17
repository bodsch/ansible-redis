from __future__ import annotations, unicode_literals

import os

import testinfra.utils.ansible_runner
from helper.molecule import get_vars, infra_hosts, local_facts

testinfra_hosts = infra_hosts(host_name="redis")

# --- tests -----------------------------------------------------------------


def test_package(host, get_vars):
    distribution = host.system_info.distribution
    release = host.system_info.release

    print(f"distribution: {distribution}")
    print(f"release     : {release}")

    if not distribution == "artix":
        packages = get_vars.get("redis_packages")

        for pack in packages:
            p = host.package(pack)
            assert p.is_installed


def test_files(host, get_vars):
    redis_files = []

    redis_files.append(get_vars.get("redis_config_file"))

    for files in redis_files:
        f = host.file(files)
        assert f.is_file


def test_user(host):
    assert host.group("redis").exists
    assert host.user("redis").exists
    assert "redis" in host.user("redis").groups
    # assert host.user("redis").shell == "/sbin/nologin"
    assert host.user("redis").home == "/var/lib/redis"


def test_service(host, get_vars):
    service_name = get_vars.get("redis_daemon")

    print(f"redis daemon: {service_name}")

    service = host.service(service_name)
    assert service.is_enabled
    assert service.is_running


def test_open_port(host, get_vars):
    for i in host.socket.get_listening_sockets():
        print(i)

    bind_address = get_vars.get("redis_network", {}).get("bind", ["127.0.0.1"])
    bind_port = get_vars.get("redis_network", {}).get("port", "6379")

    print(f"address: {bind_address}")
    print(f"port   : {bind_port}")

    for address in bind_address:
        if "ansible_default_ipv4.address" in address:
            continue
        service = host.socket(f"tcp://{address}:{bind_port}")
        assert service.is_listening
