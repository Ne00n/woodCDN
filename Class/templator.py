import itertools

class Templator:
    def nginxWrap(self,domain,body):
        template = '''
proxy_cache_path /data/nginx/cache/'''+domain+''' levels=1:2 keys_zone='''+domain+''':10m inactive=24h  max_size=1g;
'''+body+'''
'''
        return template
    def nginxHTTP(self,domain,target):
        template = '''
server {
    listen 80;
    server_name '''+domain+''';
    server_tokens off;

    location / {
        proxy_set_header Host '''+target+''';
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://'''+target+''';
        proxy_redirect off;
    }
}
'''
        return template

    def nginxHTTPS(self,domain,target):
        template = '''
server {
    listen 443 ssl http2;
    server_name '''+domain+''';
    server_tokens off;

    ssl_certificate     /opt/woodCDN/certs/'''+domain+'''-fullchain.pem;
    ssl_certificate_key /opt/woodCDN/certs/'''+domain+'''-privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3; #drop 1.0 and 1.1

    location ~* ^.+\.(?:css|cur|js|jpe?g|gif|htc|ico|png|html|xml|otf|ttf|eot|woff|woff2|svg)$ {
        proxy_cache '''+domain+''';
        proxy_cache_valid 200 1d;
        proxy_cache_valid 404 1m;
        proxy_set_header Host '''+target+''';
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass https://'''+target+''';
        proxy_redirect off;
    }

    location / {
        proxy_set_header Host '''+target+''';
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass https://'''+target+''';
        proxy_redirect off;
    }
}
'''
        return template

    def gdnsdConfig(self,pops,popsList):
        template = '''service_types => {
  state => {
    plugin => "extfile",
    file => "/usr/local/var/lib/gdnsd/state",
    direct => true,
  }
}
plugins => { geoip => {
  undefined_datacenters_ok = true
  maps => {
    prod => {
      datacenters => ['''
        for index, pop in enumerate(pops):
            template += str(pop[0])
            if index < len(pops) -1: template += ","
        template += '''],
      nets = dc.conf
    }
  },
  resources => {
    prod_www => {
      map => prod
      service_types => state,
      dcmap => {
'''
        for pop in pops:
            template += "       "+pop[0]+" => "+pop[1]+",\n"
        template += '''      }
    }
  }
}}'''
        return template

    def gdnsdZone(self,vhost):
        template = '''$TTL 86400
@     SOA ns1 '''+vhost[0]+''' (
      1      ; serial
      7200   ; refresh
      30M    ; retry
      3D     ; expire
      900    ; ncache
)
@       NS      ns1
@       NS      ns2
'''
        for index, nameserver in enumerate(vhost[1]['nameserver'].split(",")):
            template += 'ns'+str(index +1)+' 3600 A '+nameserver+"\n"
        template += "\n"
        if not vhost[1]['records']: return template
        for record in vhost[1]['records']:
            if record['type'] == "proxy":
                template += record['record']+'   30 	DYNA 	 geoip!prod_www'+'\n'
            elif record['type'] == 'TXT':
                template += record['record']+'   3600 	'+record['type']+' 	 "'+record['target']+'"\n'
            else:
                template += record['record']+'   3600 	'+record['type']+' 	 '+record['target']+'\n'
        return template
