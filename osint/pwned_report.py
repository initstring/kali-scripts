#!/usr/bin/env python3

"""
This tool queries the haveibeenpwned API to return a list of breached
email addresses.

There are other tools that do the same, maybe better, but I wanted something
that creates an output I can paste directly into a pentest report. Also it
is smart enough to extract valid email addresses anywhere in a text file,
so you don't need to clean anything up first.

Enjoy!

github.com/initstring
"""

import argparse
import requests
import time
import re
import os
import sys


# Global variables for most-likely-to-change items:
#   - API bans may happen at the User-Agent level
#   - API endpoint may change
USER_AGENT = 'pwned_reportv1'
API_URL = 'https://haveibeenpwned.com/api/v2/breachedaccount'


def process_args():
    """Handles user-passed parameters"""
    parser = argparse.ArgumentParser(description='Check haveibeenpwned for'
                                     ' compromised email addresses.')

    parser.add_argument('-f', '--infile', required=True, type=str,
                        help='Text file with email addresses, formatted'
                        ' anyway you like.')
    parser.add_argument('-s', '--sleep', default=0.5, type=int,
                        help='Seconds to sleep between each email. Default'
                        ' is .5 seconds.')
    parser.add_argument('-o', '--outfile', default='pwned.txt', type=str,
                        help='Log file to write output to. Default is'
                        ' pwned.txt')

    args = parser.parse_args()

    if not os.access(args.infile, os.R_OK):
        print("[!] Cannot access input file, please try again.")
        sys.exit()

    return args


def find_emails(infile):
    """
    Uses a regex to extract all email address from an input file.
    """
    # Thanks to regular-expressions.info for this regex
    regex = '[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}'

    # Read the file into a string, extract vaid emails
    print("[+] Processing {}".format(infile))
    with open(infile) as file_handler:
        raw_text = file_handler.read()
        emails = re.findall(regex, raw_text, re.IGNORECASE)

    if not emails:
        print("[!] No valid emails found, exiting.")
        sys.exit

    print("[+] Found {} valid email addresses in {}"
          .format(len(emails), infile))
    
    return emails


def collect_results(emails, sleep_time):
    """
    Grabs the raw, truncated, results from the API.
    """
    # API demands a custom header, so we set it here
    headers = {'User-Agent': USER_AGENT}

    # Initialize a dictionary for all the results
    results = {}

    # Start a counter for failed responses
    failed_count = 0

    # Start a counter for the status bar
    counter = 1

    for address in emails:
        url = API_URL + '/{}?truncateResponse=true'.format(address)
        res = requests.get(url, headers=headers)
        
        # Quick and dirty status counter
        sys.stdout.write('\r')
        sys.stdout.write("[+] Checking {} out of {}"
                        .format(counter, len(emails)))

        # A 403 response code usually means rate limiting
        if res.status_code is 403:
            failed_count += 1
            if failed_count >= 3:
                print("[!] Possible rate limiting encountered.")
                sys.exit()

        # A response with text means breaches found. Add to dictionary.
        if res.text:
            results[address] = res.text

        # Increment the counter and flush stdout
        counter += 1
        sys.stdout.flush()
        
        # Sleep to avoid rate limiting
        time.sleep(sleep_time)

    print("") # Need a new line after using sys.stdout to display counter
    print("[+] Found {} accounts with breach data".format(len(results)))
    return results


def format_results(results):
    """
    Outputs the breach data via markdown, ready to paste into a report.
    """
    # Initialize a new dictionary of known breach names
    known_breaches = {}

    # Breaches are returned in JSON-like format
    regex = '"Name":"(.*?)"'

    # Loop through our results, building the new dictionary ordered
    # by breach name instead of account name
    for address in results:
        breaches = re.findall(regex, results[address], re.IGNORECASE)
        for breach in breaches:
            if breach in known_breaches:
                known_breaches[breach].append(address)
            else:
                known_breaches[breach] = [address,]

    return known_breaches


def deliver_results(results, outfile):
    """
    Write final results to log file.
    """
    print("[+] Writing results to {}".format(outfile))
    with open(outfile, 'w') as file_handler:
        for breach in results:
            file_handler.write('**{}**\n'.format(breach))
            for email in results[breach]:
                file_handler.write('* {}\n'.format(email))
            file_handler.write('\n')

    print("[+] All done, enjoy!")
    return



def main():
    """
    Main program function.
    """
    args = process_args()
    emails = find_emails(args.infile)
    raw_results = collect_results(emails, args.sleep)
    final_results = format_results(raw_results)
    deliver_results(final_results, args.outfile)


if __name__ == '__main__':
    main()