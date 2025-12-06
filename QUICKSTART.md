# 快速入门指南

## 🚀 5分钟快速部署

### 第1步：环境准备

确保服务器已安装 Docker 和 Docker Compose：

```bash
# 检查 Docker
docker --version

# 检查 Docker Compose
docker-compose --version
```

### 第2步：克隆代码

```bash
# 克隆项目
git clone https://github.com/n2365683154/Myproject.git /www/wwwroot/exam_system
cd /www/wwwroot/exam_system

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件（可选）
```

### 第3步：执行架构重构（首次部署必须）

```bash
# 给脚本添加执行权限
chmod +x scripts/*.sh

# 执行架构重构（自动创建优化后的文件）
./scripts/refactor.sh
```

### 第4步：启动服务

```bash
# 使用管理脚本启动
./scripts/manage.sh start

# 或者手动启动
docker-compose -f docker-compose.prod.yml up -d
```

### 第5步：初始化数据

```bash
# 创建管理员账号
./scripts/manage.sh admin

# 修复验证逻辑（如遇登录问题）
./scripts/manage.sh fix-auth
```

### 第6步：访问系统

- **前端地址**: http://你的服务器IP:18080
- **后端API**: http://你的服务器IP:18000
- **API文档**: http://你的服务器IP:18000/api/docs

默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

---

## 🔧 常用管理命令

### 容器管理

```bash
# 查看状态
./scripts/manage.sh status

# 查看日志
./scripts/manage.sh logs backend    # 查看后端日志
./scripts/manage.sh logs frontend   # 查看前端日志

# 重启服务
./scripts/manage.sh restart

# 重建服务（代码更新后）
./scripts/manage.sh rebuild
```

### 数据管理

```bash
# 备份数据库
./scripts/manage.sh backup

# 进入MySQL容器
docker exec -it exam_mysql mysql -uroot -pexamroot system

# 进入Redis容器
docker exec -it exam_redis redis-cli
```

### 故障排查

```bash
# 查看所有容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看完整日志
docker-compose -f docker-compose.prod.yml logs --tail=100

# 重启单个服务
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 📝 常见问题

### Q1: 登录时提示"用户名或密码错误"

**解决方案**：

```bash
# 方法1：使用管理脚本修复验证逻辑
./scripts/manage.sh fix-auth

# 方法2：重新创建管理员账号
./scripts/manage.sh admin

# 重启后端
./scripts/manage.sh restart
```

### Q2: 前端无法访问后端API

**解决方案**：

```bash
# 检查后端是否正常运行
./scripts/manage.sh logs backend

# 检查端口是否开放
netstat -tulpn | grep 18000

# 检查防火墙设置
firewall-cmd --list-ports
firewall-cmd --add-port=18000/tcp --permanent
firewall-cmd --add-port=18080/tcp --permanent
firewall-cmd --reload
```

### Q3: 多选题判分不正确

**解决方案**：

系统已优化多选题判分逻辑，会自动忽略逗号、空格等符号。如仍有问题：

```bash
# 重新部署优化后的代码
./scripts/manage.sh rebuild

# 强制刷新浏览器缓存
# 按 Ctrl+Shift+R 或 Ctrl+F5
```

### Q4: 数据库连接失败

**解决方案**：

```bash
# 检查MySQL容器状态
docker ps | grep mysql

# 查看MySQL日志
docker logs exam_mysql

# 进入MySQL容器检查
docker exec -it exam_mysql mysql -uroot -pexamroot

# 重启MySQL
docker-compose -f docker-compose.prod.yml restart mysql
```

### Q5: 验证码不显示

**解决方案**：

```bash
# 检查后端日志
./scripts/manage.sh logs backend | grep captcha

# 重启后端服务
./scripts/manage.sh restart

# 检查Redis是否正常
docker exec -it exam_redis redis-cli ping
```

---

## 🔄 代码更新流程

### 1. 本地开发完成后

```bash
# 提交代码
git add .
git commit -m "描述你的修改"
git push origin main
```

### 2. 服务器更新代码

```bash
# 进入项目目录
cd /www/wwwroot/exam_system

# 拉取最新代码
git pull origin main

# 如果有代码冲突，备份后强制更新
git fetch origin
git reset --hard origin/main

# 重建并启动服务
./scripts/manage.sh rebuild
```

---

## 📊 性能优化建议

### 1. 定期备份数据

```bash
# 添加定时任务
crontab -e

# 每天凌晨3点备份
0 3 * * * cd /www/wwwroot/exam_system && ./scripts/manage.sh backup
```

### 2. 清理日志文件

```bash
# 清理Docker日志
docker system prune -a --volumes -f

# 保留最近7天的备份
find /www/wwwroot/exam_system -name "exam_backup_*.sql" -mtime +7 -delete
```

### 3. 监控资源使用

```bash
# 查看容器资源占用
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

---

## 🎓 学习资源

- **项目文档**: [docs/](./docs/)
- **API文档**: http://服务器IP:18000/api/docs
- **开发指南**: [docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md)
- **部署指南**: [docs/DEPLOY.md](./docs/DEPLOY.md)

---

## 💡 最佳实践

1. **使用管理脚本**：优先使用 `./scripts/manage.sh` 进行日常操作
2. **定期备份**：在重大操作前执行 `./scripts/manage.sh backup`
3. **查看日志**：出现问题时首先查看日志定位原因
4. **环境隔离**：开发环境和生产环境使用不同的配置文件
5. **安全第一**：及时修改默认密码和密钥

---

## 📞 获取帮助

遇到问题时：

1. 查看项目文档
2. 查看日志文件
3. 搜索常见问题
4. 提交 GitHub Issue

祝您使用愉快！🎉
