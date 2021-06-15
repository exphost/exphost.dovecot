#!/bin/bash
chmod 400 ssh_config
py.test --hosts='ansible://test' --ansible-inventory=./libvirt-inventory.py --ssh-config ssh_config --color=yes verify.d
exit $?
