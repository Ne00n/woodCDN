#!/usr/bin/python3
import simple_acme_dns, sys
sys.path.append("..") # Adds higher directory to python modules path.
from Class.cli import CLI

cli = CLI()

status = cli.status()
if status is False: print("rqlite gone")
state = status['store']['raft']['state']

if state == "Leader":
    print("Getting doamins")
    domains = cli.query(['SELECT * FROM vhosts as v JOIN domains as d ON v.domain=d.domain LEFT JOIN certs as c ON v.domain=c.domain AND v.subdomain=c.subdomain WHERE v.type = "proxy"'])
    print(domains)
    if domains is False: print("rqlite gone")
    for row in domains['results'][0]['values']:
        print(row)
        target = row[1]
        if row[2] is not "@": target = row[2]+"."+row[1]
        if row[8] == None:
            print("Missing cert for",target)

            directory = "https://acme-staging-v02.api.letsencrypt.org/directory"
            client = simple_acme_dns.ACMEClient(domains=[target],email=row[7],directory=directory,nameservers=["8.8.8.8", "1.1.1.1"],new_account=True,generate_csr=True)

            tokens = {} # record for cleanup
            for domain, token in client.request_verification_tokens():
                print("{domain} --> {token}".format(domain=domain, token=token))
                tokens[domain] = token
                cli.addVHost([row[1],"_acme-challenge."+row[2],'TXT',token])

            if client.check_dns_propagation(timeout=1200):
                client.request_certificate()
                print(client.certificate.decode())
                print(client.private_key.decode())

            else:
                client.deactivate_account()
                print("Failed to issue certificate for " + str(client.domains))
                exit(1)

            for entry in tokens:
                cli.deleteVhost([row[1],"_acme-challenge."+row[2],'TXT'])

        else:
            print("Checking cert for",target)

else:
    print("Not leader, aborting.")
