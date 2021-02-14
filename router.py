#!/usr/bin/python3 -u
from sys import stdin, stderr, exit
from Class.cli import CLI
from Class.data import Data
import geoip2.database, time

reader = geoip2.database.Reader("/opt/woodCDN/GeoLite2-City.mmdb")

cli = CLI()
data = Data()

nameservers,lastupdate,vhosts,pops = {},time.time(),{},{}

def updateData():
    fallback = False
    data = cli.query(["SELECT * FROM domains",'SELECT * FROM vhosts WHERE type != "proxy"',"SELECT * FROM pops"])

    if (data is False or "values" not in data['results'][0] or "values" not in data['results'][1] or "values" not in data['results'][2]):
        stderr.write("domains/vhosts/pops table missing or empty\n")
        return False

    pops = [x for x in data['results'][2]['values'] if x[4] + 60 > int(time.time())]
    if len(pops) == 0:
        pops = data['results'][2]['values'] #fallback
        fallback = True
    for row in data['results'][0]['values']:
        nameservers[row[0]] = row[1].split(",")
    for row in data['results'][1]['values']:
        if row[2] == "@":
            if not row[1] in vhosts: vhosts[row[1]] = []
            vhosts[row[1]].append(row[3:])
        else:
            subdomain = row[2]+"."+row[1]
            if not subdomain in vhosts: vhosts[subdomain] = []
            vhosts[subdomain].append(row[3:])
    return {'ns':nameservers,'vhosts':vhosts,'pops':pops,'fallback':fallback}

response = updateData()
if response is False:
    time.sleep(1.5) #slow down pdns restarts
    exit()

nameservers,vhosts,pops,fallback = response['ns'],response['vhosts'],response['pops'],response['fallback']

line = stdin.readline()
if "HELO\t3" not in line:
    stderr.write("Received unexpected line, wrong ABI version?\n")
    print("FAIL")

print("OK\twoodCDN Router")
stderr.write("wood is loaded\n")

geoCache = {}

while True:
    line = stdin.readline().rstrip()

    if (len(line.split("\t")) < 8):
        stderr.write("PowerDNS sent unparseable line\n")
        print("FAIL")
        continue

    type, qname, qclass, qtype, id, ip, localip, ednsip = line.split("\t")
    bits,auth,qname = "21","1",qname.lower()

    source = ip
    if ednsip != "0.0.0.0/0":
        sourceIP, sourcePrefix = ednsip.split("/")
        source = sourceIP

    if time.time() > lastupdate + 30:
        freshData = updateData()
        if freshData is not False:
            oldPoPs = pops
            nameservers,vhosts,pops,fallback = freshData['ns'],freshData['vhosts'],freshData['pops'],freshData['fallback']
            stderr.write("Updated NS information\n")
            if len(pops) != len(oldPoPs):
                stderr.write("Flushing geocache\n")
                geoCache = {}
        lastupdate = time.time()

    for domain, nameserverList in nameservers.items():
        if qname.endswith(domain):

            if(qtype == "SOA" or qtype == "ANY"):
                print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tSOA\t3600\t-1\tns1."+domain+" noc."+domain+" 2008080300 1800 3600 604800 3600")

            if(qtype == "NS" or qtype == "ANY"):
                print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tNS\t3600\t-1\tns1."+domain)
                print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tNS\t3600\t-1\tns2."+domain)

            if(qtype == "A" or qtype == "ANY"):
                skipGeo = False
                if qname.startswith("ns"):
                    skipGeo = True
                    if qname.startswith("ns1"):
                        print("DATA\t"+bits+"\t"+auth+"\tns1."+domain+"\t"+qclass+"\tA\t3600\t-1\t"+nameserverList[0])
                    elif qname.startswith("ns2"):
                        print("DATA\t"+bits+"\t"+auth+"\tns2."+domain+"\t"+qclass+"\tA\t3600\t-1\t"+nameserverList[1])
                elif qname in vhosts:
                    for entry in vhosts[qname]:
                        if entry[0] == "A": skipGeo = True
                        print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\t"+entry[0]+"\t3600\t-1\t"+entry[1])

                if skipGeo is False:
                    if not source in geoCache:
                        try:
                            response = reader.city(source)
                            popIP = data.getClosestPoP(response.location.latitude,response.location.longitude,pops,fallback)
                            geoCache[source] = popIP
                        except Exception as e:
                            stderr.write("Error "+str(e)+"\n")
                            stderr.write("Could not resolve "+source+"\n")
                            popIP = pops[0][3]
                            geoCache[source] = popIP
                    else:
                        popIP = geoCache[source]
                    print("DATA\t"+bits+"\t"+auth+"\t"+qname+"\t"+qclass+"\tA\t1\t-1\t"+popIP)

    print("END")
