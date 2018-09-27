#!/usr/bin/env python3
import argparse,OpenSSL,ssl;

"""
This script allows you to create a TLS keypair similar to a target.
May be useful for things like mobile app pentesting.
Includes things like expiry dates, subject, and extensions.
Enjoy!

Thanks to these threads:
https://stackoverflow.com/questions/7689941/how-can-i-retrieve-the-tls-ssl-peer-certificate-of-a-remote-host-using-python
https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python
"""

#############################           Global Variable Declarations           #############################

parser = argparse.ArgumentParser()
parser.add_argument('domain', type=str, help='Domain name to grab cert from (i.e. google.com)', action='store')
parser.add_argument('--port', '-p', type=int, default=443, help='Target port (default 443)', action='store')
args = parser.parse_args()

targetDomain = args.domain
targetPort = args.port

certFile = 'ssl.crt'
keyFile = 'ssl.key'
pemFile = 'ssl.pem'
#############################         End Global Variable Declarations          #############################

class CertParameters:
    certSubject = ''
    certSerial = ''
    certStart = ''
    certEnd = ''
    certIssuer = ''         # Not cloning this for now, due to the clash you will get with a dupe serial/issuer
    certExtensions = []


def get_cert(targetDomain, targetPort):
    try:
        rawCert = ssl.get_server_certificate((targetDomain, targetPort))
        print("[+] Got the certificate...")
        return rawCert
    except:
        print("[!] Sorry, error getting certificate from {} on port {}.".format(targetDomain, targetPort))

def parse_cert(cert):
    params = CertParameters
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
    params.certSubject = cert.get_subject()
    params.certSerial = cert.get_serial_number()
    params.certStart = cert.get_notBefore()
    params.certEnd = cert.get_notAfter()
    params.certVersion = cert.get_version()
    params.certExtensions = []
    for i in range(0, cert.get_extension_count()):
        params.certExtensions.append(cert.get_extension(i))
    print("[+] Parsed the certificate...")
    return(params)

def make_cert(params):
    # create a key pair
    k = OpenSSL.crypto.PKey()
    k.generate_key(OpenSSL.crypto.TYPE_RSA, 1024)

    # create a self-signed cert
    cert = OpenSSL.crypto.X509()
    cert.set_subject(params.certSubject)
    cert.set_serial_number(params.certSerial)
    cert.set_notBefore(params.certStart)
    cert.set_notAfter(params.certEnd)
    cert.set_issuer(params.certSubject)
    cert.add_extensions(params.certExtensions)

    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    open(certFile, 'wb').write(
        OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))
    open(keyFile, 'wb').write(
        OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, k))
    open(pemFile, 'wb').write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            + b"\n" + OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, k))

    print("[+] Wrote the files to {}, {}, and {}".format(certFile, keyFile, pemFile))

def main():
    targetCert = get_cert(targetDomain, targetPort)
    params = parse_cert(targetCert)
    make_cert(params)


if __name__ == "__main__":
    main()
