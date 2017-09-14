#!/bin/bash

# This script uses well-known subdomain enumeration tools.
# Output is formatted in a way I prefer.

########    PLEASE SET UP VARIABLES HERE    ########
OUTDIR=/root/bounties           # We will create subfolders for each domain here
SLDIR=/root/scripts/SecLists    # Download SecLists and place it here
EADIR=/root/scripts/enumall     # Download enumall.py and place it here (make sure to configure it)
########    YAY, ALL DONE WITH VARIABLES    ########

read -p 'Enter TLD (example: uber.com): ' RECON_DOMAIN
read -p 'Enter full URL (example: https://uber.com/au) ' RECON_URL

echo $RECON_DOMAIN
echo $RECON_URL

mkdir -p $OUTDIR/$RECON_DOMAIN/dns-recon

# change into dir - as output files from enumall go to local dir
cd $OUTDIR/$RECON_DOMAIN/dns-recon

# create a custom wordlist
cewl --depth 1 -m 4 $RECON_URL \
  -w $OUTDIR/$RECON_DOMAIN/cewl-wordlist.txt
cat $SLDIR/Discovery/DNS/sorted_knock_dnsrecon_fierce_recon-ng.txt \
  $OUTDIR/$RECON_DOMAIN/cewl-wordlist.txt \
  > /tmp/wordlist.txt

# run the consolidated recon
python $EADIR/enumall.py $RECON_DOMAIN -w /tmp/wordlist.txt

# try a DNS zone transfer
for i in $(host -t ns $RECON_DOMAIN | cut -d " " -f 4); \
  do host -l $RECON_DOMAIN $i \
  >> $OUTDIR/$RECON_DOMAIN/dns-recon/zone-transfer.txt; \
done

# remove out of scope domains
cat $RECON_DOMAIN.csv | grep $RECON_DOMAIN \
 > $OUTDIR/$RECON_DOMAIN/dns-recon/$RECON_DOMAIN.csv

# make a list of all unique hostnames
cat $RECON_DOMAIN.csv | cut -d '"' -f 2 | sort | uniq -i | grep $RECON_DOMAIN \
  > $OUTDIR/$RECON_DOMAIN/dns-recon/hostnames.txt

# make a list of all unique IP addresses
cat $RECON_DOMAIN.csv | cut -d '"' -f 4 | grep . | sort | uniq -i \
  > $OUTDIR/$RECON_DOMAIN/dns-recon/ip-list.txt

# make a list of IP addresses with DNS count
cat $RECON_DOMAIN.csv | cut -d '"' -f 4 | grep . | sort | uniq -i -c \
  | cut -d ' ' -f 7- \
  > $OUTDIR/$RECON_DOMAIN/dns-recon/ip-count.txt