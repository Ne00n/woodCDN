class Templator:
    def nginxHTTP(self,domain,target):
        template = '''
server {
    listen 80;
    server_name '''+domain+''';
    location / {
        proxy_set_header Host '''+domain+''';
        proxy_pass http://'''+target+''';
        proxy_redirect off;
    }
}'''
        return template
