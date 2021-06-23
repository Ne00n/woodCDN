#!/usr/bin/python3
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from Class.generate import Generate

generate = Generate()

if len(sys.argv) == 1:
    print("nginx certs")
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
