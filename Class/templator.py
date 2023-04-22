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

    def nginxHTTPS(self,domain,target,pop):
        template = '''
server {
    listen 443 ssl http2;
    server_name '''+domain+''';
    server_tokens off;

    ssl_certificate     /opt/woodCDN/certs/'''+domain+'''-fullchain.pem;
    ssl_certificate_key /opt/woodCDN/certs/'''+domain+'''-privkey.pem;
    ssl_trusted_certificate /opt/woodCDN/certs/'''+domain+'''-fullchain.pem;
    ssl_protocols TLSv1.2 TLSv1.3; #drop 1.0 and 1.1
    ssl_stapling_verify on;
    ssl_stapling on;

    add_header woodCDN-cache-status $upstream_cache_status;
    add_header woodCDN-pop '''+pop+''';  

    location ~* ^.+\.(?:css|cur|js|jpe?g|gif|htc|ico|png|html|xml|otf|ttf|eot|woff|woff2|svg)$ {
        proxy_cache '''+domain+''';
        proxy_cache_valid 200 301 302 1d;
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

    def gdnsdConfig(self,pops,popsList,geocast):
        template = '''service_types => {
  state => {
    plugin => "extfile",
    file => "/tmp/state",
    direct => true,
  }
}
plugins => { geoip => {
  undefined_datacenters_ok = true
  maps => {'''
        if geocast and 'values' in geocast['results'][0]:
            geocast = geocast['results'][0]['values']
            template += '''
    geocast => {
      geoip2_db => geo.mmdb,
      datacenters => ['''
        for index, geo in enumerate(geocast):
            template += str(geo[0])
            if index < len(geocast) -1: template += ","
        template += '''],
      auto_dc_coords => {
'''
        for geo in geocast:
            if geo[1] == "anycast": continue
            template += f"       {geo[0]} => [ {geo[2]}, {geo[3]} ],\n"
        template += '''
      }
    },
    wood => {
      geoip2_db => geo.mmdb,
      datacenters => ['''
        for index, pop in enumerate(pops):
            template += str(pop[0])
            if index < len(pops) -1: template += ","
        template += '''],
      auto_dc_coords => {
'''
        for pop in pops:
            if pop[1] == "anycast": continue
            template += f"       {pop[0]} => [ {pop[2]}, {pop[3]} ],\n"
        template += '''
      }
    }
  },
  resources => {
    wood_www => {
      map => wood
      service_types => state,
      dcmap => {
'''
        for pop in pops:
            template += f"       {pop[0]} => {pop[4]},\n"
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
'''
        for index, nameserver in enumerate(vhost[1]['nameserver'].split(",")):
            template += '@       NS      ns'+str(index +1)+"\n"
            template += 'ns'+str(index +1)+' 3600 A '+nameserver+"\n"
        template += "\n"
        if not vhost[1]['records']: return template
        for record in vhost[1]['records']:
            if record['type'] == "proxy":
                template += record['record']+'   30 	DYNA 	 geoip!wood_www'+'\n'
            elif record['type'] == 'TXT':
                template += record['record']+'   3600 	'+record['type']+' 	 "'+record['target']+'"\n'
            else:
                template += record['record']+'   3600 	'+record['type']+' 	 '+record['target']+'\n'
        return template
