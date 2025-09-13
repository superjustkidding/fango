#!/bin/bash

# 加载环境变量
if [ -f /app/.env ]; then
    export $(cat /app/.env | grep -v '#' | awk '/=/ {print $1}')
fi

# 设置 FLASK_ENV 如果未设置
if [ -z "$FLASK_ENV" ]; then
    export FLASK_ENV=${DEVELOPMENT:-development}
fi

# 等待数据库就绪
echo "等待数据库就绪..."
while ! nc -z $MYSQL_HOST $MYSQL_PORT; do
  sleep 0.1
done
echo "数据库已就绪!"

# 运行数据库迁移
echo "运行数据库迁移..."
flask db upgrade

# 创建管理员用户
echo "创建管理员用户..."
flask create-admin

# 根据环境变量选择启动方式
echo "当前环境: $FLASK_ENV"
if [ "$FLASK_ENV" = "development" ]; then
    # 开发环境使用 Flask 自带服务器
    echo "启动开发服务器..."
    exec flask run-with-websocket --host=0.0.0.0 --port=5000
else
    # 生产环境使用 Gunicorn
    echo "启动生产服务器..."
    exec gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - run:app
fi