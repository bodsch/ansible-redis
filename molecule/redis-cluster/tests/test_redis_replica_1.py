
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

import json
import pytest
import os

import testinfra.utils.ansible_runner

HOST = 'redis_cluster_replica_2'

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(HOST)


def base_directory():
    cwd = os.getcwd()

    if('group_vars' in os.listdir(cwd)):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = "molecule/{}".format(os.environ.get('MOLECULE_SCENARIO_NAME'))

    return directory, molecule_directory


@pytest.fixture()
def get_vars(host):
    """

    """
    base_dir, molecule_dir = base_directory()
    distribution = host.system_info.distribution

    if distribution in ['debian', 'ubuntu']:
        os = "debian"
    elif distribution in ['centos', 'redhat', 'ol']:
        os = "redhat"
    elif distribution in ['arch']:
        os = "archlinux"

    print(" -> {} / {}".format(distribution, os))

    file_defaults = "file={}/defaults/main.yml name=role_defaults".format(base_dir)
    file_vars = "file={}/vars/main.yml name=role_vars".format(base_dir)
    file_distibution = "file={}/vars/{}.yaml name=role_distibution".format(base_dir, os)
    file_molecule = "file={}/group_vars/all/vars.yml name=test_vars".format(molecule_dir)
    file_host_molecule = "file={}/host_vars/{}/vars.yml name=host_vars".format(molecule_dir, HOST)

    defaults_vars = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    distibution_vars = host.ansible("include_vars", file_distibution).get("ansible_facts").get("role_distibution")
    molecule_vars = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")
    host_vars = host.ansible("include_vars", file_host_molecule).get("ansible_facts").get("host_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)
    ansible_vars.update(host_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


def test_package(host, get_vars):
    packages = get_vars.get("redis_packages")

    for pack in packages:
        p = host.package(pack)
        assert p.is_installed


def test_config_file(host, get_vars):
    bind_address = get_vars.get("redis_network_bind")
    master_ip = get_vars.get("redis_replication_master_ip")

    bind_string = "bind {0}".format(bind_address)
    replica_of = "replicaof {0}".format(master_ip)

    network_config_file = host.file("/etc/redis.d/network.conf")
    replication_config_file = host.file("/etc/redis.d/replication.conf")
    assert network_config_file.is_file
    assert replication_config_file.is_file

    assert bind_string in network_config_file.content_string
    assert replica_of in replication_config_file.content_string


def test_service_running(host, get_vars):
    service_name = get_vars.get("redis_daemon")

    service = host.service(service_name)
    assert service.is_running


def test_open_port(host, get_vars):
    for i in host.socket.get_listening_sockets():
        print(i)

    bind_address = get_vars.get("redis_network_bind")
    bind_port = get_vars.get("redis_network_port")

    service = host.socket("tcp://{0}:{1}".format(bind_address, bind_port))
    assert service.is_listening
