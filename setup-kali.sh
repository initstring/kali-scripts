#!/bin/bash

# Set up Docker
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
echo "deb https://download.docker.com/linux/debian stretch stable" >> /etc/apt/sources.list 
apt update
apt install docker-ce -y

# Install node-js
apt install nodejs npm -y

# Install aquatone for bounty recon
gem install aquatone

# Set directory to store new stuff
mkdir /root/scripts

# Grab some good open source scripts, etc
cd /root/scripts
git clone https://github.com/danielmiessler/SecLists.git
git clone https://github.com/jhaddix/domain; mv ./domain ./enumall
git clone https://github.com/wireghoul/graudit.git

# Get ready to decompile flash stuff
wget https://www.free-decompiler.com/flash/download/ffdec_10.0.0.deb
apt install ./ffdec_10.0.0.deb -y                                                       # for editing the swf packages
apt install gnash -y                                                                    # for testing locally the swf files
rm -f ./ffdec_10.0.0.deb
mkdir /root/scripts/flash-stuff; cd /root/scripts/flash-stuff
wget https://fpdownload.macromedia.com/get/flashplayer/updaters/27/playerglobal27_0.swc # required to edit scripts inline
