#!/bin/bash
[ -z $ROLENAME ] && exit 1
echo "ROLENAME=$ROLENAME"
ansible-galaxy install -p roles -r requirements.yml
[ -L roles/$ROLENAME ] && unlink roles/$ROLENAME
[[ ! -L roles/$ROLENAME && -d roles/$ROLENAME ]] && rm -r roles/$ROLENAME
ln -s ../../../ roles/$ROLENAME
ln -s ../../../ roles/tested_role
ls roles
