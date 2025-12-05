#!/bin/bash

# 楚然智考系统 - 宝塔Docker部署脚本

echo "=========================================="
echo "   楚然智考系统 Docker 部署脚本"
echo "=========================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先在宝塔面板安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 复制环境变量文件
if [ ! -f .env ]; then
    cp .env.production .env
    echo "⚠️  已创建 .env 文件，请修改其中的密码配置！"
fi

# 停止旧容器
echo "🔄 停止旧容器..."
docker-compose -f docker-compose.prod.yml down

# 构建并启动
echo "🚀 构建并启动容器..."
docker-compose -f docker-compose.prod.yml up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态："
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo ""
echo "访问地址："
echo "  - 前端: http://服务器IP:18080"
echo "  - 后端API: http://服务器IP:18000"
echo "  - API文档: http://服务器IP:18000/docs"
echo ""
echo "默认管理员账号："
echo "  - 用户名: admin"
echo "  - 密码: admin123"
echo ""
echo "常用命令："
echo "  - 查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo "  - 重启服务: docker-compose -f docker-compose.prod.yml restart"
echo "  - 停止服务: docker-compose -f docker-compose.prod.yml down"
echo "=========================================="
