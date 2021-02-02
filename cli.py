#!/usr/bin/python3
from Class.cli import CLI
import sys

cli = CLI()

if len(sys.argv) == 1:
    print("init, add, list, delete")
elif sys.argv[1] == "init":
    cli.init()
elif sys.argv[1] == "addDomain":
    cli.addDomain(sys.argv[2],sys.argv[3])
elif sys.argv[1] == "addVHost":
    cli.addVHost(sys.argv[2],sys.argv[3],sys.argv[4])
elif sys.argv[1] == "addPoP":
    cli.addPoP(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
elif sys.argv[1] == "listDomain":
    cli.getTable("domains")
elif sys.argv[1] == "listVHost":
    cli.getTable("vhosts")
elif sys.argv[1] == "listPoP":
    cli.getTable("pops")
elif sys.argv[1] == "deleteVhost":
    cli.deleteVhost(sys.argv[2])
elif sys.argv[1] == "deleteDomain":
    cli.deleteDomain(sys.argv[2])
elif sys.argv[1] == "deletePoP":
    cli.deletePoP(sys.argv[2])
