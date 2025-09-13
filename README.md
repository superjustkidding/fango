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

### 停止所有服务
```sh
$ docker-compose -f deployed/docker-compose.yml down
```

### 验证定时任务
### 检查 Celery Beat 日志：
```sh
$ docker-compose -f deployed/docker-compose.yml logs -f celery-beat
```

### 检查 Celery Worker 日志：
```sh
$ docker-compose -f deployed/docker-compose.yml logs -f celery-worker
```

### 进入容器手动测试：
###  进入 Celery Worker 容器
```sh
$ docker-compose -f deployed/docker-compose.yml exec celery-worker bash
```

### 在容器内测试任务
```sh
$ python -c "from tasks.db_tasks import update_coupon_status; update_coupon_status()"
```

