from Class.data import Data
from Class.cli import CLI
import json, time, os

class DNS:

    path = "/home/cdn/geodns/dns/"

    def __init__(self,path=""):
        self.cli = CLI()
        self.data = Data()
        self.vhosts = {}
        self.domains = {}

        if path != "": self.path = path

        print("Loading countries")
        with open('../config/countries.json') as f:
            self.countries = json.load(f)

    def run(self):
        while True:
            response = self.fetch()
            if response is not False: self.generate()
            time.sleep(30)

    def fetch(self):
        self.fallback = False
        data = self.cli.query(["SELECT * FROM domains",'SELECT * FROM vhosts WHERE type != "proxy"',"SELECT * FROM pops"])

        if (data is False or "values" not in data['results'][0] or "values" not in data['results'][1] or "values" not in data['results'][2]):
            print("domains/vhosts/pops table missing or empty")
            return False

        self.pops = [x for x in data['results'][2]['values'] if x[5] + 60 > int(time.time())]
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
        config = {"ttl": 30,"targeting": "country @ region ip asn","wildcard":True,"data":{"":{}}}
        current = []

        for domain, nameservers in self.domains.items():
            current.append(domain+".json")

            #nameservers NS + A
            count = 1
            config["data"][""]["ns"] = []
            for nameserver in nameservers:
                ns = "ns"+str(count)+"."+domain
                config["data"][""]["ns"].append(ns)
                config["data"]["ns"+str(count)] = {}
                config["data"]["ns"+str(count)]["a"] = []
                config["data"]["ns"+str(count)]["a"].append([nameserver])
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
                                if record != domain: config["data"][record][type].append([value])
                                if record == domain: config["data"][""][type].append([value])
                            elif type == "mx" or type == "txt" or type == "spf":
                                if record != domain: config["data"][record][type].append({type:value[0]})
                                if record == domain: config["data"][""][type].append({type:value[0]})

            #geo
            for country in self.countries:
                ip = ""
                for pop in self.pops:
                    if pop[1] == country['alpha2'].lower():
                        ip = pop[4]
                        continue
                if ip == "":
                    ip = self.data.getClosestPoP(float(country['latitude']), float(country['longitude']), self.pops, self.fallback)
                if ip == "":
                    print("Could not geo",country['country'])
                    continue
                config["data"][country['alpha2'].lower()] = {}
                config["data"][country['alpha2'].lower()]["a"] = []
                config["data"][country['alpha2'].lower()]["a"].append([ip])

            #write config
            with open(self.path+domain+".json", 'w') as file:
                json.dump(config, file,indent=2)
            #print(json.dumps(config,indent=2))

        #sync files
        files = os.listdir(self.path)
        for file in files:
            if file not in current and "example" not in file and file.endswith("json") is True:
                os.remove(self.path+file)
