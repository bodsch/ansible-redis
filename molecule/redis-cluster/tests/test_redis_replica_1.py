
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

import json
import pytest
import os

import testinfra.utils.ansible_runner

HOST = 'redis_cluster_replica_1'

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(HOST)


def pp_json(json_thing, sort=True, indents=2):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def base_directory():
    """ ... """
    cwd = os.getcwd()

    if ('group_vars' in os.listdir(cwd)):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = f"molecule/{os.environ.get('MOLECULE_SCENARIO_NAME')}"

    return directory, molecule_directory


def read_ansible_yaml(file_name, role_name):
    """
    """
    read_file = None

    for e in ["yml", "yaml"]:
        test_file = f"{file_name}.{e}"
        if os.path.isfile(test_file):
            read_file = test_file
            break

    return f"file={read_file} name={role_name}"


@pytest.fixture()
def get_vars(host):
    """
        parse ansible variables
        - defaults/main.yml
        - vars/main.yml
        - vars/${DISTRIBUTION}.yaml
        - molecule/${MOLECULE_SCENARIO_NAME}/group_vars/all/vars.yml
    """
    base_dir, molecule_dir = base_directory()
    distribution = host.system_info.distribution
    release = host.system_info.release
    operation_system = None

    if distribution in ['debian', 'ubuntu']:
        operation_system = "debian"
    elif distribution in ['redhat', 'ol', 'centos', 'rocky', 'almalinux']:
        operation_system = "redhat"
    elif distribution in ['arch', 'artix']:
        operation_system = f"{distribution}linux"

    print(f"distribution: {distribution}")
    print(f"release     : {release}")

    file_defaults      = read_ansible_yaml(f"{base_dir}/defaults/main", "role_defaults")
    file_vars          = read_ansible_yaml(f"{base_dir}/vars/main", "role_vars")
    file_distibution   = read_ansible_yaml(f"{base_dir}/vars/{operation_system}", "role_distibution")
    file_molecule      = read_ansible_yaml(f"{molecule_dir}/group_vars/all/vars", "test_vars")

    defaults_vars      = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars          = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    distibution_vars   = host.ansible("include_vars", file_distibution).get("ansible_facts").get("role_distibution")
    molecule_vars      = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")
    # host_vars          = host.ansible("include_vars", file_host_molecule).get("ansible_facts").get("host_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)
    # ansible_vars.update(host_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


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


def test_config_file(host, get_vars):
    """
    """
    bind_address = get_vars.get("redis_network", {}).get("bind", "0.0.0.0")
    # bind_port = get_vars.get("redis_network", {}).get("port", "6379")

    master_ip = get_vars.get("redis_replication", {}).get("master_ip")

    bind_string = f"bind {bind_address}"
    replica_of = f"replicaof {master_ip}"

    network_config_file = host.file("/etc/redis.d/network.conf")
    replication_config_file = host.file("/etc/redis.d/replication.conf")
    assert network_config_file.is_file
    assert replication_config_file.is_file

    assert bind_string in network_config_file.content_string
    assert replica_of in replication_config_file.content_string


def test_service_running(host, get_vars):
    service_name = get_vars.get("redis_daemon")

    print(f"redis daemon: {service_name}")

    service = host.service(service_name)
    assert service.is_enabled
    assert service.is_running


def test_open_port(host, get_vars):
    """
    """
    for i in host.socket.get_listening_sockets():
        print(i)

    bind_address = get_vars.get("redis_network", {}).get("bind", "127.0.0.1")
    bind_port = get_vars.get("redis_network", {}).get("port", "6379")

    service = host.socket(f"tcp://{bind_address}:{bind_port}")
    assert service.is_listening
