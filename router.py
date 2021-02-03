#!/usr/bin/python3 -u
from sys import stdin, stderr
from Class.cli import CLI
from Class.data import Data
import geoip2.database

reader = geoip2.database.Reader("/opt/woodCDN/GeoLite2-City.mmdb")

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
    stderr.write("pops table empty or missing\n")
    print("FAIL")

line = stdin.readline()
if "HELO\t3" not in line:
    stderr.write("Received unexpected line, wrong ABI version?\n")
    print("FAIL")

print("OK\twoodCDN Router")
stderr.write("wood is loaded\n")

while True:
    line = stdin.readline().rstrip()

    if (len(line.split("\t")) < 8):
        stderr.write("PowerDNS sent unparseable line\n")
        print("FAIL")
        continue

    type, qname, qclass, qtype, id, ip, localip, ednsip = line.split("\t")
    bits,auth = "21","1"

    for domain in domains:
        if domain in qname:

            if(qtype == "SOA" or qtype == "ANY"):
                print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tSOA\t3600\t-1\tns1."+domain+" noc."+domain+" 2008080300 1800 3600 604800 3600")

            if(qtype == "NS" or qtype == "ANY"):
                print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tNS\t3600\t-1\tns1."+domain)
                print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tNS\t3600\t-1\tns2."+domain)

            if(qtype == "A" or qtype == "ANY"):
                if qname.startswith("ns1"):
                    print("DATA\t"+bits+"\t"+auth+"\tns1."+domain+"\t"+qclass+"\tA\t3600\t-1\t"+nameservers[domain][0])
                elif qname.startswith("ns2"):
                    print("DATA\t"+bits+"\t"+auth+"\tns2."+domain+"\t"+qclass+"\tA\t3600\t-1\t"+nameservers[domain][1])
                else:
                    try:
                        response = reader.city(ip)
                        ip = Data.getClosestPoP(response.location.latitude,response.location.longitude,pops)
                    except Exception as e:
                        stderr.write("Error "+str(e)+"\n")
                        stderr.write("Could not resolve "+ip+"\n")
                        ip = pops[0][3]
                        print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tA\t1\t-1\t"+ip)

    print("END");
