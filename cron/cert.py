#!/usr/bin/python3
import time, sys
sys.path.append("..") # Adds higher directory to python modules path.
from Class.cli import CLI
from Class.cert import Cert

cli = CLI()
cert = Cert()

status = cli.status()
if status is False: print("rqlite gone")
state = status['store']['raft']['state']

if state == "Leader":
    print("Getting doamins")
    domains = cli.query(['SELECT * FROM vhosts as v JOIN domains as d ON v.domain=d.domain LEFT JOIN certs as c ON v.domain=c.domain AND v.subdomain=c.subdomain WHERE v.type = "proxy"'])

    if domains is False:
        print("rqlite gone")
        sys.exit()
    if 'values' not in domains['results'][0]:
        print("no vhosts added")
        sys.exit()

    for row in domains['results'][0]['values']:
        target = row[1]
        if row[2] is not "@": target = row[2]+"."+row[1]
        if row[9] == None:
            print("Missing cert for",target)

            response = cert.getCert(target,row[1],row[2],row[8])
            if response is False:
                print("Failed to get cert for",target)
                sys.exit()

        else:
            print("Checking cert for",target)
            if time.time() > (row[5] + (86400 * 30)):
                print("Certificate is older than 30 days")

                response = cert.getCert(target,row[1],row[2],row[8])
                if response is False:
                    print("Failed to get cert for",target)
                    sys.exit()

else:
    print("Not leader, aborting.")
