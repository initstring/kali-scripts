#!/usr/bin/env python3

"""
This is a very simple web server that will listen to any incoming request and log it to the console.
You can optionally specify a certificate file to use HTTPS.
You can also try to prompt for basic auth.
Might be useful when doing pentests where Burp for some reason isn't an option, or to track pingbacks Collaborator style.

Here is how you generate a certificate to use:
    openssl genrsa -out c.key 2048
    openssl req -new -x509 -days 3650 -key c.key -out c.crt -subj "/C=AU/ST=NSW/L=Sydney/O=IT/OU=IT/CN=*.somewhere.com"
    cat c.key c.crt > ssl.pem
(Or use my cert cloner here: https://gitlab.com/initstring/pentest/blob/master/web-tools/clone-ssl.py)

Then run this tool with the '--cert ssl.pem'

Enjoy!
"""

import sys
if sys.version_info < (3, 0):
    print("\nSorry mate, you'll need to use Python 3+ on this one...\n")
    sys.exit(1)

from http.server import HTTPServer,BaseHTTPRequestHandler
import ssl,argparse,os,re,base64;

#############################           Global Variable Declarations           #############################

class bcolors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    ENDC = '\033[0m'
okBox = bcolors.BLUE +      '[*] ' + bcolors.ENDC
reqBox = bcolors.GREEN +    '[REQUEST FROM] ' + bcolors.ENDC
credsBox = bcolors.RED +    '[CREDS GIVEN]  ' + bcolors.ENDC

parser = argparse.ArgumentParser()
parser.add_argument('interface', type=str, help='Network interface to listen on.', action='store')
parser.add_argument('--cert', '-c', type=str, help='Certificate (pem) file to use.', action='store')
parser.add_argument('-p', '--port', type=int, help='Port for HTTP server. Defaults to 80 or 443 if a \
                    cert file is specified', action='store')
parser.add_argument('-b', '--basic', default=False, action="store_true", help="Prompt for basic auth")

args = parser.parse_args()

interface = args.interface
localPort = args.port or False
basicAuth = args.basic

if args.cert:
    certFile = args.cert
    if not localPort:
        localPort = 443
else:
    certFile = False
    if not localPort:
        localPort = 80


genericHTML = "This is a page, yay."

#############################         End Global Variable Declarations          #############################

class HTTPSpy(BaseHTTPRequestHandler):
    """
    This class will respond to any GET/POST/HEAD, logging the details to the console.
    """
    def generic_reply(self):
        """
        Just sends a simple 200 and the genericHTML defined above.
        If using optional basic auth, will prompt for credentials first
        """
        if basicAuth:
            if 'Authorization' not in self.headers:
                self.request_auth()
                return
            elif 'Basic ' in self.headers['Authorization']:
                self.process_auth()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(genericHTML.encode())
    
    def request_auth(self):
        """
        Will prompt user for credentials using basic auth.
        """
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Auth\"')
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write("Unauthorized.".encode())

    def process_auth(self):
        """
        Decodes basic auth username and password and prints to console
        """
        basic, encoded = self.headers['Authorization'].split(" ")
        plaintext = base64.b64decode(encoded).decode()
        print(credsBox + "HOST: {}, CREDS: {}".format(self.address_string(), plaintext))

    def do_GET(self):
        self.generic_reply()

    def do_POST(self):
        self.generic_reply()

    def do_HEAD(self):
        self.generic_reply()
    
    def log_message(self, format, *args):    
        """
        This function handles all logging to the console.
        """
        print(reqBox + self.address_string())
        print(self.command + " " + self.path)
        print(self.headers)
        if self.command == 'POST':
            contentLength = int(self.headers['Content-Length'])
            print(self.rfile.read(contentLength).decode('utf-8'))


def get_ip(interface):
    """
    This function will attempt to automatically get the IP address of the provided interface.
    """
    try:
        localIp = re.findall(r'inet (?:addr:)?(.*?) ', os.popen('ifconfig ' + interface).read())[0]
    except Exception:
        print(warnBox + "Could not get network interface info. Please check and try again.")
        sys.exit()
    return localIp

def print_details(localIp, localPort, basicAuth, certFile):
    print("\n\n")
    print("########################################")
    print(okBox + "IP ADDRESS:           {}".format(localIp))
    print(okBox + "PORT:                 {}".format(localPort))
    if basicAuth:
        print(okBox + "AUTH:                 Basic")
    if certFile:
        print(okBox + "CERTFILE:             {}".format(certFile))
    print("########################################\n\n")


def main():
    localIp = get_ip(interface)                             # Obtain IP address of target interface
    print_details(localIp, localPort, basicAuth, certFile)  # Print a nice status box
    try:
        httpd = HTTPServer((localIp, localPort), HTTPSpy)   # Start the HTTP server
    except PermissionError:                                 # Oops, no root. Try again.
        print("\nYou need root to bind to that port, try again with sudo.\n")
        sys.exit()
    if certFile:                                            # If using a certificate, wrap in SSL
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=certFile, server_side=True)
    try:
        httpd.serve_forever()                               # Start the webserver
    except KeyboardInterrupt:                               # Break on Ctrl>C
        print("\nThanks for playing, exiting now...\n")
        sys.exit()

if __name__ == "__main__":
    main()

