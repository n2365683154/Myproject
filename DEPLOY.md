# 楚然智考系统 - 宝塔面板 Docker 部署教程

> 本教程适合零基础用户，按步骤操作即可完成部署

## 📋 准备工作

### 1. 服务器要求
- **系统**: CentOS 7/8 或 Ubuntu 18/20/22
- **配置**: 最低 2核4G内存，推荐 4核8G
- **带宽**: 最低 3M，推荐 5M以上
- **已安装**: 宝塔面板

### 2. 端口说明
| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 18080 | 网站访问端口 |
| 后端 | 18000 | API接口端口 |
| MySQL | 13306 | 数据库端口（内部使用） |
| Redis | 16379 | 缓存端口（内部使用） |

---

## 🚀 部署步骤

### 第一步：安装 Docker

1. 登录宝塔面板（通常是 http://服务器IP:8888）

2. 点击左侧菜单 **「软件商店」**

3. 搜索 **「Docker管理器」**，点击 **「安装」**

4. 等待安装完成（约2-5分钟）

5. 安装完成后，点击 **「设置」**，确保 Docker 状态为 **「运行中」**

![安装Docker](https://img.shields.io/badge/状态-运行中-green)

---

### 第二步：上传项目文件

#### 方法A：通过宝塔文件管理器上传（推荐新手）

1. 在本地电脑，将整个项目文件夹打包成 **zip** 格式

2. 登录宝塔面板，点击左侧 **「文件」**

3. 进入目录 `/www/wwwroot/`

4. 点击 **「上传」**，选择刚才打包的 zip 文件

5. 上传完成后，右键点击 zip 文件，选择 **「解压」**

6. 将解压后的文件夹重命名为 `exam-system`

最终目录结构应该是：
```
/www/wwwroot/exam-system/
├── backend/
├── frontend/
├── docker-compose.prod.yml
├── deploy.sh
└── ...
```

#### 方法B：通过 Git 拉取（需要先推送到GitHub）

1. 点击宝塔面板左侧 **「终端」**

2. 输入以下命令：
```bash
cd /www/wwwroot
git clone https://github.com/n2365683154/Myproject.git exam-system
```

---

### 第三步：配置环境变量

1. 在宝塔面板，点击 **「文件」**

2. 进入 `/www/wwwroot/exam-system/` 目录

3. 找到 `.env.production` 文件，右键点击 **「编辑」**

4. 修改以下内容（重要！请更换密码）：

```bash
# 生产环境配置 - 请修改以下密码！

# MySQL配置（请更换为你自己的密码）
MYSQL_ROOT_PASSWORD=你的MySQL管理员密码
MYSQL_PASSWORD=你的MySQL用户密码

# JWT密钥（请更换为随机字符串，可以用键盘随便打一串）
SECRET_KEY=asdfjkl1234567890qwertyuiop

# 允许的跨域来源（填写你的服务器IP或域名）
ALLOWED_ORIGINS=http://你的服务器IP:18080
```

5. 点击 **「保存」**

6. 将文件重命名为 `.env`（去掉 .production）

---

### 第四步：放行防火墙端口

1. 在宝塔面板，点击左侧 **「安全」**

2. 点击 **「防火墙」** 标签

3. 点击 **「添加规则」**，依次添加以下端口：
   - 端口：`18080`，备注：考试系统前端
   - 端口：`18000`，备注：考试系统后端

4. 如果使用的是阿里云/腾讯云，还需要在云服务器控制台的 **「安全组」** 中放行这两个端口

---

### 第五步：启动部署

1. 在宝塔面板，点击左侧 **「终端」**

2. 依次输入以下命令：

```bash
# 进入项目目录
cd /www/wwwroot/exam-system

# 给部署脚本执行权限
chmod +x deploy.sh

# 执行部署（首次部署需要下载镜像，约5-15分钟）
./deploy.sh
```

3. 等待部署完成，看到以下信息表示成功：
```
==========================================
✅ 部署完成！

访问地址：
  - 前端: http://服务器IP:18080
  - 后端API: http://服务器IP:18000
  - API文档: http://服务器IP:18000/docs

默认管理员账号：
  - 用户名: admin
  - 密码: admin123
==========================================
```

---

### 第六步：验证部署

1. 打开浏览器，访问 `http://你的服务器IP:18080`

2. 看到登录页面，使用默认账号登录：
   - 用户名：`admin`
   - 密码：`admin123`

3. **重要：登录后请立即修改管理员密码！**

---

## 🔧 常用运维命令

在宝塔终端中执行（先 `cd /www/wwwroot/exam-system`）：

```bash
# 查看所有容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看实时日志
docker-compose -f docker-compose.prod.yml logs -f

# 只看后端日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 只看前端日志
docker-compose -f docker-compose.prod.yml logs -f frontend

# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启单个服务（如后端）
docker-compose -f docker-compose.prod.yml restart backend

# 停止所有服务
docker-compose -f docker-compose.prod.yml down

# 重新构建并启动（代码更新后使用）
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## ❓ 常见问题

### Q1: 访问网站显示无法连接？

**检查步骤：**
1. 确认容器正在运行：`docker-compose -f docker-compose.prod.yml ps`
2. 确认防火墙已放行端口 18080
3. 确认云服务器安全组已放行端口 18080

### Q2: 登录时提示"登录失败"？

**解决方法：**
1. 查看后端日志：`docker-compose -f docker-compose.prod.yml logs backend`
2. 确认数据库已正常启动
3. 等待1分钟后重试（首次启动数据库初始化需要时间）

### Q3: 如何更新代码？

```bash
cd /www/wwwroot/exam-system

# 如果用Git，先拉取最新代码
git pull

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build
```

### Q4: 如何备份数据？

```bash
cd /www/wwwroot/exam-system

# 备份数据库
docker exec exam_mysql mysqldump -u exam_user -pExamPass@2024 exam_system > backup_$(date +%Y%m%d).sql

# 备份上传的文件
tar -czvf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/
```

### Q5: 如何完全重置系统？

⚠️ **警告：这会删除所有数据！**

```bash
cd /www/wwwroot/exam-system

# 停止并删除所有容器和数据
docker-compose -f docker-compose.prod.yml down -v

# 重新部署
./deploy.sh
```

---

## 🔒 安全建议

1. **修改默认密码**：首次登录后立即修改 admin 密码
2. **修改数据库密码**：在 `.env` 文件中设置强密码
3. **配置HTTPS**：生产环境建议配置SSL证书
4. **定期备份**：建议每天自动备份数据库
5. **限制端口访问**：MySQL和Redis端口不要对外开放

---

## 📞 技术支持

如遇到问题，请检查：
1. Docker 容器日志
2. 防火墙/安全组配置
3. 服务器资源使用情况（内存、磁盘）

祝您部署顺利！🎉
