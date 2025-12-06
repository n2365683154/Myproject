#!/bin/bash
# 文件名: deploy-baota.sh
# 用途: 宝塔面板 Docker 一键部署脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 打印标题
print_header() {
  echo ""
  echo -e "${CYAN}========================================${NC}"
  echo -e "${CYAN}  宝塔面板 Docker 一键部署脚本${NC}"
  echo -e "${CYAN}  考试系统 v1.0${NC}"
  echo -e "${CYAN}========================================${NC}"
  echo ""
}

# 检查是否为root用户
check_root() {
  if [ "$EUID" -ne 0 ]; then 
    log_error "请使用 root 用户运行此脚本"
    exit 1
  fi
}

# 检查Docker和Docker Compose
check_docker() {
  log_step "检查 Docker 环境..."
  
  if ! command -v docker &> /dev/null; then
    log_error "Docker 未安装"
    log_info "请先在宝塔面板安装 Docker，或运行: curl -fsSL https://get.docker.com | bash"
    exit 1
  fi
  
  if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose 未安装"
    log_info "正在安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
  fi
  
  log_info "Docker 版本: $(docker --version)"
  log_info "Docker Compose 版本: $(docker-compose --version)"
}

# 检查端口占用
check_ports() {
  log_step "检查端口占用..."
  
  PORTS=(18080 18000 13306 16379)
  PORT_NAMES=("前端" "后端" "MySQL" "Redis")
  
  for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    
    if netstat -tuln | grep -q ":$PORT "; then
      log_warning "端口 $PORT ($NAME) 已被占用"
      read -p "是否继续？可能导致冲突 (y/n): " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
      fi
    else
      log_info "端口 $PORT ($NAME) 可用 ✓"
    fi
  done
}

# 检查环境配置
check_env() {
  log_step "检查环境配置..."
  
  if [ ! -f ".env" ]; then
    log_warning ".env 文件不存在，从模板创建..."
    if [ -f ".env.example" ]; then
      cp .env.example .env
      log_info ".env 文件已创建，请检查配置"
    else
      log_error ".env.example 不存在"
      exit 1
    fi
  else
    log_info ".env 文件已存在 ✓"
  fi
}

# 备份现有数据
backup_data() {
  log_step "备份现有数据..."
  
  BACKUP_DIR="./backups"
  mkdir -p "$BACKUP_DIR"
  
  # 检查是否有运行中的容器
  if docker ps | grep -q "exam_mysql"; then
    log_info "发现运行中的 MySQL 容器，正在备份..."
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
    docker exec exam_mysql mysqldump -u root -pexamroot system > "$BACKUP_FILE" 2>/dev/null || true
    
    if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
      log_info "数据库备份成功: $BACKUP_FILE"
    else
      log_warning "数据库备份失败或无数据"
    fi
  else
    log_info "没有运行中的 MySQL 容器，跳过备份"
  fi
}

# 停止旧容器
stop_old_containers() {
  log_step "停止旧容器..."
  
  if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    log_info "发现运行中的容器，正在停止..."
    docker-compose -f docker-compose.prod.yml down
    log_info "旧容器已停止"
  else
    log_info "没有运行中的容器"
  fi
}

# 清理旧资源
clean_old_resources() {
  log_step "清理旧资源..."
  
  read -p "是否清理旧的 Docker 镜像和数据卷？(y/n): " -n 1 -r
  echo
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_warning "正在清理旧资源（数据库数据将被删除）..."
    docker-compose -f docker-compose.prod.yml down -v
    docker system prune -af --volumes
    log_info "清理完成"
  else
    log_info "跳过清理"
  fi
}

# 构建镜像
build_images() {
  log_step "构建 Docker 镜像..."
  
  log_info "这可能需要几分钟时间，请耐心等待..."
  
  if docker-compose -f docker-compose.prod.yml build --no-cache; then
    log_info "镜像构建成功 ✓"
  else
    log_error "镜像构建失败"
    exit 1
  fi
}

# 启动服务
start_services() {
  log_step "启动服务..."
  
  if docker-compose -f docker-compose.prod.yml up -d; then
    log_info "服务启动成功 ✓"
  else
    log_error "服务启动失败"
    exit 1
  fi
}

# 等待服务就绪
wait_for_services() {
  log_step "等待服务就绪..."
  
  log_info "等待 MySQL 启动..."
  for i in {1..30}; do
    if docker exec exam_mysql mysqladmin ping -h localhost -u root -pexamroot &> /dev/null; then
      log_info "MySQL 已就绪 ✓"
      break
    fi
    echo -n "."
    sleep 2
  done
  echo ""
  
  log_info "等待后端启动..."
  sleep 10
  
  log_info "等待前端启动..."
  sleep 5
}

