# woodCDN

## Work in Progress

**Idea**<br />
- Multiple low end servers
- Simple cli to manage vhosts and settings
- Keep the overhead and dependencies at a minimum
- Keep it Simple and Stupid and fucking Dry
- High Availability, even if the db cluster shits itself, stuff should keep going
- Latency Based routing to reduce latency

**Software**<br />
- Nginx as proxy/caching device
- rqlite to store the vhosts/domains/pops
- gdnsd as nameserver + latency based routing
- python3 for syncing/generating the vhosts
- python3 to add/edit/delete vhosts and settings

**Features**<br />
- High Availability
- HTTPS Support (single cert)
- Renew Certificates after 30 days
- Rerouting offline locations
- Geo routed + proxied DNS entries
- Static DNS entries

**Todo**<br />
- HTTPS Support (wildcard)
- IPv6 Support

**Routing Data**<br />
- https://github.com/Ne00n/latency-geolocator-4550<br>
Since the goal is to use latency based routing, you first need to scan the entire internet and build the routing file with the tool above.<br>
In theory you can write the routing file by hand, if you want, for testing and such.<br>

## Setup<br />
1. Get a full mesh VPN like [tinc](https://www.tinc-vpn.org/) and deploy it on all nodes (at least 3)</br >
You can use ansible for that so you get it up in a few minutes. Fork that I [used](https://github.com/Ne00n/ansible-tinc).</br >
Add rqlite as entry to hosts that points to the local vpn interface.<br />
```
echo "10.0.x.x rqlite" >> /etc/hosts
```
2. Install woodCDN<br >
```
adduser cdn --disabled-login
mkdir /opt/woodCDN && chown -R cdn:cdn /opt/woodCDN/ && cd /opt/;su cdn
git clone https://github.com/Ne00n/woodCDN.git && cd woodCDN && git checkout gdnsd
exit; chmod 775 -R /opt/woodCDN; chmod 750 /opt/woodCDN/certs
```
3. Setup a [rqlite](https://github.com/rqlite/rqlite) instance on every node<br >
```
su cdn -c "cd; wget https://github.com/rqlite/rqlite/releases/download/v7.14.2/rqlite-v7.14.2-linux-amd64.tar.gz && tar xvf rqlite-v7.14.2-linux-amd64.tar.gz && mv rqlite-v7.14.2-linux-amd64 rqlite"
#Make sure to check for the latest release!
cp /opt/woodCDN/config/rqlite.service /etc/systemd/system/rqlite.service
#Needs to be edited
systemctl enable rqlite && systemctl start rqlite
```
**rqlite is known to NOT resolve hostnames!**<br />
To run rqlite as service and on boot, checkout config/rqlite.service<br />
You can check the cluster status by running<br />
```
curl rqlite:4003/nodes?pretty
```
4. Deploy the Code

You may need run beforehand
```
apt-get install python3-dev build-essential libffi-dev -y
```

**All Nodes**
```
apt-get install sudo git python3 python3-pip -y && pip3 install simple-acme-dns
cp /opt/woodCDN/config/cdnLastrun.service /etc/systemd/system/ && systemctl enable cdnLastrun && systemctl start cdnLastrun
cp /opt/woodCDN/config/cdnCert.service /etc/systemd/system/ && systemctl enable cdnCert && systemctl start cdnCert
```
**Nginx Nodes**
```
apt-get install nginx -y
mkdir -p /data/nginx/cache && chgrp -R cdn /etc/nginx/sites-enabled/ && chmod 775 -R /etc/nginx/sites-enabled/
echo "cdn ALL=(ALL) NOPASSWD: /usr/sbin/service nginx reload" >> /etc/sudoers.d/woodCDN
cp /opt/woodCDN/config/cdnNginx.service /etc/systemd/system/ && systemctl enable cdnNginx && systemctl start cdnNginx
cp /opt/woodCDN/config/woodCDN.conf /etc/nginx/conf.d/
```
**DNS Nodes**
```
apt-get install gdnsd -y
echo "cdn ALL=(ALL) NOPASSWD: /usr/sbin/service gdnsd restart" >> /etc/sudoers.d/woodCDN
echo "cdn ALL=(ALL) NOPASSWD: /usr/bin/gdnsdctl reload-zones" >> /etc/sudoers.d/woodCDN
#If you compiled gdnsd
#echo "cdn ALL=(ALL) NOPASSWD: /usr/local/bin/gdnsdctl reload-zones" >> /etc/sudoers.d/woodCDN
#continue
chgrp -R cdn /etc/gdnsd/ && chmod 775 -R /etc/gdnsd/
cp /opt/woodCDN/config/cdnDNS.service /etc/systemd/system/ && systemctl enable cdnDNS && systemctl start cdnDNS
#Give gdnsd access to /tmp/state (systemd)
systemctl edit --full gdnsd
#add this, below Service
TemporaryFileSystem=/tmp/:ro
BindReadOnlyPaths=/tmp/state
```
300MB up to 2GB Memory needed for gdnsd (depends on zone file size, failover nodes...)<br />
**If you upload the dc.conf, the POP's need to be already added, otherwise gdnsd will refuse to start**<br>
Afterwards you should be able to run that on any node but just once<br />
```
cd /opt/woodCDN; python3 cli.py init
```

**cli**<br />
Add your first Domain
```
python3 cli.py domain add <name> <email> <ns1>,<ns2>
#Example
python3 cli.py domain add bla.com noc@bla.com 1.1.1.1,2.2.2.2
#The email is needed for lets encrypt
```
Add your first PoP<br/>
```
python3 cli.py pop add <id> <hostname of node> <v4>
#Example
python3 cli.py pop add 1 atlanta 3.3.3.3
#The hostname needs to match the hostname of the node, otherwise the cron won't be updating data correctly
```
- Internally the system uses the id from the rqlite database, these have to match the ID's from the dc.conf<br>
- The first POP you add, is used by gdnsd to route traffic that can't be associated/mapped with the dc.conf<br>
- The name/pop "anycast" will be always set to UP<br>
- The POP name is case sensitive<br>

Add your first vhost (proxy/dns) entry
```
python3 cli.py vhost add <domain> <subdomain> <type> <value>
#type can be proxy or A, TXT...
#to proxy a IP/Domain
python3 cli.py vhost add bla.com test proxy website.com
#to add a static dns entry
python3 cli.py vhost add bla.com static A 2.2.2.2
```
