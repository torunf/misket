# Statik siteyi nginx ile servis eder — build adımı yok, dosyalar olduğu gibi.
FROM nginx:alpine
COPY . /usr/share/nginx/html
RUN rm -f /usr/share/nginx/html/Dockerfile /usr/share/nginx/html/CNAME && \
    printf 'server {\n  listen 80;\n  root /usr/share/nginx/html;\n  location / { try_files $uri $uri/ $uri/index.html =404; }\n  gzip on;\n  gzip_types text/css application/javascript application/json image/svg+xml;\n  add_header X-Content-Type-Options nosniff;\n}\n' > /etc/nginx/conf.d/default.conf
