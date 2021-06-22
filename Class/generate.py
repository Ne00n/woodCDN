from Class.templator import Templator
from Class.cli import CLI
from Class.cert import Cert
import requests, subprocess, json, time, os

class Generate:

    nginxPath = "/etc/nginx/sites-enabled/"
    nginxCerts = "/opt/woodCDN/certs/"
    gdnsdConfig = "/etc/gdnsd/config"
    reload = False
    pops = {}

    def __init__(self):
        self.cli = CLI()
        self.cert = Cert()
        self.templator = Templator()

    def run(self):
        while True:
            self.certs()
            self.nginx()
            self.gdnsd()
            time.sleep(60)

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

                if domain+"-fullchain.pem" not in files or entry[5] > os.path.getmtime(self.nginxCerts+domain+"-fullchain.pem"):
                    print("Writing",domain+"-fullchain.pem")
                    with open(self.nginxCerts+domain+"-fullchain.pem", 'w') as out:
                        out.write(entry[3])
                    self.reload = True
                else:
                    print(domain+"-fullchain.pem","skipping")

                if domain+"-privkey.pem" not in files or entry[5] > os.path.getmtime(self.nginxCerts+domain+"-privkey.pem"):
                    print("Writing",domain+"-privkey.pem")
                    with open(self.nginxCerts+domain+"-privkey.pem", 'w') as out:
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

                #If the vhost does not exists or the database timestamp is newer than the file timestamp
                if "cdn-"+domain not in files or entry[5] > os.path.getmtime(self.nginxPath+"cdn-"+domain):

                    print("Writing HTTP config for",domain)
                    http = self.templator.nginxHTTP(domain,entry[4])
                    vhost = self.templator.nginxWrap(domain,http)

                    with open(self.nginxPath+"cdn-"+domain, 'w') as out:
                        out.write(vhost)
                    self.reload = True

                #If the vhost exist lets do some modifications
                if os.path.isfile(self.nginxPath+"cdn-"+domain):
                    with open(self.nginxPath+"cdn-"+domain, 'r') as f:
                        file = f.read()

                    if "443" not in file and os.path.isfile(self.nginxCerts+domain+"-fullchain.pem") and os.path.isfile(self.nginxCerts+domain+"-privkey.pem"):
                        print("Writing HTTPS config for",domain)
                        http = self.templator.nginxHTTP(domain,entry[4])
                        https = self.templator.nginxHTTPS(domain,entry[4])
                        vhost = self.templator.nginxWrap(domain,http+https)

                        with open(self.nginxPath+"cdn-"+domain, 'w') as out:
                            out.write(vhost)
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

    def gdnsd(self):
        print("Updating gdnsd")

        data = self.cli.query(['SELECT * FROM pops'])
        if not 'values' in data['results'][0]: return False

        pops = [x for x in data['results'][0]['values'] if x[2] + 60 > int(time.time())]
        if len(pops) == 0: pops = data['results'][0]['values'] #fallback

        reload = False
        if self.pops != data['results'][0]: reload = True

        config = self.templator.gdnsdConfig(data['results'][0]['values'])

        if reload:
            with open(self.gdnsdConfig, 'w') as out:
                out.write(config)
            print("Restarting gdnsd")
            subprocess.run(["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "gdnsd"])

        self.pops = data['results'][0]
