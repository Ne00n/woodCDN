#!/usr/bin/python3 -u
from multiprocessing.pool import ThreadPool
from sys import stdin, stderr, exit
from Class.cli import CLI
from Class.data import Data
import geoip2.database, time

reader = geoip2.database.Reader("/opt/woodCDN/GeoLite2-City.mmdb")
pool = ThreadPool(processes=1)

cli = CLI()
data = Data()

nameservers,lastupdate,vhosts,pops = {},time.time(),{},{}

def updateData():
    data = cli.query(["SELECT * FROM domains","SELECT * FROM vhosts","SELECT * FROM pops"])

    if (data is False or "values" not in data['results'][0] or "values" not in data['results'][1] or "values" not in data['results'][2]):
        stderr.write("domains/vhosts/pops table missing or empty\n")
        return False

    for row in data['results'][0]['values']:
        nameservers[row[0]] = row[1].split(",")
    for row in data['results'][1]['values']:
        if row[4] == None: continue
        if row[3] == "@":
            if not row[1] in vhosts: vhosts[row[1]] = []
            vhosts[row[1]].append(row[2:])
        else:
            if not row[3]+"."+row[1] in vhosts: vhosts[row[3]+"."+row[1]] = []
            vhosts[row[3]+"."+row[1]].append(row[2:])
    return {'ns':nameservers,'vhosts':vhosts,'pops':data['results'][2]['values']}

def syncData(data):
    global nameservers, vhosts, pops
    if data is not False:
        nameservers,vhosts,pops = data['ns'],data['vhosts'],data['pops']
        stderr.write("Updated NS information\n")

response = updateData()
if response is False:
    time.sleep(1.5) #slow down pdns restarts
    exit()

nameservers,vhosts,pops = response['ns'],response['vhosts'],response['pops']

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

    for domain, nameserverList in nameservers.items(): #prevent fuckery if thread is updating
        if qname.endswith(domain):

            if(qtype == "SOA" or qtype == "ANY"):
                print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tSOA\t3600\t-1\tns1."+domain+" noc."+domain+" 2008080300 1800 3600 604800 3600")

            if(qtype == "NS" or qtype == "ANY"):
                print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tNS\t3600\t-1\tns1."+domain)
                print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tNS\t3600\t-1\tns2."+domain)

            if(qtype == "A" or qtype == "ANY"):
                if qname in vhosts:
                    for entry in vhosts[qname]:
                        print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\t"+entry[0]+"\t3600\t-1\t"+entry[2])
                elif qname.startswith("ns1"):
                    print("DATA\t"+bits+"\t"+auth+"\tns1."+domain+"\t"+qclass+"\tA\t3600\t-1\t"+nameserverList[0])
                elif qname.startswith("ns2"):
                    print("DATA\t"+bits+"\t"+auth+"\tns2."+domain+"\t"+qclass+"\tA\t3600\t-1\t"+nameserverList[1])
                else:
                    try:
                        response = reader.city(ip)
                        ip = data.getClosestPoP(response.location.latitude,response.location.longitude,pops)
                    except Exception as e:
                        stderr.write("Error "+str(e)+"\n")
                        stderr.write("Could not resolve "+ip+"\n")
                        ip = pops[0][3]
                    print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tA\t1\t-1\t"+ip)

    print("END");
    if time.time() > lastupdate + 60:
        pool.apply_async(updateData, callback=syncData)
        lastupdate = time.time()
