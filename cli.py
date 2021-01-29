#!/usr/bin/python3
from Class.cli import CLI
import sys

cli = CLI()

if len(sys.argv) == 1:
    print("init, add, list, delete")
elif sys.argv[1] == "init":
    cli.init()
elif sys.argv[1] == "add":
    cli.add(sys.argv[2],sys.argv[3])
elif sys.argv[1] == "list":
    cli.list()
elif sys.argv[1] == "delete":
    cli.delete(sys.argv[2])
