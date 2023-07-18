# SSL Prime Checker

SSL Prime Checker is a command-line tool that checks the prime number used in SSL/TLS connections. It retrieves the prime value from the Diffie-Hellman or elliptic curve Diffie-Hellman parameters and performs various checks on the prime, such as primality testing.

## Features

- Checks the prime number used in SSL/TLS connections for security analysis.
- Supports checking prime numbers for individual servers or a list of servers.
- Retrieves the prime number from Diffie-Hellman or elliptic curve Diffie-Hellman parameters.
- Performs primality testing and analysis on the retrieved prime number.
- Supports a custom known primes file for comparison and analysis.

## Requirements

- Python 3
- gmpy2 library (install using `pip install gmpy2`)
- OpenSSL compiled with the enable-ssl-trace option
  - This will be compiled during the first run if not present in the working folder and named `openssl-trace`

## Usage

`python ssl_prime_checker.py [options]`


### Options

- `-s`, `--server`: Specify server hostnames or IP addresses to check the prime number.
- `-f`, `--file`: Specify a file containing a list of hosts (one per line) to check the prime number for multiple servers.
- `-p`, `--port`: Specify the port number to connect to (default is 443).

## Known Primes

The list of known prime numbers used for comparison and analysis is sourced from the [primecheck](https://github.com/hannob/primecheck) project by Hanno Böck. The `knownprimes.ini` file included in this repository is based on the `knownprimes.txt` file from the primecheck project.

## Example Usage

- Check the prime number for a single server:

`python ssl_prime_checker.py -s example.com`

- Check the prime number for multiple servers using a file:

`python ssl_prime_checker.py -f hosts.txt`

- Specify a custom port:

`python ssl_prime_checker.py -s example.com -p8443`
