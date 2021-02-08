#!/usr/bin/python3
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from Class.generate import Generate

generate = Generate()

if len(sys.argv) == 1:
    print("nginx")
elif sys.argv[1] == "nginx":
    generate.nginx()
