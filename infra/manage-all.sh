#!/bin/bash

case "$1" in
    start)
        echo "启动所有 Fango 服务..."
        cd infra && ./manage-infra.sh start
        cd ..
        # 这里可以添加启动主应用的命令
        # docker-compose up -d
        echo "请手动启动 Flask 应用: flask run --host=0.0.0.0 --port=5000"
        ;;
    stop)
        echo "停止所有 Fango 服务..."
        # 这里可以添加停止主应用的命令
        # docker-compose down
        cd infra && ./manage-infra.sh stop
        ;;
    restart)
        echo "重启所有 Fango 服务..."
        cd infra && ./manage-infra.sh restart
        cd ..
        # 这里可以添加重启主应用的命令
        # docker-compose restart
        ;;
    status)
        echo "基础设施服务状态:"
        cd infra && ./manage-infra.sh status
        cd ..
        echo ""
        echo "主应用服务状态:"
        # 这里可以添加查看主应用状态的命令
        # docker-compose ps
        echo "请手动检查 Flask 应用状态"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac