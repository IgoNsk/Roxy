#!/bin/bash

set -xe

virtualenv --no-site-packages --python=/usr/bin/python3 ./venv
source ./venv/bin/activate
pip install -r requirements.txt