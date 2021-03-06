#!/bin/bash

##### NOTE: RUN THIS FROM A TERMINAL WIHIN A GUI SESSION (WINE DEPS) ####
#####     Last tested with Kali 2017.2. Use at your own risk!        ####

tput setaf 1; echo "You should be launching the from the terminal within a desktop session, as some of the scripts launch GUI commands..."; tput sgr0
read -p "Press enter to continue"

read -p "Would you like to set a new password? [Y,N]: " INPUT
if [[ $INPUT == "Y" || $INPUT == "y" ]]; then
        passwd
else
        echo "OK, continuing..."
fi

read -p "Would you like to change you hostname? Kali sounds shady in logs... [Y,N]: " INPUT
if [[ $INPUT == "Y" || $INPUT == "y" ]]; then
        read -p "Let's set a new hostname: " HOSTNAME
        echo $HOSTNAME > /etc/hostname
        hostname $HOSTNAME
        sed -i "s/kali/$HOSTNAME/g" /etc/hosts
else
        echo "OK, continuing..."
fi

apt update; apt upgrade -y

tput setaf 1; echo "Configuring text-based address bar in file browser..."; tput sgr0
gsettings set org.gnome.nautilus.preferences always-use-location-entry true

tput setaf 1; echo "Setting up a /root/scripts/ directory for you..."; tput sgr0
mkdir /root/scripts

tput setaf 1; echo "Updating ruby..."; tput sgr0
gem update --system

tput setaf 1; echo "Enabling dependencies for SystemMonitor and installing it (enable in Tweaks)..."; tput sgr0
apt install gnome-shell-extension-system-monitor gir1.2-networkmanager-1.0 gir1.2-gtop-2.0 -y

tput setaf 1; echo "Starting github clones..."; tput sgr0
cd /opt/
for repo in \
    leebaird/discover                 `# Nice DNS/human recon tool with integrated HTML report output` \
    danielmiessler/SecLists           `# Wordlists for DNS, passwords, users, fuzzing, etc` \
    fuzzdb-project/fuzzdb             `# More wordlists!` \
    jhaddix/domain                    `# Sub-domain enumeration tool` \
    wireghoul/graudit                 `# greo auditing for source code review` \
    pentestgeek/phishing-frenzy       `# Phishing framework with nice web UI` \
    tcstool/NoSQLMap                  `# MongoDB and CouchDB scanning and exploitation` \
    DanMcInerney/net-creds            `# Scans pcap files for passwords and hashes` \
    samratashok/nishang               `# PowerShell tools for all phases of the pentest` \
    brav0hax/smbexec                  `# A rapid psexec style attack with samba tools` \
    cheetz/Easy-P                     `# auto-generates commong PowerShell commands` \
    codingo/VHostScan                 `# Discovers virtual web hosts on a server` \
    nidem/kerberoast                  `# Set of scripts for kerberoasting` \
    EmpireProject/Empire              `# Consolidated PowerShell attack framework` \
    drwetter/testssl.sh               `# SSL test script ` \
    CoreSecurity/impacket             `# Python classes for working with network protocols` \
    nyxgeek/lyncsmash                 `# Awesome username enumeration through SkypeBusiness` \
    bbb31/slurp                       `# S3 bucket enumeration tool` \
    swisskyrepo/PayloadsAllTheThings  `# More intruder payloads` \
    initstring/linkedin2username      `# My shitty username generator` \
    bugcrowd/HUNT                     `# Awesome methodology plugin for Burp` \
    oblique/create_ap                 `# Easy AP tool for creating hotspots` \
  ;do \
  tput setaf 1; echo "Cloning $repo..."; tput sgr0; \
  git clone https://github.com/$repo.git; \
done

tput setaf 1; echo "Configuring the discovery scripts, which also updates the distro..."; tput sgr0
cd /opt/discover && ./update.sh

tput setaf 1; echo "Discover calls harvester directly - fixing permissions so it works..."; tput sgr0
chmod u+x /usr/share/theharvester/theHarvester.py

