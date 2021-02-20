#!/usr/bin/python3
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from Class.generate import Generate
from Class.dns import DNS

generate = Generate()
dns = DNS()

if len(sys.argv) == 1:
    print("nginx certs")
elif sys.argv[1] == "nginx":
    generate.nginx()
elif sys.argv[1] == "certs":
    generate.certs()
elif sys.argv[1] == "dns":
    response = dns.fetch()
    if response is False: sys.exit()
    dns.generate()
elif sys.argv[1] == "run":
    generate.run()
