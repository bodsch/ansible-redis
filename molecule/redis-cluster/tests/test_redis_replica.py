from __future__ import annotations, unicode_literals

import os

import testinfra.utils.ansible_runner
from helper.molecule import get_vars, infra_hosts, local_facts

testinfra_hosts = infra_hosts(host_name="redis_replica")

# --- tests -----------------------------------------------------------------


def test_config_file(host, get_vars):
    """ """
    import re

    redis_config = get_vars.get("redis_config_file")
    primary_address = get_vars.get("redis_replication").get("master_ip", None)
    primary_port = get_vars.get("redis_replication").get("master_port", "6379")

    net_config_file = host.file(redis_config)
    re_replicaof = re.compile(f"replicaof {primary_address} {primary_port}")

    content = net_config_file.content_string.split("\n")

    assert net_config_file.is_file
    assert len(list(filter(re_replicaof.match, content))) > 0