tput setaf 1; echo "Downloading neo4j for you, as prompted by the discovery install..."; tput sgr0
cd /opt
wget https://neo4j.com/artifact.php?name=neo4j-community-3.2.5-unix.tar.gz -O ./neo4j.tar.gz
tar -xf ./neo4j.tar.gz
rm -f ./neo4j.tar.gz

tput setaf 1; echo "Configuring Veil framework..."; tput sgr0
# Note: already installed in the discovery script above. If not, you can run:
# git clone https://github.com/Veil-Framework/Veil.git /opt/Veil
cd /opt/Veil/setup
./setup.sh -c

tput setaf 1; echo "Confiuring Empire..."; tput sgr0
echo "" | /opt/Empire/setup/install.sh

tput setaf 1; echo "Preparing Metasploit..."; tput sgr0
systemctl enable postgresql; systemctl start postgresql
msfdb init
echo exit | msfconsole                                                 # sets up the needed .msf4 folder
echo "spool /root/msf_console.log" > /root/.msf4/msfconsole.rc         # enables logging of all msf activity

tput setaf 1; echo "Installing tools with easy installs..."; tput sgr0
apt install wifiphisher openvas crackmapexec hostapd-wpe bettercap -y
gem install aquatone
ln -s /usr/bin/crackmapexec /usr/bin/cme # creating a short alias

tput setaf 1; echo "Configuring impacket..."; tput sgr0
cd /opt/impacket
python ./setup.py install

tput setaf 1; echo "Installing some messy requirements for smbexec..."; tput sgr0
cd /tmp
wget https://github.com/libyal/libesedb/releases/download/20170121/libesedb-experimental-20170121.tar.gz
tar -xzvf ./libesedb-experimental-20170121.tar.gz
cd libesedb-20170121
CFLAGS="-g -O2 -Wall -fgnu89-inline" ./configure --enable-static-executables
make
mv esedbtools /opt/esedbtools

tput setaf 1; echo "Configuring smbexec..."; tput sgr0
wget https://github.com/interference-security/ntds-tools/raw/master/ntdsxtract_v1_0.zip -O /tmp/ntds.zip
unzip /tmp/ntds.zip -d /tmp/
mv "/tmp/NTDSXtract 1.0" /opt/NTDSXtract
apt-get install automake autoconf autopoint gcc-mingw-w64-x86-64 libtool pkg-config
echo 1 | /opt/smbexec/install.sh

tput setaf 1; echo "Getting DSHashes script, we need it for smbexec..."; tput sgr0
cd /tmp
wget https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/ptscripts/source-archive.zip
unzip ./source-archive.zip
mkdir /opt/NTDSXtract
cp /tmp/ptscripts/trunk/dshashes.py /opt/NTDSXtract/

tput setaf 1; echo "Installing spiderfoot, another OSINT tool..."; tput sgr0
wget http://sourceforge.net/projects/spiderfoot/files/spiderfoot-2.11.0-src.tar.gz/download -O /tmp/spider.tar.gz
tar xzvf /tmp/spider.tar.gz -C /opt/
pip install lxml
pip install netaddr
pip install M2Crypto
pip install cherrypy
pip install mako
rm -f /tmp/spider.tar.gz

tput setaf 1; echo "Installing jython2.7 for use with Burp..."; tput sgr0
cd /tmp
wget https://repo1.maven.org/maven2/org/python/jython-installer/2.7.0/jython-installer-2.7.0.jar
java -jar /tmp/jython-installer-2.7.0.jar -s -d /opt/jython


tput setaf 1; echo "Configuring gitrob..."; tput sgr0
apt install libpq-dev -y zlib1g-dev
runuser -l postgres -c 'createuser -s gitrob --pwprompt'
runuser -l postgres -c 'createdb -O gitrob gitrob'
gem install gitrob

tput setaf 1; echo "Preparing gitrob... provide the password from earlier"; tput sgr0
gitrob --configure

tput setaf 1; echo "All done, yay!"; tput sgr0
