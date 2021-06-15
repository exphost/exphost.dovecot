#!/bin/bash
./destroy.sh && (rm -r files/ssh-keys roles terraform_tmp */__pycache__;unlink venv)
