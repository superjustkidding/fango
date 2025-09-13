#!/bin/bash

# 等待数据库和消息队列就绪
echo "等待数据库就绪..."
while ! nc -z $MYSQL_HOST $MYSQL_PORT; do
  sleep 0.1
done
echo "数据库已就绪!"

echo "等待消息队列就绪..."
while ! nc -z $(echo $CELERY_BROKER_URL | awk -F'[@:/]' '{print $4}') $(echo $CELERY_BROKER_URL | awk -F'[@:/]' '{print $5}'); do
  sleep 0.1
done
echo "消息队列已就绪!"

# 启动 Celery Beat
echo "启动 Celery Beat..."
exec celery -A tasks.celery_app:celery beat --loglevel=info