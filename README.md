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
- python3 for syncing/generating the vhosts
- python3 to add/edit/delete vhosts and settings

**Setup**<br />
```
#Nginx
apt-get install sudo nginx git python3 -y
#DNS
apt-get install git python3 pdns-server pdns-backend-pipe -y
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

You need some kind of decentralized vpn like cloudvpn or tinc otherwise rqlite tls configuration will be quite painful.<br />
You can get the free country lite database here https://dev.maxmind.com/geoip/geoip2/geolite2/<br />

**rqlite**<br />
```
#First node
./rqlited -http-addr 10.0.0.1:4003 -raft-addr 10.0.0.1:4004 datadir
#Moah nodes
./rqlited -http-addr 10.0.0.2:4003 -raft-addr 10.0.0.2:4004 -join http://10.0.0.1:4003 datadir
```
Afterwards you should be able to run on that on any node but just once
```
python3 cli.py init
```

**cron**<br />
You need to add python3 generate.py nginx to cronjob at least every 60s, to sync the database with the local nginx<br />
