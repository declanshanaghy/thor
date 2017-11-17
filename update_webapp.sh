#!/usr/bin/env bash

set -e

source /home/ec2-user/thor/venv/bin/activate
pip install -r /home/ec2-user/thor/webapp/requirements.txt

sudo /usr/local/bin/supervisorctl reread
sudo /usr/local/bin/supervisorctl update
sudo /usr/local/bin/supervisorctl restart thor-web thor-asciiwh
