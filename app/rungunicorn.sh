#!/bin/bash
#openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private.pem -out public.pem
openssl req -new -newkey rsa:4096 -days 3650 -nodes -x509 \
    -subj "/C=US/ST=Ohio/L=Cleveland/O=SHW/CN=localhost" \
    -keyout private.pem  -out public.pem
gunicorn --certfile=public.pem --keyfile=private.pem -w 4 -b 0.0.0.0:7070 app:app
