# homie-web-ui



## Not recommended to general usage!
This code is written mainly for my personal purpose. I do not take any responsibility for this code,
and I will not provide any support for it. If you really want to use it - ok, but make sure you know
what you're doing.

[//]: # (### Usage)

[//]: # (Build:)

[//]: # (```shell)

[//]: # (docker build -t rzarajczyk/smart-home-services:<<newtag>> .)

[//]: # (docker tag rzarajczyk/smart-home-services:<<newtag>> rzarajczyk/smart-home-services:latest)

[//]: # (```)

[//]: # (Run:)

[//]: # (```shell)

[//]: # (docker run -it --rm  --network="host" --name smart-home-services -v $&#40;pwd&#41;/config:/smart-home-services/config -v $&#40;pwd&#41;/logs:/smart-home-services/logs rzarajczyk/smart-home-services:latest)

[//]: # (```)

[//]: # (Directories to mount:)

[//]: # (- `/smart-home-services/config` - it will contain config file. If directory is empty, sample config will be created.)

[//]: # (- `/smart-home-services/logs` - it will contain log file.)

