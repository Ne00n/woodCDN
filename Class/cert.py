from Class.rqlite import rqlite
import json

class Cert(rqlite):

    def addCert(self,data):
        print("adding",data[0])
        response = self.execute(['INSERT INTO certs(domain,subdomain,fullchain,privkey,updated) VALUES(?, ?, ?, ?, ?)',data[0],data[1],data[2],data[3],data[4]])
        print(json.dumps(response, indent=4, sort_keys=True))
