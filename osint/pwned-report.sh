#!/bin/bash

# This is a very simple (and ugly) script used to report on breached
# passwords. It returns a list in markdown format, simply because that is
# what I need for my reports.
#
# If you get 403 errors, change to a new User-Agent. That's what the API uses
# to ban bad behaviour.
#
# github.com/initstring

AGENT="pwned_report.sh"
URL="https://haveibeenpwned.com/api/v2/breachedaccount"
SLEEP=".5s"

# Give advice on how to run script
if [ $# -eq 0 ]
  then
    echo "Usage: pwned_report.sh <file name>"
    echo "<file name> should be a text file with one email per line."
    exit 1
fi

for EMAIL in `cat $1`; do
  RES=$(curl -s \
        $URL/$EMAIL?truncateResponse=true \
        -H "User-Agent: $AGENT")

  if echo $RES | grep -q 'Access denied'; then
    echo "[!] Rate limiting, shoot!"
    exit 1
  fi
  
  if [ ${#RES} -gt 1 ]; then
    BREACHES=$(echo $RES | grep -oP '"Name":"((.*?))"')
    echo "* $EMAIL:"
    for LINE in $BREACHES; do
      echo "  * `echo $LINE | cut -d '"' -f 4` "
    done
  fi

  # Sleep to avoid rate limiting
  sleep $SLEEP
done
