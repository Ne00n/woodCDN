from Class.rqlite import rqlite
import json, os

class Cert(rqlite):

    def addCert(self,data):
        print("adding",data[0])
        response = self.execute(['INSERT INTO certs(domain,subdomain,fullchain,privkey,updated) VALUES(?, ?, ?, ?, ?)',data[0],data[1],data[2],data[3],data[4]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def syncVHosts(self,current,files,reload,path):
        #vhosts removed from database
        for file in files:
            if file not in current and "cdn-" in file:
                os.remove(path+file)
                reload = True
        return reload

    def syncCerts(self,current,files,path):
        #certs removed from database
        for file in files:
            if file not in current:
                os.remove(path+file)
