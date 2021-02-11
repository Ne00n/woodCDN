#!/usr/bin/python3
import simple_acme_dns, time, sys
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
        if row[8] == None:
            print("Missing cert for",target)

            directory = "https://acme-staging-v02.api.letsencrypt.org/directory"
            client = simple_acme_dns.ACMEClient(domains=[target],email=row[7],directory=directory,nameservers=["8.8.8.8", "1.1.1.1"],new_account=True,generate_csr=True)

            tokens = {} # record for cleanup
            for domain, token in client.request_verification_tokens():
                print("adding {domain} --> {token}".format(domain=domain, token=token))
                cli.addVHost([row[1],"_acme-challenge."+row[2],'TXT',token])
                tokens[domain] = token

            print("Waiting for dns propagation")
            try:
                if client.check_dns_propagation(timeout=1200):
                    client.request_certificate()
                    fullchain = client.certificate.decode()
                    privkey = client.private_key.decode()
                    cert.addCert([row[1],row[2],fullchain,privkey],time.time())
                else:
                    client.deactivate_account()
                    print("Failed to issue certificate for " + str(client.domains))
                    exit(1)
            except Exception as e:
                print(e)
            finally:
                cli.deleteVhost([row[1],"_acme-challenge."+row[2],'TXT'])

        else:
            print("Checking cert for",target)

else:
    print("Not leader, aborting.")
