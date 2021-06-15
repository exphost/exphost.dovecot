#!/usr/bin/env python
### conf section
#NAME_FILTER = ''
STATE_MASK = None
STATE_MASK = [0,1,2,3,4,5,6,7,8]
#NAME_FILTER = '^exphost-.*'
#CLUSTER_NAME= 'exphost-dev'

import libvirt
import re
import json
import yaml
import jinja2
import os

def lookup(type, key):
    if type=="env":
        return os.environ.get(key)
    return None

URI = jinja2.Template("{{ lookup('env', 'QEMU_URI')|default('qemu:///system', true) }}").render(lookup=lookup)

with open("group_vars/all/iac.yml", "r") as f:
    iac = yaml.safe_load(f)
    CLUSTER_NAME = jinja2.Template(iac['iac']['name']).render(lookup=lookup)

def libvirt_callback(userdata, err):
    pass

libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)


#name_filter_re = re.compile(NAME_FILTER)

conn = libvirt.open(URI)

inventory = {}
inventory['all'] = {'hosts': []}

for domain in conn.listAllDomains():

    hostname = domain.name()
    try:
        metadata = (domain.metadata(type=0, uri=None)).split("\n")
        this_cluster = False
        for desc in metadata:
            if desc.startswith("cluster:"):
                if desc.split("cluster:")[1].strip() == CLUSTER_NAME:
                    this_cluster = True
            if desc.startswith("hostname:"):
                hostname = desc.split("hostname:")[1].strip()
        if not this_cluster:
            continue
    except libvirt.libvirtError:
        continue

    hostname = hostname.replace("_","-")

    if STATE_MASK and not domain.state()[0] in STATE_MASK:
        continue

    inventory['all']['hosts'].append(hostname)

    try:
        addresses = domain.interfaceAddresses(1)
        ### Take the eth0 interface
        ip_address = addresses['eth0']['addrs'][0]['addr']
        if "_meta" not in inventory:
            inventory['_meta'] = {'hostvars': {}}
        if domain not in inventory['_meta']['hostvars']:
            inventory["_meta"]['hostvars'][hostname] = {}
        inventory['_meta']['hostvars'][hostname]['ansible_host'] = ip_address
    except libvirt.libvirtError:
        pass

    try:
        metadata = domain.metadata(type=0, uri=None)
        for desc_line in metadata.split("\n"):
            if desc_line.startswith("roles: "):
                roles = desc_line.split("roles:")[1].strip().split(",")
                for role in roles:
                    if role not in inventory:
                        inventory[role] = {'hosts': []}
                    inventory[role]['hosts'].append(hostname)
                        
    except libvirt.libvirtError:
        pass
print(json.dumps(inventory, indent=4, sort_keys=True))
