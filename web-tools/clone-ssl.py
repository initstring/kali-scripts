#!/usr/bin/env python3
import argparse,OpenSSL,ssl,os,random;

"""
This script allows you to create a TLS certificate and key that mimics a target domain.
It will first create a CA similar to that of your target, and then use that to sign a second certificate.
Useful for things like web and mobile app pentesting. Includes things like expiry dates, subject, and extensions.

You'll get an output folder with a bunch of files. Far from me to tell you what to do with them, but I tend to use the
following:
    - client.pem: Use this to run your spoofed webserver/proxy/etc
    - ca.crt: Import this as a trusted CA in a mobile device or browser

I'm definitely not a TLS expert, so please let me know if you have better ideas.

This doesn't make a complete chain, only one step back, that could be a future improvement.

Enjoy!

Thanks to these threads:
stackoverflow.com/questions/7689941/how-can-i-retrieve-the-tls-ssl-peer-certificate-of-a-remote-host-using-python
stackoverflow.com/questions/45873832/how-do-i-create-and-sign-certificates-with-pythons-pyopenssl
stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python
"""

#############################           Global Variable Declarations           #############################

parser = argparse.ArgumentParser()
parser.add_argument('domain', type=str, help='Domain name to grab cert from (i.e. google.com)', action='store')
parser.add_argument('--port', '-p', type=int, default=443, help='Target port (default 443)', action='store')
args = parser.parse_args()

targetDomain = args.domain
targetPort = args.port

#############################         End Global Variable Declarations          #############################

class CertParameters:
    def __init__(self):
        self.certSubject = ''
        self.certSerial = ''
        self.certStart = ''
        self.certEnd = ''
        self.certVersion = ''
        self.certIssuer = ''         # Not cloning this for now, due to the clash you will get with a dupe serial/issuer
        self.certExtensions = []

class FileNames:
    def __init__(self):
        self.caCrtFile = 'ca.crt'
        self.caKeyFile = 'ca.key'
        self.caPemFile = 'ca.pem'
        self.clientCrtFile = 'client.crt'
        self.clientKeyFile = 'client.key'
        self.clientPemFile = 'client.pem'

def get_cert(targetDomain, targetPort):
    try:
        rawCert = ssl.get_server_certificate((targetDomain, targetPort))
        print("[+] Got the certificate...")
        return rawCert
    except:
        print("[!] Sorry, error getting certificate from {} on port {}.".format(targetDomain, targetPort))

def parse_cert(params, cert):
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
    params.certSubject = cert.get_subject()
    params.certSerial = cert.get_serial_number()
    params.certStart = cert.get_notBefore()
    params.certEnd = cert.get_notAfter()
    params.certVersion = cert.get_version()
    params.certIssuer = cert.get_issuer()
    params.certExtensions = []
    for i in range(0, cert.get_extension_count()):
        extText = cert.get_extension(i).__str__()
        if 'keyid' not in extText:
            params.certExtensions.append(cert.get_extension(i))
    print("[+] Parsed the certificate...")
    return(params)

def make_ca_cert(params):
    """
    First, we make a fake CA cert to mimic the 'issuer' of our client.
    We will then use this CA cert to sign our client cert.
    You can add the fake CA cert to your trusted profiles on your mobile device / OS / browser / etc for testing.
    """
    caKey = OpenSSL.crypto.PKey()
    caKey.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
    cert = OpenSSL.crypto.X509()

    # Set some basic required parameters
    cert.set_version(2)
    cert.set_serial_number(random.randint(50000000,100000000))
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)

    # The next line will set this cert's name to be the issuer of the target client cert, issued by itself
    cert.set_subject(params.certIssuer)
    cert.set_issuer(params.certIssuer)
    
    # Now we define the necessary settings for this to be a CA cert
    cert.add_extensions([
        OpenSSL.crypto.X509Extension(b"basicConstraints", True, b"CA:TRUE, pathlen:0"),
        OpenSSL.crypto.X509Extension(b"keyUsage", True, b"keyCertSign, cRLSign"),
        OpenSSL.crypto.X509Extension(b"subjectKeyIdentifier", False, b"hash", subject=cert),
        ])
    cert.add_extensions([
        OpenSSL.crypto.X509Extension(b"authorityKeyIdentifier", False, b"keyid:always",issuer=cert)
        ])

    # Sign it and we're done
    cert.set_pubkey(caKey)
    cert.sign(caKey, 'sha256')

    print("[+] Made the fake CA cert...") 

    return caKey, cert

def make_client_cert(params, caKey, caCert):
    clientKey = OpenSSL.crypto.PKey()
    clientKey.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
    cert = OpenSSL.crypto.X509()

    # The following lines attempt to mimic attributes of a target domain's cert
    cert.set_subject(params.certSubject)
    cert.set_serial_number(params.certSerial)
    cert.set_notBefore(params.certStart)
    cert.set_notAfter(params.certEnd)
    cert.set_issuer(params.certIssuer)
    cert.set_version(params.certVersion)

    # Now we set the issuer to our fake CA
    cert.add_extensions([
        OpenSSL.crypto.X509Extension(b"authorityKeyIdentifier", False, b"keyid:always",issuer=caCert)
        ])

    # Add in all the custom extensions we scraped from the target domain
    cert.add_extensions(params.certExtensions)

    # Sign it and we're done
    cert.set_pubkey(clientKey)
    cert.sign(caKey, 'sha256')

    print("[+] Made the fake client cert...")

    return clientKey, cert

def write_files(caCrt, caKey, clientCrt, clientKey, fileNames):
    dir = 'clonessl-output'
    if not os.path.exists(dir):
            os.makedirs(dir)

    caCrtBytes = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, caCrt)
    caKeyBytes = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, caKey)
    clientCrtBytes = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, clientCrt)
    clientKeyBytes = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, clientKey)

    # First write key, crt, and pem file for the CA
    open(dir + '/' + fileNames.caKeyFile, 'wb').write(caKeyBytes)
    open(dir + '/' + fileNames.caCrtFile, 'wb').write(caCrtBytes)
    open(dir + '/' + fileNames.caCrtFile, 'wb').write(caCrtBytes)

    # Same for the client, where the pem file also includes the chain of crts back to the fake CA
    open(dir + '/' + fileNames.clientCrtFile, 'wb').write(clientCrtBytes)
    open(dir + '/' + fileNames.clientKeyFile, 'wb').write(clientKeyBytes)
    open(dir + '/' + fileNames.clientPemFile, 'wb').write(clientKeyBytes + b'\n' 
        + clientCrtBytes + b'\n'
        + caCrtBytes)

    print("[+] Wrote the following files to {}:".format(dir))
    for i in vars(fileNames):
        print("    * " + vars(fileNames)[i])

def main():
    fileNames = FileNames()
    params = CertParameters()
    targetCert = get_cert(targetDomain, targetPort)
    params = parse_cert(params, targetCert)
    caKey, caCrt = make_ca_cert(params)
    clientKey, clientCrt = make_client_cert(params, caKey, caCrt)
    write_files(caCrt, caKey, clientCrt, clientKey, fileNames)


if __name__ == "__main__":
    main()

