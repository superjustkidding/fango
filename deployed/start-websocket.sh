#!/bin/bash

# 加载环境变量
if [ -f /app/.env ]; then
    export $(cat /app/.env | grep -v '#' | awk '/=/ {print $1}')
fi

# 设置 FLASK_ENV 如果未设置
if [ -z "$FLASK_ENV" ]; then
    export FLASK_ENV=${FLASK_ENV:-production}
fi

# 设置默认服务地址（使用 Docker 服务名）
MYSQL_HOST=${MYSQL_HOST:-mysql}
MYSQL_PORT=${MYSQL_PORT:-3306}
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}
RABBITMQ_HOST=${RABBITMQ_HOST:-rabbitmq}
RABBITMQ_PORT=${RABBITMQ_PORT:-5672}
MONGODB_HOST=${MONGODB_HOST:-mongodb}
MONGODB_PORT=${MONGODB_PORT:-27017}

# 等待服务就绪的函数
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local timeout=${4:-30}

    echo "等待 $service 就绪 ($host:$port)..."
    local start_time=$(date +%s)

    while ! nc -z $host $port; do
        sleep 1
        local current_time=$(date +%s)
        local elapsed_time=$((current_time - start_time))

        if [ $elapsed_time -ge $timeout ]; then
            echo "$service 在 $timeout 秒内未就绪，跳过等待"
            return 1
        fi
    done

    echo "$service 已就绪!"
    return 0
}

# 等待所有依赖服务就绪
wait_for_service $MYSQL_HOST $MYSQL_PORT "MySQL" 60
wait_for_service $REDIS_HOST $REDIS_PORT "Redis" 30
wait_for_service $RABBITMQ_HOST $RABBITMQ_PORT "RabbitMQ" 30
wait_for_service $MONGODB_HOST $MONGODB_PORT "MongoDB" 30

# 启动 WebSocket 服务
echo "启动 WebSocket 服务..."
echo "当前环境: $FLASK_ENV"
exec flask run-with-websocket --host=0.0.0.0 --port=8000
