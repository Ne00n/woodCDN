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
- [rqlite](https://github.com/rqlite/rqlite) to store the vhosts/domains/pops
- [geodns](https://github.com/abh/geodns) as nameserver + geo
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

**Setup**<br />
1. Get a full mesh VPN like [tinc](https://www.tinc-vpn.org/) and deploy it on all nodes (at least 3)</br >
You can use ansible for that so you get it up in a few minutes. Fork that I [use](https://github.com/Ne00n/ansible-tinc).</br >
Add rqlite as entry to hosts that points to the local vpn interface.<br />
2. Setup a [rqlite](https://github.com/rqlite/rqlite) instance on every node<br >
```
adduser cdn --disabled-login
#Make sure to check for the latest release!
su cdn; curl -L https://github.com/rqlite/rqlite/releases/download/v5.8.0/rqlite-v5.8.0-linux-amd64.tar.gz -o rqlite-v5.8.0-linux-amd64.tar.gz
tar xvfz rqlite-v5.8.0-linux-amd64.tar.gz; mv xvfz rqlite-v5.8.0-linux-amd64 rqlite
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
3. Deploy the Code<br />

**Nginx / DNS** <br />
```
apt-get install git python3 python3-pip -y
pip3 install simple-acme-dns
#Nginx and DNS
mkdir /opt/woodCDN
chown -R cdn:cdn /opt/woodCDN/
cd /opt/;su cdn
git clone https://github.com/Ne00n/woodCDN.git
exit; chmod 775 -R /opt/woodCDN; chmod 750 /opt/woodCDN/certs
```
**Nginx**<br />
```
apt-get install sudo nginx git python3 python3-pip -y
pip3 install simple-acme-dns
mkdir -p /data/nginx/cache
chgrp -R cdn /etc/nginx/sites-enabled/
chmod 775 -R /etc/nginx/sites-enabled/
echo "cdn ALL=(ALL) NOPASSWD: /usr/sbin/service nginx reload" >> /etc/sudoers
```
**DNS** <br />
```
#Make sure to check for the latest release!
wget https://golang.org/dl/go1.16.linux-amd64.tar.gz
tar -C /usr/local -xzf go*.linux-amd64.tar.gz
echo "export PATH=$PATH:/usr/local/go/bin" >> /etc/profile
go version
su cdn; cd /home/cdn
git clone https://github.com/Ne00n/geodns
cd geodns; ./build.sh
```

You can get maxmind databases [here](https://dev.maxmind.com/geoip/geoip2/geolite2/)<br />
Get & Put<br />
```
GeoLite2-ASN.mmdb
GeoLite2-City.mmdb                                    
GeoLite2-Country.mmdb
```

Into /usr/share/GeoIP/ on each dns node<br />
**service**<br />
```
#Nginx
cp /opt/woodCDN/config/cdnGenerateNginx.service /etc/systemd/system/
systemctl enable cdnGenerateNginx && systemctl start cdnGenerateNginx
#Nginx and DNS
cp /opt/woodCDN/config/cdnLastrun.service /etc/systemd/system/
systemctl enable cdnLastrun && systemctl start cdnLastrun
#DNS
cp /opt/woodCDN/config/cdnGenerateDNS.service /etc/systemd/system/
systemctl enable cdnGenerateDNS && systemctl start cdnGenerateDNS
cp /opt/woodCDN/config/geodns.service /etc/systemd/system/
systemctl enable geodns && systemctl start geodns
```

**cron**<br />
```
*/5 *  *   *   *     /opt/woodCDN/scripts/cert.sh >/dev/null 2>&1      #all nodes
```

**init**<br />
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
python3 cli.py pop add <hostname of node> <country> <latitude> <longitude> <v4>
#Example
python3 cli.py pop add gravelines fr 46.22 2.21 3.3.3.3
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
