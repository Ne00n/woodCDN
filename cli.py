#!/usr/bin/python3
from Class.cli import CLI
from Class.cert import Cert
import sys

cli = CLI()
cert = Cert()

if len(sys.argv) == 1:
    print("init, domain, vhost, pop, cert")
elif sys.argv[1] == "init":
    cli.init()
elif sys.argv[1] == "domain":
    if len(sys.argv) == 2:
        print("domain add <name> <email> <ns1>,<ns2>\ndomain list\ndomain del <name>")
    elif sys.argv[2] == "add":
        cli.addDomain(sys.argv[3:])
    elif sys.argv[2] == "list":
        cli.getTable("domains")
    elif sys.argv[2] == "del":
        cli.deleteDomain(sys.argv[3:])
elif sys.argv[1] == "vhost":
    if len(sys.argv) == 2:
        print("vhost add <domain> <subdomain> <type> <value>\nvhost list\nvhost del <domain> <subdomain> <type>")
    elif sys.argv[2] == "add":
        cli.addVHost(sys.argv[3:])
    elif sys.argv[2] == "list":
        cli.getTable("vhosts")
    elif sys.argv[2] == "del":
        cli.deleteVhost(sys.argv[3:])
elif sys.argv[1] == "pop":
    if len(sys.argv) == 2:
        print("pop add <name> <v4>\npop list\npop del <name>")
    elif sys.argv[2] == "add":
        cli.addPoP(sys.argv[3:])
    elif sys.argv[2] == "list":
        cli.getTable("pops")
    elif sys.argv[2] == "del":
        cli.deletePoP(sys.argv[3:])
elif sys.argv[1] == "cert":
    if len(sys.argv) == 2:
        print("cert del <domain> <subdomain>")
    elif sys.argv[2] == "del":
        cert.deleteCert(sys.argv[3:])
