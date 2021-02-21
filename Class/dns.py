from Class.cli import CLI
import json, time

class DNS:
    def __init__(self):
        self.cli = CLI()
        self.vhosts = {}
        self.domains = {}

    def fetch(self):
        self.fallback = False
        data = self.cli.query(["SELECT * FROM domains",'SELECT * FROM vhosts WHERE type != "proxy"',"SELECT * FROM pops"])

        if (data is False or "values" not in data['results'][0] or "values" not in data['results'][1] or "values" not in data['results'][2]):
            print("domains/vhosts/pops table missing or empty")
            return False

        self.pops = [x for x in data['results'][2]['values'] if x[4] + 60 > int(time.time())]
        if len(self.pops) == 0:
            self.pops = data['results'][2]['values'] #fallback
            self.fallback = True

        for row in data['results'][0]['values']:
            self.domains[row[0]] = row[1].split(",")

        for row in data['results'][1]['values']:
            if not row[1] in self.vhosts: self.vhosts[row[1]] = {}
            if not row[3] in self.vhosts[row[1]]: self.vhosts[row[1]][row[3]] = {}
            if row[2] == "@":
                if not row[1] in self.vhosts[row[1]][row[3]]: self.vhosts[row[1]][row[3]][row[1]] = []
                self.vhosts[row[1]][row[3]][row[1]].append(row[4:])
            else:
                subdomain = row[2]
                if not subdomain in self.vhosts[row[1]][row[3]]: self.vhosts[row[1]][row[3]][subdomain] = []
                self.vhosts[row[1]][row[3]][subdomain].append(row[4:])

    def generate(self):
        print("Generating configs")
        config = {"ttl": 30,"targeting": "country @ region ip asn","data":{"":{}}}

        for domain, nameservers in self.domains.items():

            #nameservers NS + A
            count = 1
            config["data"][""]["ns"] = []
            for nameserver in nameservers:
                ns = "ns"+str(count)+"."+domain
                config["data"][""]["ns"].append(ns)
                config["data"][ns] = {}
                config["data"][ns]["a"] = []
                config["data"][ns]["a"].append(nameserver)
                count = count + 1

            #static entries
            if domain in self.vhosts:
                for type, entries in self.vhosts[domain].items():
                    type = type.lower()
                    for record,values in entries.items():
                        if record != domain:
                            if record not in config["data"]: config["data"][record] = {}
                            if type not in config["data"][record]: config["data"][record][type] = []
                        else:
                            if type not in config["data"][""]: config["data"][""][type] = []
                        for value in values:
                            if type == "a" or type == "aaaa":
                                if record != domain: config["data"][record][type].append(value)
                                if record == domain: config["data"][""][type].append(value)
                            elif type == "mx" or type == "txt" or type == "spf":
                                if record != domain: config["data"][record][type].append({type:value})
                                if record == domain: config["data"][""][type].append({type:value})

            print(json.dumps(config,indent=2))
