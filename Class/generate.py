from Class.templator import Templator
from Class.cli import CLI
from Class.cert import Cert
import requests, subprocess, json, time, os

class Generate:

    nginxPath = "/etc/nginx/sites-enabled/"
    nginxCerts = "/opt/woodCDN/certs/"
    reload = False

    def __init__(self):
        self.cli = CLI()
        self.cert = Cert()
        self.templator = Templator()

    def run(self):
        self.certs()
        self.nginx()

    def certs(self):
        print("Updating certs")

        data = self.cli.query(['SELECT * FROM certs'])
        files,current = os.listdir(self.nginxCerts),[]

        if 'values' in data['results'][0]:
            for entry in data['results'][0]['values']:
                if entry[2] == "@": domain = entry[1]
                if entry[2] != "@": domain = entry[2]+"."+entry[1]
                current.append(domain+"-fullchain.pem")
                current.append(domain+"-privkey.pem")

                if domain+"-fullchain.pem" not in files or row[5] > os.path.getmtime(self.nginxCerts+domain+"-fullchain.pem"):
                    print("Writing",domain+"-fullchain.pem")
                    with open(self.nginxCerts+domain+"-fullchain.pem", 'a') as out:
                        out.write(entry[3])
                    self.reload = True
                else:
                    print(domain+"-fullchain.pem","skipping")

                if domain+"-privkey.pem" not in files or row[5] > os.path.getmtime(self.nginxCerts+domain+"-privkey.pem"):
                    print("Writing",domain+"-privkey.pem")
                    with open(self.nginxCerts+domain+"-privkey.pem", 'a') as out:
                        out.write(entry[4])
                    self.reload = True
                else:
                    print(domain+"-privkey.pem","skipping")

        self.cert.syncCerts(current,files,self.nginxCerts)

    def nginx(self):
        print("Updating nginx")

        data = self.cli.query(['SELECT * FROM vhosts WHERE type = "proxy"'])
        files,current = os.listdir(self.nginxPath),[]

        if 'values' in data['results'][0]:
            for entry in data['results'][0]['values']:
                if entry[2] == "@": domain = entry[1]
                if entry[2] != "@": domain = entry[2]+"."+entry[1]
                current.append("cdn-"+domain)
                if "cdn-"+domain not in files:
                    print("Writing HTTP config for",domain)
                    http = self.templator.nginxHTTP(domain,entry[4]) + "\n"
                    with open(self.nginxPath+"cdn-"+domain, 'a') as out:
                        out.write(http)
                    self.reload = True
                else:
                    with open(self.nginxPath+"cdn-"+domain, 'r') as f:
                        file = f.read()
                    if "443" not in file and os.path.isfile(self.nginxCerts+domain+"-fullchain.pem") and os.path.isfile(self.nginxCerts+domain+"-privkey.pem"):
                        print("Writing HTTPS config for",domain)
                        file = file + self.templator.nginxHTTPS(domain,entry[4]) + "\n"
                        with open(self.nginxPath+"cdn-"+domain, 'w') as out:
                            out.write(file)
                        self.reload = True
                    elif "443" not in file:
                        print("Cert missing for",domain,"skipping")
                    else:
                        print("cdn-"+domain,"skipping")

        #vhosts removed from database
        for file in files:
            if file not in current and "cdn-" in file:
                os.remove(path+file)
                self.reload = True

        if self.reload:
            #Gracefull reloading, won't impact incomming or ongoing connections
            print("Reloading nginx")
            subprocess.run(["/usr/bin/sudo", "/usr/sbin/service", "nginx", "reload"])
