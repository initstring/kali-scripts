#!/bin/bash

# Set up additional packages
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
echo "deb https://download.docker.com/linux/debian stretch stable" >> /etc/apt/sources.list 
apt update
apt install npm docker-ce -y
gem install aquatone

# Set up some directories
mkdir /root/scripts

# Grab some good open source stuff
cd /root/scripts
git clone https://github.com/danielmiessler/SecLists.git
git clone https://github.com/jhaddix/domain; move ./domain ./enumall
