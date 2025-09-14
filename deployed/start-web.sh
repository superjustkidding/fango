#!/bin/bash

# 加载环境变量
if [ -f /app/.env ]; then
    export $(cat /app/.env | grep -v '#' | awk '/=/ {print $1}')
fi

# 设置 FLASK_ENV 如果未设置
if [ -z "$FLASK_ENV" ]; then
    export FLASK_ENV=${DEVELOPMENT:-production}
fi

# 等待所有依赖服务就绪
echo "等待MySQL就绪..."
while ! nc -z host.docker.internal 3306; do  # 使用 host.docker.internal 访问宿主机 MySQL
  sleep 0.1
done
echo "MySQL已就绪!"

echo "等待Redis就绪..."
while ! nc -z fango-redis 6379; do  # 使用容器名称
  sleep 0.1
done
echo "Redis已就绪!"

echo "等待RabbitMQ就绪..."
while ! nc -z fango-rabbitmq 5672; do  # 使用容器名称
  sleep 0.1
done
echo "RabbitMQ已就绪!"

echo "等待MongoDB就绪..."
while ! nc -z fango-mongodb 27017; do  # 使用容器名称
  sleep 0.1
done
echo "MongoDB已就绪!"

# 根据不同脚本执行不同操作
if [ "$(basename $0)" = "start-web.sh" ]; then
    # Web 服务特定操作
    echo "运行数据库迁移..."
    flask db upgrade

    echo "创建管理员用户..."
    flask create-admin

    echo "当前环境: $FLASK_ENV"
    if [ "$FLASK_ENV" = "development" ]; then
        echo "启动开发服务器..."
        exec flask run-with-websocket --host=0.0.0.0 --port=5000
    else
        echo "启动生产服务器..."
        exec gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - run:app
    fi
elif [ "$(basename $0)" = "start-celery-worker.sh" ]; then
    # Celery Worker 特定操作
    echo "启动 Celery Worker..."
    echo "当前环境: $FLASK_ENV"
    exec celery -A tasks.celery_app:celery worker --loglevel=info --queues=db_tasks,email_tasks
elif [ "$(basename $0)" = "start-celery-beat.sh" ]; then
    # Celery Beat 特定操作
    echo "启动 Celery Beat..."
    echo "当前环境: $FLASK_ENV"
    exec celery -A tasks.celery_app:celery beat --loglevel=info
fi