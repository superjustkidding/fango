# 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=app/__init__.py
ENV FLASK_ENV=production

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 复制启动脚本
COPY deployed/start-web.sh /start-web.sh
COPY deployed/start-celery-worker.sh /start-celery-worker.sh
COPY deployed/start-celery-beat.sh /start-celery-beat.sh

# 设置脚本权限
RUN chmod +x /start-web.sh /start-celery-worker.sh /start-celery-beat.sh

# 暴露端口
EXPOSE 5000

# 默认启动 Web 服务
CMD ["/start-web.sh"]