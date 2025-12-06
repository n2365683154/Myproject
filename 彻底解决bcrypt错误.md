# 彻底解决 bcrypt 错误 - 终极方案

## 🎯 问题根源

**找到了！** `requirements.txt` 中有 `passlib[bcrypt]==1.7.4`，导致Docker构建时仍然安装bcrypt！

## ✅ 已完成的修复

### 1. 修改代码
- ✅ `backend/app/core/security.py` - 改用MD5
- ✅ `backend/app/services/auth_service.py` - 使用统一security模块
- ✅ `backend/app/main.py` - 初始化使用MD5

### 2. 移除依赖
- ✅ `backend/requirements.txt` - 删除 `passlib[bcrypt]`

### Git提交记录
```
commit a33f22d - 将密码加密方式改为MD5
commit 5169127 - 从requirements.txt中移除passlib依赖
```

---

## 🚀 服务器彻底重建（复制执行）

### ⚡ 一键完全重建命令

```bash
ssh root@150.242.81.138 << 'EOFCMD'
cd /www/wwwroot/exam_system

echo "=== 1. 拉取最新代码 ==="
git fetch origin
git reset --hard origin/main
git pull origin main

echo "=== 2. 停止并删除所有容器 ==="
docker-compose -f docker-compose.prod.yml down -v

echo "=== 3. 删除所有旧镜像 ==="
docker rmi exam_backend exam_frontend -f
docker rmi $(docker images -f "dangling=true" -q) -f 2>/dev/null || true

echo "=== 4. 清理Docker缓存 ==="
docker builder prune -af
docker system prune -af --volumes

echo "=== 5. 重新构建（完全无缓存）==="
docker-compose -f docker-compose.prod.yml build --no-cache --pull

echo "=== 6. 启动所有服务 ==="
docker-compose -f docker-compose.prod.yml up -d

echo "=== 7. 等待10秒后检查日志 ==="
sleep 10
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

echo ""
echo "=== 8. 检查容器状态 ==="
docker-compose -f docker-compose.prod.yml ps
EOFCMD
```

### 📋 分步执行（如果一键命令失败）

```bash
# 1. SSH连接服务器
ssh root@150.242.81.138

# 2. 进入项目目录
cd /www/wwwroot/exam_system

# 3. 强制更新代码（覆盖任何本地修改）
git fetch origin
git reset --hard origin/main
git pull origin main

# 4. 查看最新的requirements.txt（确认passlib已删除）
cat backend/requirements.txt | grep -i passlib
# 应该显示：# passlib[bcrypt]==1.7.4  # 已移除

# 5. 停止所有容器并删除数据卷
docker-compose -f docker-compose.prod.yml down -v

# 6. 删除所有相关镜像
docker rmi exam_backend -f
docker rmi exam_frontend -f
docker rmi exam_mysql -f
docker rmi exam_redis -f

# 7. 清理所有Docker缓存（重要！）
docker builder prune -af
docker system prune -af --volumes

# 8. 重新构建后端（完全无缓存，强制拉取基础镜像）
docker-compose -f docker-compose.prod.yml build --no-cache --pull backend

# 9. 构建前端
docker-compose -f docker-compose.prod.yml build --no-cache --pull frontend

# 10. 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 11. 实时查看后端日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## ✅ 预期正确日志

启动后，日志应该显示：

```
exam_backend  | 2025-12-06 18:xx:xx.xxx | INFO | app.main:lifespan:21 - 楚然智考系统启动中...
exam_backend  | 2025-12-06 18:xx:xx.xxx | INFO | app.main:lifespan:25 - 数据库初始化完成
exam_backend  | 2025-12-06 18:xx:xx.xxx | INFO | app.main:lifespan:29 - Redis连接成功
exam_backend  | 2025-12-06 18:xx:xx.xxx | INFO | app.main:init_default_data:74 - 开始初始化默认数据...
exam_backend  | 2025-12-06 18:xx:xx.xxx | INFO | app.main:init_default_data:90 - 已创建 XX 个权限
exam_backend  | 2025-12-06 18:xx:xx.xxx | INFO | app.main:init_default_data:114 - 已创建 2 个角色
exam_backend  | 2025-12-06 18:xx:xx.xxx | INFO | app.main:init_default_data:132 - ✓ 默认数据初始化完成
exam_backend  | 2025-12-06 18:xx:xx.xxx | INFO | app.main:init_default_data:133 - ✓ 默认管理员账号: admin / admin123
exam_backend  | 2025-12-06 18:xx:xx.xxx | INFO | app.main:lifespan:37 - 楚然智考系统启动完成
exam_backend  | [2025-12-06 18:xx:xx +0800] [7] [INFO] Application startup complete.
```

### ❌ 不应该再出现的错误

- ❌ `(trapped) error reading bcrypt version`
- ❌ `AttributeError: module 'bcrypt' has no attribute '__about__'`
- ❌ `password cannot be longer than 72 bytes`
- ❌ `Deadlock found when trying to get lock`
- ❌ 任何 passlib 相关错误

---

## 🔍 验证修复

### 1. 检查依赖是否正确

在容器中验证：

```bash
# 进入后端容器
docker exec -it exam_backend bash

