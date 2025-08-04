amazon
亚马逊代理
quickstart
build
$ docker build -t amazon .
start
$ docker compose -f deploy/compose-dev.yaml up  -d
stop
$ docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose-dev.yaml stop
debug
$ docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose-dev.yaml logs -f
