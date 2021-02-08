# woodCDN

## Work in Progress

**Idea**<br />
- Multiple low end servers
- Simple cli to manage vhosts and settings
- Keep the overhead and dependencies at a minimum
- Keep it Simple and Stupid and fucking Dry
- Decentralized + High Availability even if the db cluster shits itself, stuff should keep going
- GeoDNS to reduce latency

**Software**<br />
- Nginx as proxy/caching device
- rqlite to store the vhosts/domains/pops
- pdns as nameserver + geodns
- python3 for syncing/generating the vhosts
- python3 to add/edit/delete vhosts and settings

**Features**<br />
- High Availability
- Not proxied DNS entries

**Todo**<br />
- Rerouting offline locations
- HTTPS Support (wildcard per domain)

**Setup**<br />
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

You need some kind of decentralized mesh vpn like VpnCloud or Tinc otherwise rqlite tls configuration will be quite painful.<br />
You can get the free city lite database here https://dev.maxmind.com/geoip/geoip2/geolite2/<br />

**rqlite**<br />
```
#First node
rqlited -http-addr 10.0.0.1:4003 -raft-addr 10.0.0.1:4004 datadir
#Moah nodes
rqlited -http-addr 10.0.0.2:4003 -raft-addr 10.0.0.2:4004 -join http://10.0.0.1:4003 datadir
```
You can check the cluster status by running
```
rqlite --host rqlite --port 4003
.status
```
To run rqlite as service and on boot config/rqlite.service<br />
Afterwards you should be able to run on that on any node but just once<br />
```
python3 cli.py init
```

**cron**<br />
You need to add python3 generate.py nginx to cronjob at least every 60s, to sync nginx with the database<br />
