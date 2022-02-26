#!/bin/bash
`TMP=$(mktemp -d)
cp $(pwd)/config/smart-devices-to-mqtt.yaml $TMP
echo "Temp directory is $TMP"
docker run -it --rm \
    --name homie-web-ui \
    -v $TMP:/homie-web-ui/config \
    -p 8080:8080 \
    rzarajczyk/homie-web-ui:latest
