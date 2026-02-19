#!/bin/sh
set -e

# 仅替换 BACKEND_URL，保留 nginx 自身变量（$uri 等）
envsubst '${BACKEND_URL}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
