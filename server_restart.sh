#!/usr/bin/env bash

set -e

sudo /usr/local/bin/supervisorctl reread
sudo /usr/local/bin/supervisorctl update
sudo /usr/local/bin/supervisorctl restart thor-asciiwh
