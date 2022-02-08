#!/bin/bash
docker run -it --rm \
    --name homie-web-ui \
    -v $(pwd)/config:/homie-web-ui/config \
    -v $(pwd)/logs:/homie-web-ui/logs \
    -p 8080:8080 \
    rzarajczyk/homie-web-ui:latest
