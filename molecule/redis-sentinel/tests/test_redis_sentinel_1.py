
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
import pytest
import os
import testinfra.utils.ansible_runner

import pprint
pp = pprint.PrettyPrinter()

HOST = 'redis_sentinel_1'


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(HOST)

def base_directory():
    """
    """
    cwd = os.getcwd()

    if 'group_vars' in os.listdir(cwd):
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
    operation_system = None

    if distribution in ['debian', 'ubuntu']:
        operation_system = "debian"
    elif distribution in ['redhat', 'ol', 'centos', 'rocky', 'almalinux']:
        operation_system = "redhat"
    elif distribution in ['arch', 'artix']:
        operation_system = f"{distribution}linux"

    # print(" -> {} / {}".format(distribution, os))
    # print(" -> {}".format(base_dir))

    file_defaults      = read_ansible_yaml(f"{base_dir}/defaults/main", "role_defaults")
    file_vars          = read_ansible_yaml(f"{base_dir}/vars/main", "role_vars")
    file_distibution   = read_ansible_yaml(f"{base_dir}/vars/{operation_system}", "role_distibution")
    file_molecule      = read_ansible_yaml(f"{molecule_dir}/group_vars/all/vars", "test_vars")
    file_host_molecule = read_ansible_yaml(f"{molecule_dir}/host_vars/{HOST}/vars", "host_vars")

    defaults_vars      = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars          = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    distibution_vars   = host.ansible("include_vars", file_distibution).get("ansible_facts").get("role_distibution")
    molecule_vars      = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")
    host_vars          = host.ansible("include_vars", file_host_molecule).get("ansible_facts").get("host_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)
    ansible_vars.update(host_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


@pytest.mark.parametrize("packages", [
    "redis-server",
    "redis-sentinel",
    "redis-tools"
])
def test_package(host, packages):
    p = host.package(packages)
    assert p.is_installed


def test_config_file(host, get_vars):
    """
    """
    bind_address = get_vars.get("redis_network", {}).get("bind", "0.0.0.0")
    bind_port = get_vars.get("redis_network", {}).get("port", "6379")

    bind_string = f"bind {bind_address}"
    port_string = f"port {bind_port}"

    net_config_file = host.file("/etc/redis.d/network.conf")

    assert net_config_file.is_file

    assert bind_string in net_config_file.content_string
    assert port_string in net_config_file.content_string

def test_sentinel_config_file(host, get_vars):
    """
    """
    bind_address = get_vars.get("redis_sentinel", {}).get("bind", "0.0.0.0")
    bind_port = get_vars.get("redis_sentinel", {}).get("port", "26379")
    announce_ip = get_vars.get("redis_sentinel", {}).get("announce_ip", "127.0.0.1")

    master_ip = get_vars.get("redis_replication", {}).get("master_ip")

    bind_string = f"bind {bind_address}"
    port_string = f"port {bind_port}"
    announce_string = f"sentinel announce-ip \"{announce_ip}\""

    config_file = host.file("/etc/redis/sentinel.conf")

    assert config_file.is_file

    assert bind_string in config_file.content_string
    assert port_string in config_file.content_string
    assert announce_string in config_file.content_string


def test_running_redis_service(host):
    service = host.service("redis-server")
    assert service.is_running


def test_running_sentinel_service(host):
    service = host.service("redis-sentinel")
    assert service.is_running


def test_open_port(host, get_vars):
    for i in host.socket.get_listening_sockets():
        pp.pprint(i)

    bind_address = get_vars.get("redis_network", {}).get("bind", "0.0.0.0")
    bind_port = get_vars.get("redis_network", {}).get("port", "6379")

    sentinel_address = get_vars.get("redis_sentinel", {}).get("bind")
    sentinel_port = 26379

    sockets = [
        f"tcp://{bind_address}:{bind_port}",
        f"tcp://{sentinel_address}:{sentinel_port}",
    ]

    for socket in sockets:
        service = host.socket(socket)
        assert service.is_listening
