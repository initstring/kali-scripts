#!/bin/bash

# Useful for PWK labs whil studying for OSCP

# Note: this script requires a pre-existing text file
# '/root/iplist.txt)' with one IP address per line to scan.
# You will also need 'seclists' installed here: /root/scripts/seclists
# (find it at https://github.com/danielmiessler/SecLists)

# Running this script in a production environment would be a bad idea -
# it is very chatty and would likely get you in trouble. Don't use this
# anywhere you don't have permission!

# The output is individual text files sorted in folders by target IP located
# in '/root/recon/'

# Usage: ./initial-scan.sh

# Kick off general tasks - some in background
for ip in $(cat /root/iplist.txt); do \
  mkdir -p /root/recon/$ip; \

  echo "Kicking off top ports nmap for $ip..."; \
  nmap --top-ports 50 -sV --open -v $ip \
    >> /root/recon/$ip/$ip-nmap-top.txt \

  echo "Sleeping 10 seconds..."; sleep 10; \
  echo "Kicking off full nmap for $ip..."; \
  nmap -vv -Pn -A -sC -sS -T 4 -p- $ip \
    >> /root/recon/$ip/$ip-nmap-full.txt \

  echo "Sleeping 10 seconds..."; sleep 10; \
  echo "Kicking off UDP nmap for $ip..."; \
  nmap -sU -v $ip >> /root/recon/$ip/$ip-nmap-udp.txt \

  echo "Sleeping 10 seconds..."; sleep 10; \
  echo "Kicking off enum4linux for $ip... in background"; \
  nohup enum4linux $ip >> /root/recon/$ip/$ip-enum4linux.txt & \
  
  echo "Sleeping 10 seconds..."; sleep 10; \
  echo "Kicking off onesixtyone for $ip..."; \
  nohup onesixtyone $ip >> /root/recon/$ip/$ip-onesixtyone.txt & \

  echo "Sleeping 10 seconds..."; sleep 10; \
  echo "Kicking off Gobuster scripts in background for $ip..."; \
  gobuster -u http://$ip \
    -w /root/scripts/seclists/Discovery/Web_Content/common.txt \
    -s '200,204,301,302,307,403,500' -e \
    >> /root/recon/$ip/$ip-gobuster-common.txt & \
  sleep 5; \
  gobuster -u http://$ip \
    -w /root/scripts/seclists/Discovery/Web_Content/cgis.txt \
    -s '200,204,301,302,307,403,500' -e \
    >> /root/recon/$ip/$ip-gobuster-cgis.txt & \

  echo "Sleeping 10 seconds..."; sleep 10; \
  echo "Kicking off nikto in background for $ip..."; \
  nohup nikto -h $ip >> /root/recon/$ip/$ip-nikto.txt & \

  echo "Sleeping 10 seconds..."; sleep 10; \
done
