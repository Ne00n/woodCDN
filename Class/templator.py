class Templator:
    def nginxWrap(self,body):
        template = '''
proxy_cache_path /data/nginx/cache levels=1:2 keys_zone=STATIC:10m inactive=24h  max_size=1g;
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
    listen 443;
    server_name '''+domain+''';
    server_tokens off;

    ssl_certificate     /opt/woodCDN/certs/'''+domain+'''-fullchain.pem;
    ssl_certificate_key /opt/woodCDN/certs/'''+domain+'''-privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3; #drop 1.0 and 1.1
    ssl on;

    location ~* ^.+\.(?:css|cur|js|jpe?g|gif|htc|ico|png|html|xml|otf|ttf|eot|woff|woff2|svg)$ {
        proxy_cache STATIC;
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
