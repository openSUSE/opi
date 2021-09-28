#!/bin/bash

python3 setup.py install -f
cp -v opi-proxy.service /etc/systemd/system/
systemctl daemon-reload
test -e /etc/opi-proxy.json || cp -v config.sample.json /etc/opi-proxy.json
