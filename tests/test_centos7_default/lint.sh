#!/bin/bash
result=0
trap 'result=1' ERR
yamllint roles/tested_role

ansible-lint dummy_playbook.yml --exclude $(ls roles/exphost.* -d|grep -v "^roles/$ROLENAME$"|paste -s -d ,|sed 's/,/ --exclude /g')
exit $result

