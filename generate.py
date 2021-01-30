#!/usr/bin/python3
from Class.generate import Generate
import sys

generate = Generate()

if len(sys.argv) == 1:
    print("nginx")
elif sys.argv[1] == "nginx":
    generate.nginx()
