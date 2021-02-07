import requests, json

class CLI:

    ip,port = "rqlite",4003

    def curl(self,url,query):
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        query = json.dumps(query)
        try:
            r = requests.post(url, data=query, headers=headers)
            if (r.status_code == 200):
                return r.json()
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def query(self,query,level="none",timings="&timings"):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/query?pretty'+timings+'&level='+level
        return self.curl(url,query)

    def execute(self,query):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/execute?pretty&timings'
        query = [query]
        return self.curl(url,query)

    def init(self):
        self.execute(["CREATE TABLE pops (name TEXT NOT NULL PRIMARY KEY, latitude DECIMAL(10,7) NOT NULL, longitude DECIMAL(10,7) NOT NULL,v4 TEXT NOT NULL)"])
        self.execute(["CREATE TABLE domains (domain TEXT NOT NULL PRIMARY KEY, nsv4 TEXT NOT NULL)"])
        self.execute(["CREATE TABLE vhosts (id INTEGER NOT NULL PRIMARY KEY, domain TEXT NOT NULL, subdomain TEXT NOT NULL, type TEXT not NULL, value TEXT NULL, FOREIGN KEY(domain) REFERENCES domains(domain))"])
        self.execute(["PRAGMA foreign_keys = ON"])

    def addDomain(self,data):
        print("adding",data[0])
        response = self.execute(['INSERT INTO domains(domain,nsv4) VALUES(?, ?)',data[0],data[1]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def addVHost(self,data):
        print("adding",data[0])
        response = self.execute(['INSERT INTO vhosts(domain,subdomain,type,value) VALUES(?, ?, ?, ?)',data[0],data[1],data[2],data[3]])
        print(json.dumps(response, indent=4, sort_keys=True))

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
        response = self.execute(['DELETE FROM vhosts WHERE subdomain=? and type=?',data[0],data[1]])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deletePoP(self,data):
        response = self.execute(['DELETE FROM pops WHERE name=?',data[0]])
        print(json.dumps(response, indent=4, sort_keys=True))
