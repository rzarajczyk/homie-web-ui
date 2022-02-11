#!/bin/bash
TAG=$(date '+%Y%m%d')
docker build -t rzarajczyk/homie-web-ui:$TAG .
docker tag rzarajczyk/homie-web-ui:$TAG rzarajczyk/homie-web-ui:latest
docker push rzarajczyk/homie-web-ui:$TAG
docker push rzarajczyk/homie-web-ui:latest
