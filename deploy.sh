#!/usr/bin/env bash
rsync -a -v -L up-log.sh up.py up_route.js up.sh package.json package-lock.json $1

