#!/bin/bash
ANSIBLE_CONFIG=fabsible.cfg ansible -i libvirt-inventory.py test -b  -m reboot
ANSIBLE_CONFIG=fabsible.cfg ansible -i libvirt-inventory.py test -m wait_for -a port=22
