#!/bin/bash

if [ -n "$1" ]; then
    openssl req -new -newkey rsa:2048 -days 365 -nodes -sha256 -x509 -keyout ./clients/privateKeys/$1.key -out ./clients/certs/$1.crt -subj "/CN=$1" &>/dev/null
    cat ./clients/certs/$1.crt >> ./server/clients.pem
fi