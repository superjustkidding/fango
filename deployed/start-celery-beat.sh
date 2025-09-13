#!/bin/bash

# 加载环境变量
if [ -f /app/.env ]; then
    export $(cat /app/.env | grep -v '#' | awk '/=/ {print $1}')
fi

# 设置 FLASK_ENV 如果未设置
if [ -z "$FLASK_ENV" ]; then
    export FLASK_ENV=${DEVELOPMENT:-development}
fi

# 等待数据库和消息队列就绪
echo "等待数据库就绪..."
while ! nc -z $MYSQL_HOST $MYSQL_PORT; do
  sleep 0.1
done
echo "数据库已就绪!"

echo "等待消息队列就绪..."
# 解析 RabbitMQ 主机和端口
RABBITMQ_HOST=$(echo $CELERY_BROKER_URL | awk -F'[@:/]' '{print $4}')
RABBITMQ_PORT=$(echo $CELERY_BROKER_URL | awk -F'[@:/]' '{print $5}')
RABBITMQ_PORT=${RABBITMQ_PORT:-5672}  # 默认端口

while ! nc -z $RABBITMQ_HOST $RABBITMQ_PORT; do
  sleep 0.1
done
echo "消息队列已就绪!"

# 启动 Celery Beat
echo "启动 Celery Beat..."
echo "当前环境: $FLASK_ENV"
exec celery -A tasks.celery_app:celery beat --loglevel=info