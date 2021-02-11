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
- pdns as nameserver + geodns
- python3 for syncing/generating the vhosts
- python3 to add/edit/delete vhosts and settings

**Features**<br />
- High Availability
- HTTPS Support (single cert)
- Rerouting offline locations
- Geo routed + proxied DNS entries
- Static DNS entries

**Todo**<br />
- HTTPS Support (wildcard)

**Setup**<br />
1. Get a full mesh VPN like [tinc](https://www.tinc-vpn.org/) and deploy it on all nodes (at least 3)</br >
You can use ansible for that so you get it up in a few minutes. Fork that I [use](https://github.com/Ne00n/ansible-tinc).</br >
Add rqlite entry to hosts that points to the local vpn interface.<br />
2. Setup a [rqlite](https://github.com/rqlite/rqlite) instance on every node<br >
```
#First node
rqlited -http-addr 10.0.0.1:4003 -raft-addr 10.0.0.1:4004 datadir
#Moah nodes
rqlited -http-addr 10.0.0.2:4003 -raft-addr 10.0.0.2:4004 -join http://10.0.0.1:4003 datadir
```
You can check the cluster status by running
```
curl rqlite:4003/status?pretty
#or
rqlite --host rqlite --port 4003
.status
```
To run rqlite as service and on boot config/rqlite.service<br />
3. Deploy the Code
```
#Nginx
apt-get install sudo nginx git python3 python3-pip -y
#DNS
apt-get install git python3 python3-pip pdns-server pdns-backend-pipe -y
pip3 install geoip2
#Both
adduser cdn --disabled-login
#Nginx
chgrp -R cdn /etc/nginx/sites-enabled/
chmod 775 -R /etc/nginx/sites-enabled/
echo "cdn ALL=(ALL) NOPASSWD: /usr/sbin/service nginx reload" >> /etc/sudoers
#Both
mkdir /opt/woodCDN
chown -R cdn:cdn /opt/woodCDN/
cd /opt/;su cdn
git clone https://github.com/Ne00n/woodCDN.git
exit; chmod 775 -R /opt/woodCDN
```

You can get the free city lite database [here](https://dev.maxmind.com/geoip/geoip2/geolite2/)<br />
Put the Database on each dns node in /opt/woodCDN<br />
Afterwards you should be able to run on that on any node but just once<br />
```
python3 cli.py init
```

**cli**<br />
Add your first Domain
```
python3 cli.py domain add <name> <email> <ns1>,<ns2>
```
Add your first PoP<br/>
```
python3 cli.py pop add <hostname of node> <v4> <latitude> <longitude>
```
Add your first vhost (proxy/dns) entry
```
python3 cli.py vhost add <domain> <subdomain> <type> <value>
#type can be proxy or A, TXT...
```

**cron**<br />
Check /scripts, lastrun (nginx/pop) and generate (nginx/pop) need to be added as cronjob to run every 60s<br />
Afterwards you can bring the dns servers online, without any entries or configured cronjobs they won't start.<br />
