import requests, time, json

class rqlite:

    ip,port = "rqlite",4003

    def curl(self,url,query):
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        #retry 4 times
        for run in range(4):
            try:
                if not query:
                    r = requests.get(url,allow_redirects=False)
                else:
                    query = json.dumps(query)
                    r = requests.post(url, data=query, headers=headers,allow_redirects=False)
                if r.status_code == 301:
                    leader = r.headers['Location']
                    r = requests.post(leader, data=query, headers=headers,allow_redirects=False)
                if (r.status_code == 200):
                    return r.json()
            except Exception as e:
                print(e)
            time.sleep(2)
        return False

    def query(self,query,level="none",timings="&timings"):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/query?pretty'+timings+'&level='+level
        return self.curl(url,query)

    def execute(self,query):
        url = 'http://'+self.ip+':'+str(self.port)+'/db/execute?pretty&timings'
        query = [query]
        return self.curl(url,query)

    def status(self):
        url = 'http://'+self.ip+':'+str(self.port)+'/status?pretty'
        return self.curl(url,[])

    def nodes(self):
        url = 'http://'+self.ip+':'+str(self.port)+'/nodes?pretty'
        return self.curl(url)

    def init(self):
        self.execute(["CREATE TABLE pops (id TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL UNIQUE, latitude DECIMAL(10,7) NOT NULL, longitude DECIMAL(10,7) NOT NULL,v4 TEXT NOT NULL)"])
        self.execute(["CREATE TABLE domains (domain TEXT NOT NULL PRIMARY KEY, nsv4 TEXT NOT NULL, email TEXT NOT NULL)"])
        self.execute(["CREATE TABLE vhosts (id INTEGER NOT NULL PRIMARY KEY, domain TEXT NOT NULL, subdomain TEXT NOT NULL, type TEXT NOT NULL, value TEXT NOT NULL, updated INTEGER NOT NULL, FOREIGN KEY(domain) REFERENCES domains(domain) ON DELETE CASCADE)"])
        self.execute(["CREATE TABLE certs (id INTEGER NOT NULL PRIMARY KEY, domain TEXT NOT NULL, subdomain TEXT NULL, fullchain TEXT NOT NULL, privkey TEXT not NULL, updated INTEGER NOT NULL, FOREIGN KEY(domain) REFERENCES domains(domain) ON DELETE CASCADE)"])
        self.execute(["PRAGMA foreign_keys = ON"])
