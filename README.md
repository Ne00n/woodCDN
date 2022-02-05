# woodCDN

## Work in Progress

**Idea**<br />
- Multiple low end servers
- Simple cli to manage vhosts and settings
- Keep the overhead and dependencies at a minimum
- Keep it Simple and Stupid and fucking Dry
- High Availability, even if the db cluster shits itself, stuff should keep going
- GeoDNS to reduce latency

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

## Setup<br />
1. Get a full mesh VPN like [tinc](https://www.tinc-vpn.org/) and deploy it on all nodes (at least 3)</br >
You can use ansible for that so you get it up in a few minutes. Fork that I [use](https://github.com/Ne00n/ansible-tinc).</br >
Add rqlite as entry to hosts that points to the local vpn interface.<br />
```
echo "10.0.251.x rqlite" >> /etc/hosts
```
2. Setup a [rqlite](https://github.com/rqlite/rqlite) instance on every node<br >
```
adduser cdn --disabled-login
#Make sure to check for the latest release!
su cdn; curl -L https://github.com/rqlite/rqlite/releases/download/v7.2.0/rqlite-v7.2.0-linux-amd64.tar.gz -o rqlite-v7.2.0-linux-amd64.tar.gz
tar xvfz rqlite-v7.2.0-linux-amd64.tar.gz; mv rqlite-v7.2.0-linux-amd64 rqlite
#First node
rqlited -node-id 1 -http-addr 10.0.0.x:4003 -raft-addr 10.0.0.x:4004 datadir
#Moah nodes
rqlited -node-id 2 -http-addr 10.0.0.x:4003 -raft-addr 10.0.0.x:4004 -join http://10.0.0.1:4003 datadir
```
To run rqlite as service and on boot, checkout config/rqlite.service<br />
You can check the cluster status by running<br />
**rqlite is known to NOT resolve hostnames!**
```
curl rqlite:4003/nodes?pretty
```
3. Deploy the Code

**All Nodes**
```
apt-get install sudo git python3 python3-pip -y && pip3 install simple-acme-dns
mkdir /opt/woodCDN && chown -R cdn:cdn /opt/woodCDN/ && cd /opt/;su cdn
git clone https://github.com/Ne00n/woodCDN.git && cd woodCDN && git checkout gdnsd
exit; chmod 775 -R /opt/woodCDN; chmod 750 /opt/woodCDN/certs
cp /opt/woodCDN/config/cdnLastrun.service /etc/systemd/system/ && systemctl enable cdnLastrun && systemctl start cdnLastrun
cp /opt/woodCDN/config/cdnCert.service /etc/systemd/system/ && systemctl enable cdnCert && systemctl start cdnCert
```
**Nginx Nodes**
```
apt-get install nginx -y
mkdir -p /data/nginx/cache && chgrp -R cdn /etc/nginx/sites-enabled/ && chmod 775 -R /etc/nginx/sites-enabled/
echo "cdn ALL=(ALL) NOPASSWD: /usr/sbin/service nginx reload" >> /etc/sudoers
cp /opt/woodCDN/config/cdnNginx.service /etc/systemd/system/ && systemctl enable cdnNginx && systemctl start cdnNginx
```
**DNS Nodes**
```
apt-get install gdnsd -y
echo "cdn ALL=(ALL) NOPASSWD: /usr/sbin/service gdnsd restart" >> /etc/sudoers
echo "cdn ALL=(ALL) NOPASSWD: /usr/local/bin/gdnsdctl reload-zones" >> /etc/sudoers
chgrp -R cdn /etc/gdnsd/ && chmod 775 -R /etc/gdnsd/
cp /opt/woodCDN/config/cdnDNS.service /etc/systemd/system/ && systemctl enable cdnDNS && systemctl start cdnDNS
```
1GB+ Memory needed for boot<br />
Afterwards you should be able to run on that on any node but just once<br />
```
python3 cli.py init
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
python3 cli.py pop add <hostname of node> <v4>
#Example
python3 cli.py pop add atlanta 3.3.3.3
#The hostname needs to match the hostname of the node, otherwise the cron won't be updating data correctly
```
Add your first vhost (proxy/dns) entry
```
python3 cli.py vhost add <domain> <subdomain> <type> <value>
#type can be proxy or A, TXT...
#to proxy a IP/Domain
python3 cli.py vhost add bla.com test proxy website.com
#to add a static dns entry
python3 cli.py vhost add bla.com static A 2.2.2.2
```
