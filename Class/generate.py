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
                print("Writing",domain+"-fullchain.pem")
                with open(self.nginxCerts+domain+"-fullchain.pem", 'a') as out:
                    out.write(entry[3])
                print("Writing",domain+"-privkey.pem")
                with open(self.nginxCerts+domain+"-privkey.pem", 'a') as out:
                    out.write(entry[4])
            else:
                print(domain,"skipping")

        #certs removed from database
        for file in files:
            if file not in current:
                os.remove(self.nginxCerts+file)

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
                print("Writing HTTP config for",domain)
                http = self.templator.nginxHTTP(domain,entry[4])
                with open(self.nginxPath+"cdn-"+domain, 'a') as out:
                    out.write(http)
                self.reload = True
            else:
                with open(self.nginxPath+"cdn-"+domain, 'r') as f:
                    file = f.read()
                if "443" not in file and os.path.isfile(nginxCerts+domain+"-fullchain.pem") and os.path.isfile(nginxCerts+domain+"-privkey.pem"):
                    print("Writing HTTPS config for",domain)
                    file = file + "\n\n" + self.templator.nginxHTTPS(domain,entry[4])
                    with open(self.nginxCerts+"cdn-"+domain, 'a') as out:
                        out.write(file)
                    self.reload = True
                elif "443" not in file:
                    print("Cert missing for",domain,"skipping")
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
