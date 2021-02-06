from Class.templator import Templator
from Class.cli import CLI
import requests, subprocess, json, os

class Generate:

    nginxPath = "/etc/nginx/sites-enabled/"

    def __init__(self):
        self.cli = CLI()
        self.templator = Templator()

    def nginx(self):
        print("Updating nginx")

        response = self.cli.query(["SELECT * FROM vhosts WHERE value is null"])
        if 'values' not in response['results'][0]: return False

        files,reload,current = os.listdir(self.nginxPath),False,[]

        for entry in response['results'][0]['values']:
            current.append("cdn-"+entry[0])
            if "cdn-"+entry[0] not in files:
                http = self.templator.nginxHTTP(entry[0],entry[1])
                with open(self.nginxPath+"cdn-"+entry[0], 'a') as out:
                    out.write(http)
                reload = True
            else:
                print("cdn-"+entry[0],"skipping")

        for file in files:
            #vhosts removed from database
            if file not in current and "cdn-" in file:
                os.remove(self.nginxPath+file)
                reload = True

        if reload:
            #Gracefull reloading, won't impact incomming or ongoing connections
            subprocess.run(["/usr/sbin/service", "nginx","reload"])
