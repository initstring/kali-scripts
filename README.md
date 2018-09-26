# Pentest Tools
A junk drawer of pentest tools - nothing special enough for its own repo. Things in here may be out of date, but if you see something you like that isn't working let me know and I will try to fix it up.

Enjoy!

----------------


## osint
- **sub-recon.sh**: Leverages tools like enumall.py (recon-ng), cewl, etc to do some hardcore subdomain enumeration. Useful for a penetration test or for hunting bug bounties.

## password-cracking
- **extract-hashes.py**: This is used to get a nice, clean, hashcat-usable file from a messy password breach. It takes lines from a file and outputs something like this: `some@mail.com:5d41402abc4b2a76b9719d911017c592`. Currently hard-coded for MD5. Future improvements: add more hash type regexes and provide an argument to specify the hash type you are looking for.
- **simple.mask**: A hashcat mask I've been using based on common corporate passwords I run into. Probably not as good as what comes by default with hashcat, and some of the rules are intense so should be run with a timeout.

## web-tools
- **httpspy.py**: Runs a local HTTP/HTTPS server and logs all incoming requests to the console. Might be useful in odd situations where Burp cannot be used for whatever reason.
- **clone-ssl.py**: Makes a CA keypair sort of like a target. Might be useful in web or mobile app pentesting.

## phishing
- **screenshot-macro**: Macro to add to an XLS as a phishing payload. Captures a desktop screenshot and emails it back to the address variable you set, using the default Outlook profile. Pops a message box at the end saying "Sorry, your account is not authorised to view this data." Works well with a spreadsheet that has an obfuscated section that looks tempting enough to enable content to unlock.

## kali-setup
- **setup-kali.sh**: Configuring Kali Linux after a stock installation.
- **kali-macbook.sh**: Fix some small things (wifi, tilde, etc) when running natively on a Macbook.

## oscp
- **oscp-scan.sh**:  Reads IP addresses from a single file and looks for potential entry points. If you're building a custom OSCP script, perhaps this will give you some ideas. Not that handy in the real world, as there are way better tools available.















