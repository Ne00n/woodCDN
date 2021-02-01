import requests, json

class CLI:

    ip,port = "127.0.0.1",4001

    def curl(self,url,query):
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        query = json.dumps(query)
        r = requests.post(url, data=query, headers=headers)
        if (r.status_code == 200):
            return r.json()
        else:
            return False

    def query(self,query):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/query?pretty&timings'
        return self.curl(url,query)

    def execute(self,query):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/execute?pretty&timings'
        query = [query]
        return self.curl(url,query)

    def init(self):
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

    def listDomain(self):
        response = self.query(["SELECT * FROM domains"])
        print(json.dumps(response, indent=4, sort_keys=True))

    def listVHost(self):
        response = self.query(["SELECT * FROM vhosts"])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteDomain(self,domain):
        response = self.execute(['DELETE FROM domains WHERE domain=?',domain])
        print(json.dumps(response, indent=4, sort_keys=True))

    def deleteVhost(self,subdomain):
        response = self.execute(['DELETE FROM vhosts WHERE subdomain=?',domain])
        print(json.dumps(response, indent=4, sort_keys=True))
