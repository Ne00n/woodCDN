#!/usr/bin/python3 -u
from sys import stdin, stderr, stdout
from Class.cli import CLI
import geoip2.database

reader = geoip2.database.Reader('/opt/woodCDN/GeoLite2-Country.mmdb')

cli = CLI()

domainsRaw = cli.query(["SELECT * FROM domains"])
nameservers,domains = {},[]

for result in domainsRaw['results']:
    if 'values' in result:
        for row in result['values']:
            nameservers[row[0]] = row[1].split(",")
            domains.append(row[0])

line = stdin.readline()
if "HELO\t3" not in line:
    print("FAIL\n")

print("OK\twoodCDN Router\n")
stderr.write("wood is loaded\n")

while True:
    line = stdin.readline().rstrip()

    if (len(line.split("\t")) < 8):
        print("FAIL\n")
        continue

    type, qname, qclass, qtype, id, ip, localip, ednsip = line.split("\t")

    if any(ext in qname for ext in domains):
        stderr.write(qname+"\n")
        stderr.write("match\n")

        if(qtype == "SOA" or qtype == "ANY"):
            stderr.write("SOA\n")
            print("DATA	$qname	$qclass	SOA	3600	-1	ns1.example.com ahu.example.com 2008080300 1800 3600 604800 3600\n")

        if(qtype == "NS" or qtype == "ANY"):
            stderr.write("NS\n")
            print("DATA	$qname	$qclass	NS	3600	-1	ns1.example.com\n")
            print("DATA	$qname	$qclass	NS	3600	-1	ns2.example.com\n")

        if(qtype == "A" or qtype == "ANY"):
            stderr.write("A\n")
            print("DATA	$qname	$qclass	A	3600	-1	1.2.3.4\n")
            print("DATA	$qname	$qclass	A	3600	-1	1.2.3.5\n")
            print("DATA	$qname	$qclass	A	3600	-1	1.2.3.6\n")
    else:
        stdout.write("FAIL\n")
        stderr.write("no match\n")

    stdout.write('END\n');
