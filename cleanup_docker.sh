#!/bin/bash
#
# Docker Cleanup Script
# 提供两种模式：
# 1. safe   -> 只清理构建缓存（builder cache）
# 2. full   -> 清理所有未使用的镜像、容器、卷和网络

set -e

MODE=$1

if [ -z "$MODE" ]; then
    echo "用法: $0 [safe|full]"
    echo "  safe -> 只清理 Docker 构建缓存"
    echo "  full -> 清理未使用的镜像、容器、卷、网络和构建缓存"
    exit 1
fi

if [ "$MODE" == "safe" ]; then
    echo "正在清理 Docker 构建缓存..."
    docker builder prune -af
    echo "安全清理完成！"
elif [ "$MODE" == "full" ]; then
    echo "即将执行彻底清理（未使用的镜像、容器、卷、网络都会删除）"
    read -p "是否继续? (y/N): " CONFIRM
    if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
        docker system prune -a -f --volumes
        echo "彻底清理完成！"
    else
        echo "已取消操作。"
    fi
else
    echo "未知模式: $MODE"
    echo "用法: $0 [safe|full]"
    exit 1
fi
