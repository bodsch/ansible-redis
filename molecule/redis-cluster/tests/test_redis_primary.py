from __future__ import annotations, unicode_literals

import os

import testinfra.utils.ansible_runner
from helper.molecule import get_vars, infra_hosts, local_facts

testinfra_hosts = infra_hosts(host_name="redis_primary")

# --- tests -----------------------------------------------------------------


def test_config_file(host, get_vars):
    """ """
    redis_config = get_vars.get("redis_config_file")
    bind_address = get_vars.get("redis_network").get("bind", [])

    bind_string = f"bind {bind_address[0]}"

    net_config_file = host.file(redis_config)
    assert net_config_file.is_file

    assert bind_string in net_config_file.content_string
