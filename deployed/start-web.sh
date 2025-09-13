#!/bin/bash

# 加载环境变量（如果需要在脚本中显式加载）
if [ -f /app/.env ]; then
    export $(cat /app/.env | grep -v '#' | awk '/=/ {print $1}')
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

# 启动应用
echo "启动应用..."
if [ "$FLASK_ENV" = "production" ]; then
    # 生产环境使用 Gunicorn
    exec gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - run:app
else
    # 开发环境使用 Flask 自带服务器
    exec flask run-with-websocket --host=0.0.0.0 --port=5000
fi