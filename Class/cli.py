import requests, json

class CLI:

    ip,port = "rqlite",4003

    def curl(self,url,query):
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        query = json.dumps(query)
        r = requests.post(url, data=query, headers=headers)
        if (r.status_code == 200):
            return r.json()
        else:
            return False

    def query(self,query,level="none"):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/query?pretty&timings&level='+level
        return self.curl(url,query)

    def execute(self,query,level="none"):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/execute?pretty&timings&level='+level
        query = [query]
        return self.curl(url,query)

    def init(self):
        self.execute(["CREATE TABLE pops (name TEXT NOT NULL PRIMARY KEY, latitude DECIMAL(10,7) NOT NULL, longitude DECIMAL(10,7) NOT NULL,v4 TEXT NOT NULL)"])
        self.execute(["CREATE TABLE domains (domain TEXT NOT NULL PRIMARY KEY, nsv4 TEXT NOT NULL)"])
        self.execute(["CREATE TABLE vhosts (domain TEXT NOT NULL PRIMARY KEY, subdomain TEXT NOT NULL, backend TEXT NOT NULL, FOREIGN KEY(domain) REFERENCES domains(domain))"])
        self.execute(["PRAGMA foreign_keys = ON"])

    def addDomain(self,domain,nsv4):
        print("adding",domain)
        response = self.execute(['INSERT INTO domains(domain,nsv4) VALUES(?, ?)',domain,nsv4])
        print(json.dumps(response, indent=4, sort_keys=True))

    def addVHost(self,domain,subdomain,target):
        print("adding",domain)
        response = self.execute(['INSERT INTO vhosts(domain,subdomain,backend) VALUES(?, ?, ?)',domain,subdomain,target])
        print(json.dumps(response, indent=4, sort_keys=True))

    def addPoP(self,name,v4,latitude,longitude):
        print("adding",name)
        response = self.execute(['INSERT INTO pops(name,v4,latitude,longitude) VALUES(?, ?, ?, ?)',name,v4,latitude,longitude])
        print(json.dumps(response, indent=4, sort_keys=True))

    def getTable(self,table="domains"):
        response = self.query(["SELECT * FROM "+table])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteDomain(self,domain):
        response = self.execute(['DELETE FROM domains WHERE domain=?',domain])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteVhost(self,subdomain):
        response = self.execute(['DELETE FROM vhosts WHERE subdomain=?',domain])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deletePoP(self,name):
        response = self.execute(['DELETE FROM pops WHERE name=?',name])
        print(json.dumps(response, indent=4, sort_keys=True))
