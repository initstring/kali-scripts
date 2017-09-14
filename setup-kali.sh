#!/bin/bash

# Set up Docker
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
echo "deb https://download.docker.com/linux/debian stretch stable" >> /etc/apt/sources.list 
apt update
apt install docker-ce -y

# Install node-js
cd /tmp
git clone git://github.com/nodejs/node.git
cd node
./configure
make install
apt install npm -y

# Add more pentesting tools
gem install aquatone

# Set up some directories
mkdir /root/scripts

# Grab some good open source scripts, etc
cd /root/scripts
git clone https://github.com/danielmiessler/SecLists.git
git clone https://github.com/jhaddix/domain; move ./domain ./enumall

