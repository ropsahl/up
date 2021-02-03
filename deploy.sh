#!/usr/bin/env bash
rsync -a -v -L node_modules up-log.sh up.py up_route.js up.sh pi@192.168.86.175:/home/pi/bin/up

