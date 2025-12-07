#!/bin/bash
# 一键部署脚本（不依赖 docker-compose）
# 从 0 到启动 MySQL、Redis、后端、前端

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

log_info "项目路径: $PROJECT_ROOT"

# ==================== 1. 停止并删除旧容器 ====================

log_info "停止并删除旧容器 (exam_backend / exam_frontend / exam_mysql / exam_redis)..."

docker rm -f exam_backend exam_frontend exam_mysql exam_redis 2>/dev/null || true

# ==================== 2. 构建镜像 ====================

log_info "开始构建后端镜像 exam_backend..."

docker build --no-cache -t exam_backend ./backend

log_info "开始构建前端镜像 exam_frontend..."

docker build --no-cache -t exam_frontend ./frontend

# ==================== 3. 启动数据库和缓存 ====================

log_info "启动 MySQL (exam_mysql)..."

docker run -d \
  --name exam_mysql \
  -e MYSQL_ROOT_PASSWORD=examroot \
  -e MYSQL_DATABASE=system \
  -e MYSQL_USER=system \
  -e MYSQL_PASSWORD=examroot \
  -p 13306:3306 \
  mysql:8.0

log_info "启动 Redis (exam_redis)..."

docker run -d \
  --name exam_redis \
  -p 16379:6379 \
  redis:7-alpine

log_info "等待 MySQL / Redis 启动 (30 秒)..."

sleep 30

# ==================== 4. 启动后端 ====================

log_info "启动后端 (exam_backend)..."

docker run -d \
  --name exam_backend \
  --link exam_mysql:mysql \
  --link exam_redis:redis \
  -p 18000:8000 \
  -e DATABASE_URL="mysql+pymysql://system:examroot@mysql:3306/system" \
  -e REDIS_URL="redis://redis:6379/0" \
  exam_backend

# ==================== 5. 启动前端 ====================

log_info "启动前端 (exam_frontend)..."

docker run -d \
  --name exam_frontend \
  --link exam_backend:backend \
  -p 18080:80 \
  exam_frontend

# ==================== 6. 显示状态 ====================

log_info "当前容器状态:"

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep exam_ || true

log_info "后端最近日志:"

docker logs --tail=20 exam_backend || true

log_info "前端最近日志:"

docker logs --tail=20 exam_frontend || true

log_info "部署完成！"
log_info "前端:  http://<服务器IP>:18080"
log_info "后端API文档: http://<服务器IP>:18000/api/docs"
