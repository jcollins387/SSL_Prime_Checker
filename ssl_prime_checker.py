#!/usr/bin/python3

import gmpy2
import optparse
import subprocess
import re
import configparser
import os
import sys
import signal

parser = optparse.OptionParser()

parser.add_option("-s", "--server", dest="servers", action="append", default=[], help="server hostnames or IP addresses")
parser.add_option("-f", "--file", dest="file", help="file containing a list of hosts")
parser.add_option("-p", "--port", dest="port", default=443, help="port (default 443/https)")
parser.add_option("-t", "--timeout", dest="timeout", type="float", default=10.0, help="timeout in seconds")
(opts, args) = parser.parse_args()

config = configparser.ConfigParser()
config.read(os.path.dirname(sys.argv[0]) + '/knownprimes.ini')

def check_prime(server):
    try:
        ossl_out = subprocess.check_output(["./openssl-trace",
                                            "s_client", "-trace",
                                            "-servername", server,
                                            "-cipher", "DHE",
                                            "-connect", f"{server}:{opts.port}"],
                                           stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=opts.timeout)

        for line in ossl_out.decode("utf-8").splitlines():
            if 'dh_p' in line:
                prime = gmpy2.mpz(re.sub(".*: ", "", line), 16)
                print(f"Host: {server}")
                print(f"p: {hex(prime)}")

                if gmpy2.is_prime(prime):
                    prime_str = "yes"
                else:
                    prime_str = "no"

                common_str = "no"
                common_name = ""
                for section in config.sections():
                    known_prime = config.get(section, "prime")
                    if known_prime == hex(prime):
                        common_str = "yes"
                        common_name = section
                        break

                print(f"prime: {prime_str}")
                print(f"common: {common_str}")
                print(f"common name: {common_name}")

                print("-" * 50)
                return

        print(f"Failed to obtain prime p for {server}")
    except subprocess.TimeoutExpired:
        print(f"Timeout occurred for {server}. Skipping to the next host.")
        print("-" * 50)

def build_openssl_trace():
    openssl_trace_script = """
#include <stdio.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    if (execvp("openssl", argv) == -1)
    {
        perror("execvp");
        return 1;
    }

    return 0;
}
"""

    with open("openssl-trace.c", "w") as file:
        file.write(openssl_trace_script)

    if subprocess.call(["gcc", "-o", "openssl-trace", "openssl-trace.c"]) == 0:
        print("openssl-trace built successfully.")
        os.remove("openssl-trace.c")
    else:
        print("Failed to build openssl-trace.")
        sys.exit(1)

def prompt_build_openssl_trace():
    response = input("The openssl-trace script was not found. Do you want to build it? (y/n): ")
    if response.lower() == "y":
        build_openssl_trace()
    else:
        sys.exit(1)

def timeout_handler(signum, frame):
    print("Timeout occurred.")
    print("-" * 50)

if not os.path.isfile("./openssl-trace"):
    prompt_build_openssl_trace()

signal.signal(signal.SIGALRM, timeout_handler)

if opts.servers:
    for server in opts.servers:
        signal.alarm(int(opts.timeout))
        check_prime(server)
        signal.alarm(0)  # Reset the alarm after each host
elif opts.file:
    try:
        with open(opts.file, "r") as file:
            hostnames = file.readlines()
            hostnames = [h.strip() for h in hostnames]
    except FileNotFoundError:
        print(f"Error: File {opts.file} not found.")
        sys.exit(1)

    for hostname in hostnames:
        signal.alarm(int(opts.timeout))
        check_prime(hostname)
        signal.alarm(0)  # Reset the alarm after each host
else:
    parser.print_help()
    sys.exit(1)
