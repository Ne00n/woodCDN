#!/usr/bin/python3 -u
from math import sin, cos, sqrt, atan2, radians
from sys import stdin, stderr
from Class.cli import CLI
from Class.data import Data
import geoip2.database

reader = geoip2.database.Reader("/opt/woodCDN/GeoLite2-Country.mmdb")

cli = CLI()
data = Data()

domainsRaw,pops = cli.query(["SELECT * FROM domains"]),cli.query(["SELECT * FROM pops"])
nameservers,domains = {},[]

for result in domainsRaw["results"]:
    if "values" in result:
        for row in result["values"]:
            nameservers[row[0]] = row[1].split(",")
            domains.append(row[0])

if "values" in pops['results'][0]:
    pops = pops['results'][0]['values']
else:
    stderr.write("Database down or pops table empty\n")
    print("FAIL")

line = stdin.readline()
if "HELO\t3" not in line:
    stderr.write("Received unexpected line, wrong ABI version?\n")
    print("FAIL")

print("OK\twoodCDN Router")
stderr.write("wood is loaded\n")

while True:
    line = stdin.readline().rstrip()

    stderr.write(line)
    if (len(line.split("\t")) < 8):
        stderr.write("PowerDNS sent unparseable line\n")
        print("FAIL")
        continue

    type, qname, qclass, qtype, id, ip, localip, ednsip = line.split("\t")
    bits,auth = "21","1"

    if any(ext in qname for ext in domains):

        if(qtype == "SOA" or qtype == "ANY"):
            print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tSOA\t3600\t-1\tahu.example.com ns1.example.com 2008080300 1800 3600 604800 3600")

        if(qtype == "NS" or qtype == "ANY"):
            print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tNS\t3600\t-1\tns1.example.com")
            print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tNS\t3600\t-1\tns2.example.com")

        if(qtype == "A" or qtype == "ANY"):
            try:
                response = reader.country(ip)
                ip = Data.getClosestPoP(response.location.latitude,response.location.longitude,pops)
            except:
                ip = pops[0][3]
                stderr.write("Could not resolve"+ip+"\n")
            print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tA\t3600\t-1\t"+ip)
            print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tA\t3600\t-1\t"+ip)

    print("END");
