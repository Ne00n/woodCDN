# woodCDN

## Work in Progress, proceed with caution

**Idea**<br />
- Multiple low end servers
- Simple cli to manage vhosts and settings
- Keep the overhead and dependencies at a minimum
- Keep it Simple and Stupid and fucking Dry
- Decentralized + High Availability even if the db cluster shits itself, stuff should keep going
- GeoDNS to reduce latency

**Software**<br />
- Nginx as proxy/caching device
- rqlite to store the vhosts
- python3 for syncing/generating the vhosts
- python3 to add/edit/delete vhosts and settings

**Setup**<br />
```
apt-get install sudo nginx git python3 -y
adduser cdn --disabled--login
chgrp -R cdn /etc/nginx/sites-enabled/
chmod 775 -R /etc/nginx/sites-enabled/
echo "cdn ALL=(ALL) NOPASSWD: /usr/sbin/service nginx reload" >> /etc/sudoers
cd /home/cdn/;su cdn
git clone https://github.com/Ne00n/woodCDN.git
```

**rqlite**<br />
```
rqlited -http-addr 127.0.0.1:4001 -http-cert server.crt \
-http-key key.pem -raft-addr :4004 -join https://xxx.xxx.xxx.xxx:4004 \
-node-encrypt -node-cert node.crt -node-key node-key.pem dataDir
```

You need signed cert otherwise use -no-node-verify however this is not recommended.<br />

**cron**<br />
You need to add python3 generate.py nginx to cronjob at least every 60s, to sync the database with the local nginx<br />
