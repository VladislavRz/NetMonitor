from hive_api import HiveAPI
from ivre_api import IvreAPI
import json
import settings
from settings import Tags
import os.path
import pandas
import argparse


def parse_hosts(hosts):
    # host[0] - IP узла
    # host[1] - список формата [port, status]

    up_hosts = {}
    for host in hosts:
        if host[1]:
            up_hosts[host[0]] = {str(port[0]): port[1] for port in host[1]}

    return up_hosts


def check_port(port, new_ports, old_ports):
    tag = None

    if (port in new_ports.keys()) and (port not in old_ports.keys()):
        tag = Tags.open_p

    elif (port not in new_ports.keys()) and (port in old_ports.keys()):
        tag = Tags.close_p

    elif new_ports[port] != old_ports[port]:
        tag = Tags.change_p

    return tag


def check_host(host, new_hosts, old_hosts):
    tag = None

    if (host in new_hosts.keys()) and (host not in old_hosts.keys()):
        tag = Tags.add_h

    elif (host not in new_hosts.keys()) and (host in old_hosts.keys()):
        tag = Tags.delete_h

    return tag


def parse_host_tag(host, subnet, new_hosts, tag):
    description = None
    artifacts = [['ip', host]]

    if tag == Tags.add_h:
        artifacts.append(['status', 'created'])
        for port in new_hosts[host]:
            artifacts.append(['port', port + ': ' + new_hosts[host][port]])
        description = f'В сети {subnet} обнаружен новый узел {host}'

    elif tag == Tags.delete_h:
        artifacts.append(['status', 'deleted'])
        description = f'Из сети {subnet} удален узел {host}'

    return artifacts, description


def parse_port_tag(port, host, subnet, new_hosts, tag):
    description = None
    artifacts = [['ip', host], ['port', port]]

    if tag == Tags.open_p:
        artifacts.append(['status', new_hosts[host][port]])
        description = f'В сети {subnet} на хосте {host} обнаружен новый порт {port}'

    elif tag == Tags.close_p:
        artifacts.append(['status', 'closed'])
        description = f'В сети {subnet} на хосте {host} закрыт порт {port}'

    elif tag == Tags.change_p:
        artifacts.append(['status', new_hosts[host][port]])
        description = f'В сети {subnet} на хосте {host} порт {port} изменил статус'

    return artifacts, description


def check_changes(new_hosts, old_hosts, subnetne, net_name, hive_api):
    hosts = set(list(new_hosts.keys()) + list(old_hosts.keys()))

    # Проверка хостов
    for host in hosts:
        tag = check_host(host, new_hosts, old_hosts)
        if tag:
            artifacts, description = parse_host_tag(host, subnetne, new_hosts, tag)
            artifacts.append(['Network Name', net_name])
            alert_type = 'Изменение состава сети'
            hive_api.make_alert(host, description, alert_type, artifacts, tag.value)
            continue

        ports = set(list(new_hosts[host].keys()) + list(old_hosts[host].keys()))

    # Проверка портов
        for port in ports:
            tag = check_port(port, new_hosts[host], old_hosts[host])
            if tag:
                artifacts, description = parse_port_tag(port, host, subnetne, new_hosts, tag)
                artifacts.append(['Network Name', net_name])
                alert_type = 'Изменение состава портов'
                hive_api.make_alert(host, description, alert_type, artifacts, tag.value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    file = parser.parse_args().filename

    tbl = pandas.read_csv(file, sep=';', encoding='utf-8')
    nets = list(zip([subnet for subnet in tbl['Network']], [name for name in tbl['Name']]))

    ivre = IvreAPI(settings.ivre_url)
    hive = HiveAPI(settings.hive_url, settings.hive_api_key)

    for subnet, name in nets:
        file = name.replace(' ', '_') + '.json'
        # Получение информации из ivre
        new_state = ivre.get_hosts(subnet)
        new_state = parse_hosts(new_state)

        if os.path.exists(file):
            # Загрузка предыдущего состояния
            with open(file, 'r') as f:
                old_state = json.load(f)

            check_changes(new_state, old_state, subnet, name, hive)

        # Сохранение нового состояния
        with open(file, 'w') as f:
            json.dump(new_state, f)
