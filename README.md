# Fango应用说明

### build

```sh
$ docker build -t fango .
```

### start

```sh
$ docker compose -f deploy/docker-compose.yml up  -d
```

### stop

```sh
$ docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose-dev.yaml stop
```

### debug

```sh
$ docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose-dev.yaml logs -f
```

