from Class.templator import Templator
from Class.cli import CLI
import requests, subprocess, json, os

class Generate:

    nginxPath = "/etc/nginx/sites-enabled/"
    nginxCerts = "/opt/woodCDN/certs/"
    reload = False

    def __init__(self):
        self.cli = CLI()
        self.templator = Templator()

    def certs(self):
        print("Updating certs")

        data = self.cli.query(['SELECT * FROM certs'])
        if 'values' not in data['results'][0]: return False

        files,current = os.listdir(self.nginxCerts),[]

        for entry in data['results'][0]['values']:
            if entry[2] == "@": domain = entry[1]
            if entry[2] != "@": domain = entry[2]+"."+entry[1]
            current.append("cdn-"+domain)
            if "cdn-"+domain not in files:
                with open(self.nginxCerts+domain+"-fullchain.pem", 'a') as out:
                    out.write(entry[3])
                with open(self.nginxCerts+domain+"-privkey.pem", 'a') as out:
                    out.write(entry[4])
                self.reload = True
            else:
                print(domain,"skipping")

        #certs removed from database
        for file in files:
            if file not in current:
                os.remove(self.nginxCerts+file)
                self.reload = True

    def nginx(self):
        print("Updating nginx")

        data = self.cli.query(['SELECT * FROM vhosts WHERE type = "proxy"'])
        if 'values' not in data['results'][0]: return False

        files,current = os.listdir(self.nginxPath),[]

        for entry in data['results'][0]['values']:
            if entry[2] == "@": domain = entry[1]
            if entry[2] != "@": domain = entry[2]+"."+entry[1]
            current.append("cdn-"+domain)
            if "cdn-"+domain not in files:
                http = self.templator.nginxHTTP(domain,entry[4])
                with open(self.nginxPath+"cdn-"+domain, 'a') as out:
                    out.write(http)
                self.reload = True
            else:
                print("cdn-"+domain,"skipping")

        #vhosts removed from database
        for file in files:
            if file not in current and "cdn-" in file:
                os.remove(self.nginxPath+file)
                self.reload = True

        if self.reload:
            #Gracefull reloading, won't impact incomming or ongoing connections
            subprocess.run(["/usr/sbin/service", "nginx","reload"])
