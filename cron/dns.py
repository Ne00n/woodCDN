#!/usr/bin/python3
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from Class.dns import DNS

if len(sys.argv) == 1:
    print("dns")
elif sys.argv[1] == "dns":
    if len(sys.argv) > 2:
        dns = DNS(sys.argv[2])
    else:
        dns = DNS()
    response = dns.fetch()
    if response is False: sys.exit()
    dns.generate()
elif sys.argv[1] == "run":
    if len(sys.argv) > 2:
        dns = DNS(sys.argv[2])
    else:
        dns = DNS()
    dns.run()
