#!/usr/bin/python3
from sys import stdin
from Class.cli import CLI
import geoip2.database

reader = geoip2.database.Reader('/opt/woodCDN/GeoLite2-Country.mmdb')

cli = CLI()

domains = cli.query(["SELECT * FROM domains"])
vhosts = cli.query(["SELECT * FROM vhosts"])

domainList = {}

for result in domains['results']:
    if 'values' in result:
        for row in result['values']:
            domainList[row[0]] = row[1].split(",")

line = stdin.readline()
if line is not "HELO\t3":
    print("FAIL\n",flush=True)

print("OK\twoodCDN\n",flush=True)

while True:
    line = stdin.readline()

    if (len(line.split("#")) < 8):
        print("FAIL\n",flush=True)
        continue

    type, qname, qclass, qtype, id, ip = data.split("\t")

    if any(qname in item for entry in domainList):
        print(qname)

    if((qtype == "SOA" or qtype == "ANY") and qname == "example.com"):
        print("DATA	$qname	$qclass	SOA	3600	-1	ns1.example.com ahu.example.com 2008080300 1800 3600 604800 3600\n")

    if((qtype == "NS" or qtype == "ANY") and qname == "example.com"):
        print("DATA	$qname	$qclass	NS	3600	-1	ns1.example.com\n")
        print("DATA	$qname	$qclass	NS	3600	-1	ns2.example.com\n")

    if((qtype == "A" or qtype == "ANY") and qname == "webserver.example.com"):
        print("DATA	$qname	$qclass	A	3600	-1	1.2.3.4\n")
        print("DATA	$qname	$qclass	A	3600	-1	1.2.3.5\n")
        print("DATA	$qname	$qclass	A	3600	-1	1.2.3.6\n")

    print('END\n',flush=True);
