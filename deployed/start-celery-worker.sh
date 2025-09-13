#!/bin/bash

# 加载环境变量（如果需要在脚本中显式加载）
if [ -f /app/.env ]; then
    export $(cat /app/.env | grep -v '#' | awk '/=/ {print $1}')
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

# 启动 Celery Worker
echo "启动 Celery Worker..."
exec celery -A tasks.celery_app:celery worker --loglevel=info --queues=db_tasks,email_tasks