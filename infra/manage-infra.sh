#!/bin/bash
cd "$(dirname "$0")"

case "$1" in
    start)
        echo "启动 Fango 基础设施服务..."
        docker-compose up -d
        ;;
    stop)
        echo "停止 Fango 基础设施服务..."
        docker-compose down
        ;;
    restart)
        echo "重启 Fango 基础设施服务..."
        docker-compose restart
        ;;
    status)
        echo "服务状态:"
        docker-compose ps
        ;;
    logs)
        echo "查看日志:"
        docker-compose logs $2
        ;;
    update)
        echo "更新服务..."
        docker-compose pull
        docker-compose up -d
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs [服务名]|update}"
        exit 1
        ;;
esac