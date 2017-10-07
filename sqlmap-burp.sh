#!/bin/bash

# This script starts the API to use sqlmap with the Burp Suite plugin.

IP="$(ifconfig eth0 |grep "netmask" | cut -d " " -f 10)"
PORT=8083
FILE=/usr/share/sqlmap/sqlmapapi.py

echo "Starting sqlmap in server mode for BurpSuite using $IP on port $PORT..."
echo "Hit Ctrl-C to stop..."

python $FILE -s -H $IP -p $PORT