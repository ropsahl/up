#!/usr/bin/env bash
mkdir -p up-logs
while read line ; do
  echo "$(date +'%y-%m-%0d %H:%M:%S')" ';' $1 ';' $line >> up-logs/$1.log 2>&1
done
