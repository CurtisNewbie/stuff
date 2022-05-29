#!/bin/bash

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/curtisnewbie.com.key -out /etc/ssl/certs/curtisnewbie.com.crt

cp /etc/ssl/certs/curtisnewbie.com.crt /home/alphaboi/services/nginx/cert/curtisnewbie.com.crt
cp /etc/ssl/private/curtisnewbie.com.key /home/alphaboi/services/nginx/cert/curtisnewbie.com.key
