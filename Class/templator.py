class Templator:
    def nginxHTTP(self,domain,target):
        template = '''
server {
    listen 80;
    server_name '''+domain+''';
    location / {
        proxy_set_header Host '''+domain+''';
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://'''+target+''';
        proxy_redirect off;
    }
}'''
        return template
    def nginxHTTPS(self,domain,target):
        template = '''
server {
    listen 443;
    server_name '''+domain+''';

    ssl_certificate           /opt/woodCDN/certs/'''+domain+'''-fullchain.pem;
    ssl_certificate_key       /opt/woodCDN/certs/'''+domain+'''-privkey.pem;
    ssl on;

    location / {
        proxy_set_header Host '''+domain+''';
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://'''+target+''';
        proxy_redirect off;
    }
}'''
        return template