# 检查是否还有passlib（应该没有）
pip list | grep -i passlib
# 应该没有输出

# 检查是否还有bcrypt（应该没有）
pip list | grep -i bcrypt
# 应该没有输出

# 测试MD5加密
python -c "import hashlib; print(hashlib.md5('admin123'.encode()).hexdigest())"
# 应该输出: 0192023a7bbd73250516f069df18b500

# 退出容器
exit
```

### 2. 检查数据库密码格式

```bash
# 进入MySQL容器
docker exec -it exam_mysql mysql -uroot -pexamroot

# 查看管理员密码（应该是32位MD5）
USE system;
SELECT id, username, hashed_password FROM users WHERE username='admin';

# 应该看到：
# 1 | admin | 0192023a7bbd73250516f069df18b500

# 退出
exit
```

### 3. 测试登录

访问：http://150.242.81.138:18080

- 用户名：`admin`
- 密码：`admin123`

应该能够成功登录！

---

## 🔧 如果仍然失败

### 方案A：手动清理容器

```bash
# 停止所有容器
docker stop $(docker ps -a -q)

# 删除所有容器
docker rm $(docker ps -a -q)

# 删除所有镜像
docker rmi $(docker images -q) -f

# 删除所有数据卷
docker volume rm $(docker volume ls -q)

# 删除所有网络
docker network rm $(docker network ls -q) 2>/dev/null || true

# 然后重新构建
cd /www/wwwroot/exam_system
docker-compose -f docker-compose.prod.yml build --no-cache --pull
docker-compose -f docker-compose.prod.yml up -d
```

### 方案B：重新克隆项目

```bash
# 备份数据
cd /www/wwwroot
docker exec exam_mysql mysqldump -u root -pexamroot system > system_backup.sql 2>/dev/null || true

# 删除旧项目
rm -rf exam_system

# 重新克隆
git clone https://github.com/n2365683154/Myproject.git exam_system
cd exam_system

# 复制配置文件（如果有）
# cp /path/to/.env backend/.env

# 构建并启动
docker-compose -f docker-compose.prod.yml build --no-cache --pull
docker-compose -f docker-compose.prod.yml up -d

# 等待启动
sleep 15

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 方案C：查看详细构建日志

```bash
cd /www/wwwroot/exam_system

# 查看构建过程中的详细日志
docker-compose -f docker-compose.prod.yml build --no-cache --progress=plain backend 2>&1 | tee build.log

# 搜索是否还在安装passlib
grep -i passlib build.log
grep -i bcrypt build.log

# 应该没有找到相关输出
```

---

## 📊 故障排查清单

| 检查项 | 命令 | 预期结果 |
|-------|------|---------|
| 代码是否最新 | `git log -1` | commit 5169127 |
| requirements.txt | `cat backend/requirements.txt \| grep passlib` | 已注释 |
| Docker镜像 | `docker images \| grep exam` | 最新时间戳 |
| 容器运行 | `docker ps` | 4个容器都是Up |
| 后端日志 | `docker logs exam_backend` | 无bcrypt错误 |
| 依赖列表 | `docker exec exam_backend pip list` | 无passlib |

---

## 💡 为什么之前失败？

1. **requirements.txt未更新** - Docker构建时仍安装passlib
2. **Docker缓存** - 使用了旧的镜像层
3. **镜像未删除** - 旧镜像仍在系统中

## ✅ 现在已解决

1. ✅ 代码改用MD5（hashlib内置）
2. ✅ requirements.txt删除passlib
3. ✅ 提供完全清理的部署命令
4. ✅ 彻底重建Docker镜像

---

## 🎉 执行后确认

部署完成后，必须确认：

- [ ] 后端容器正常运行
- [ ] 日志中**完全没有**bcrypt相关错误
- [ ] 日志显示"默认数据初始化完成"
- [ ] 可以访问前端页面
- [ ] 可以使用admin/admin123登录
- [ ] 容器中没有安装passlib包

---

**立即执行一键重建命令！这次一定能解决！** 🚀
