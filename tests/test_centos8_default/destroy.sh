#!/bin/bash
for instance in terraform_tmp/*; do
    echo "Destroy $instance"
    pushd $instance
    terraform destroy -auto-approve
    pwd
    popd
done
