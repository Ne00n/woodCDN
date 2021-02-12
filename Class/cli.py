from Class.rqlite import rqlite
import json, time

class CLI(rqlite):

    def addDomain(self,data):
        print("adding",data[0])
        response = self.execute(['INSERT INTO domains(domain,email,nsv4) VALUES(?, ?, ?)',data[0],data[1],data[2]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def addVHost(self,data):
        print("adding",data[0])
        response = self.execute(['INSERT INTO vhosts(domain,subdomain,type,value,updated) VALUES(?, ?, ?, ?, ?)',data[0],data[1],data[2],data[3],int(time.time())])
        print(json.dumps(response, indent=4, sort_keys=True))
        return response

    def addPoP(self,data):
        print("adding",data[0])
        response = self.execute(['INSERT INTO pops(name,v4,latitude,longitude) VALUES(?, ?, ?, ?)',data[0],data[1],data[2],data[3]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def getTable(self,table="domains"):
        response = self.query(["SELECT * FROM "+table])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteDomain(self,data):
        response = self.execute(['DELETE FROM domains WHERE domain=?',data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteVhost(self,data):
        response = self.execute(['DELETE FROM vhosts WHERE domain=? and subdomain=? AND type =?',data[0],data[1],data[2]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deletePoP(self,data):
        response = self.execute(['DELETE FROM pops WHERE name=?',data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))