# 初始化数据
init_data() {
  log_step "初始化系统数据..."
  
  read -p "是否创建管理员账号？(y/n): " -n 1 -r
  echo
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "正在创建管理员账号..."
    
    docker exec -it exam_backend python -c "
from app.database import SessionLocal
from app.models.user import User, Role, UserRole
import datetime

db = SessionLocal()

# 创建管理员角色
admin_role = db.query(Role).filter(Role.code == 'admin').first()
if not admin_role:
    admin_role = Role(
        name='管理员',
        code='admin',
        description='系统管理员',
        is_active=True
    )
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)
    print('✓ 管理员角色创建成功')
else:
    print('✓ 管理员角色已存在')

# 创建管理员用户
admin = db.query(User).filter(User.username == 'admin').first()
if not admin:
    admin = User(
        username='admin',
        hashed_password='admin123',
        email=None,
        phone=None,
        real_name='系统管理员',
        is_active=True,
        is_superuser=True,
        created_at=datetime.datetime.now()
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # 添加角色关联
    user_role = UserRole(
        user_id=admin.id,
        role_id=admin_role.id
    )
    db.add(user_role)
    db.commit()
    print('✓ 管理员账号创建成功')
    print('  用户名: admin')
    print('  密码: admin123')
else:
    print('✓ 管理员账号已存在')

db.close()
" 2>/dev/null || log_warning "管理员创建可能失败，请稍后手动创建"
  fi
}

# 显示服务状态
show_status() {
  log_step "服务状态..."
  
  echo ""
  docker-compose -f docker-compose.prod.yml ps
  echo ""
}

# 显示访问信息
show_access_info() {
  SERVER_IP=$(hostname -I | awk '{print $1}')
  
  echo ""
  echo -e "${CYAN}========================================${NC}"
  echo -e "${CYAN}  部署完成！${NC}"
  echo -e "${CYAN}========================================${NC}"
  echo ""
  echo -e "${GREEN}访问地址：${NC}"
  echo -e "  前端: ${BLUE}http://${SERVER_IP}:18080${NC}"
  echo -e "  后端API: ${BLUE}http://${SERVER_IP}:18000${NC}"
  echo -e "  API文档: ${BLUE}http://${SERVER_IP}:18000/api/docs${NC}"
  echo ""
  echo -e "${GREEN}默认账号：${NC}"
  echo -e "  用户名: ${YELLOW}admin${NC}"
  echo -e "  密码: ${YELLOW}admin123${NC}"
  echo ""
  echo -e "${GREEN}常用命令：${NC}"
  echo -e "  查看状态: ${CYAN}./scripts/manage.sh status${NC}"
  echo -e "  查看日志: ${CYAN}./scripts/manage.sh logs backend${NC}"
  echo -e "  重启服务: ${CYAN}./scripts/manage.sh restart${NC}"
  echo -e "  备份数据: ${CYAN}./scripts/manage.sh backup${NC}"
  echo ""
  echo -e "${GREEN}宝塔面板：${NC}"
  echo -e "  在 Docker → 容器列表 中可以看到所有容器"
  echo -e "  可以直接在面板上管理容器（启动/停止/日志）"
  echo ""
  echo -e "${YELLOW}重要提示：${NC}"
  echo -e "  1. 请及时修改默认密码"
  echo -e "  2. 在宝塔面板的安全设置中开放端口 18080 和 18000"
  echo -e "  3. 建议设置定时任务进行数据备份"
  echo ""
  echo -e "${CYAN}========================================${NC}"
  echo ""
}

# 显示日志
show_logs() {
  read -p "是否查看后端日志？(y/n): " -n 1 -r
  echo
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "后端日志（按 Ctrl+C 退出）："
    docker-compose -f docker-compose.prod.yml logs -f backend
  fi
}

# 主函数
main() {
  print_header
  
  # 检查环境
  check_root
  check_docker
  check_ports
  check_env
  
  # 确认部署
  echo ""
  log_warning "即将开始部署，请确认："
  echo "  - 项目路径: $(pwd)"
  echo "  - 前端端口: 18080"
  echo "  - 后端端口: 18000"
  echo "  - MySQL端口: 13306"
  echo "  - Redis端口: 16379"
  echo ""
  read -p "确认部署？(y/n): " -n 1 -r
  echo
  
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "取消部署"
    exit 0
  fi
  
  # 执行部署
  backup_data
  stop_old_containers
  build_images
  start_services
  wait_for_services
  init_data
  
  # 显示结果
  show_status
  show_access_info
  show_logs
}

# 运行主函数
main "$@"
