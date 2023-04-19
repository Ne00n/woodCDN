#!/usr/bin/python3
import socket, sys
sys.path.append("..") # Adds higher directory to python modules path.
from Class.generate import Generate

hostname = socket.gethostname()
if "." in hostname:
    pop = hostname.split(".", 1)[0]
else:
    pop = hostname

generate = Generate(pop)

if len(sys.argv) == 1:
    print("nginx, certs, config, zones, gdnsd, run")
elif sys.argv[1] == "nginx":
    generate.nginx()
elif sys.argv[1] == "certs":
    generate.certs()
elif sys.argv[1] == "config":
    generate.gdnsdConfig()
elif sys.argv[1] == "zones":
    generate.gdnsdZones()
elif sys.argv[1] == "gdnsd":
    generate.gdnsd()
elif sys.argv[1] == "run":
    generate.run()
