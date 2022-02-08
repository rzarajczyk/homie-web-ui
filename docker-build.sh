#!/bin/bash
TAG=$1
if [ -z $TAG ]; then
    echo "TAG is required"
    exit 1
fi

docker build -t rzarajczyk/homie-web-ui:$TAG .
docker tag rzarajczyk/homie-web-ui:$TAG rzarajczyk/homie-web-ui:latest
