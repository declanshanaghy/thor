#!/usr/bin/env bash

set -e

source /home/ec2-user/thor/venv/bin/activate
pip install -r /home/ec2-user/thor/webapp/requirements.txt
