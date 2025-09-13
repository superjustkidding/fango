# Fango应用说明

### 构建和启动所有服务
```sh
$ docker-compose -f deployed/docker-compose.yml up -d --build
```
### 查看所有服务状态
```sh
$ docker-compose -f deployed/docker-compose.yml ps
```

### 查看特定服务日志
```sh
$ docker-compose -f deployed/docker-compose.yml logs -f web
$ docker-compose -f deployed/docker-compose.yml logs -f celery-worker
$ docker-compose -f deployed/docker-compose.yml logs -f celery-beat
```

###停止所有服务
```sh
$ docker-compose -f deployed/docker-compose.yml down
```