#!/bin/bash
#tmpdir=$(mktemp -d)
#if [ -z $tmpdir ]; then
#    echo "Could not create temp dir"
#    exit 1
#fi
#cd $tmpdir
MD5=($(md5sum requirements.txt))
python3 -m venv /tmp/$MD5
ln -s /tmp/$MD5 ./venv
. venv/bin/activate
pip install -r requirements.txt
mkdir -p files/ssh-keys/test
ln -s ~/.ssh/id_rsa.pub files/ssh-keys/test/from_host
