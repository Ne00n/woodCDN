import requests, json

class CLI:

    ip,port = "127.0.0.1",4001

    def __init__(self):
        print("woodCDN")

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
        self.curl(["CREATE TABLE vhosts (domain TEXT NOT NULL PRIMARY KEY, backend TEXT NOT NULL)"])

    def add(self,domain,target):
        print("adding",domain)
        response = self.execute(['INSERT INTO vhosts(domain,backend) VALUES(?, ?)',domain,target])
        print(json.dumps(response, indent=4, sort_keys=True))

    def list(self):
        response = self.query(["SELECT * FROM vhosts"])
        print(json.dumps(response, indent=4, sort_keys=True))

    def delete(self,domain):
        response = self.execute(['DELETE FROM vhosts WHERE domain=?',domain])
        print(json.dumps(response, indent=4, sort_keys=True))
