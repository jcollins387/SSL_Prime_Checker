#!/usr/bin/python3

import gmpy2
import optparse
import subprocess
import re
import configparser
import os
import sys

parser = optparse.OptionParser()

parser.add_option("-s", "--server", dest="servers", action="append", default=[], help="server hostnames or IP addresses")
parser.add_option("-f", "--file", dest="file", help="file containing a list of hosts")
parser.add_option("-p", "--port", dest="port", default=443, help="port (default 443/https)")
(opts, args) = parser.parse_args()

config = configparser.ConfigParser()
config.read(os.path.dirname(sys.argv[0]) + '/knownprimes.ini')

def check_prime(server):
    ossl_out = subprocess.check_output([os.path.dirname(sys.argv[0]) + "/openssl-trace",
                                        "s_client", "-trace",
                                        "-servername", server,
                                        "-cipher", "DHE",
                                        "-connect", f"{server}:{opts.port}"],
                                       stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for line in ossl_out.decode("utf-8").splitlines():
        if 'dh_p' in line:
            prime = gmpy2.mpz(re.sub(".*: ", "", line), 16)
            print(f"Checking prime p for {server}: {hex(prime)}")

            if gmpy2.is_prime(prime):
                print("\033[92mp is prime\033[39m")
            else:
                print("\033[91mp is not a prime, that is broken\033[39m")

            p12 = gmpy2.div(gmpy2.sub(prime, 1), 2)
            print("-" * 50)
            return

    print(f"Failed to obtain prime p for {server}")

if opts.servers:
    for server in opts.servers:
        check_prime(server)
elif opts.file:
    try:
        with open(opts.file, "r") as file:
            hostnames = file.readlines()
            hostnames = [h.strip() for h in hostnames]
    except FileNotFoundError:
        print(f"Error: File {opts.file} not found.")
        sys.exit(1)

    for hostname in hostnames:
        check_prime(hostname)
else:
    parser.print_help()
    sys.exit(1)
