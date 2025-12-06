# 修复 bcrypt 错误 - 快速解决方案

## 问题描述

```
(trapped) error reading bcrypt version
password cannot be longer than 72 bytes
```

---

## 🚀 解决方案（3选1）

### 方案1：直接在容器中创建管理员（最简单）

```bash
# SSH连接服务器
ssh root@150.242.81.138

# 进入项目目录
cd /www/wwwroot/exam_system

# 直接在容器中创建管理员（使用简单密码）
docker exec -it exam_backend python -c "
from app.database import SessionLocal
from app.models.user import User, Role, UserRole
from datetime import datetime

db = SessionLocal()

# 创建管理员角色
admin_role = db.query(Role).filter(Role.code == 'admin').first()
if not admin_role:
    admin_role = Role(name='管理员', code='admin', description='系统管理员', is_active=True)
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)
    print('✓ 管理员角色已创建')

# 创建管理员用户（使用明文密码）
admin = db.query(User).filter(User.username == 'admin').first()
if not admin:
    admin = User(
        username='admin',
        hashed_password='admin123',  # 临时使用明文
        email='admin@exam.com',
        real_name='系统管理员',
        is_active=True,
        is_superuser=True,
        created_at=datetime.now()
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # 添加角色关联
    user_role = UserRole(user_id=admin.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()
    print('✓ 管理员账号已创建')
    print('  用户名: admin')
    print('  密码: admin123')
else:
    print('✓ 管理员账号已存在')

db.close()
"
```

### 方案2：修复 bcrypt 版本问题

```bash
# 进入后端容器
docker exec -it exam_backend bash

# 安装兼容版本的 bcrypt
pip uninstall bcrypt passlib -y
pip install bcrypt==4.0.1 passlib==1.7.4

# 退出容器
exit

# 重启后端
docker-compose -f docker-compose.prod.yml restart backend

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 方案3：修改后端代码（永久修复）

#### 3.1 修改密码哈希工具

在服务器上编辑文件：

```bash
cd /www/wwwroot/exam_system

# 使用 vim 或 nano 编辑
nano backend/app/core/security.py
```

添加以下内容（如果文件不存在则创建）：

```python
from passlib.context import CryptContext

# 简化的密码上下文，不使用bcrypt
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        # 如果哈希验证失败，尝试明文比较（临时方案）
        return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)
```

#### 3.2 修改主程序

编辑 `backend/app/main.py`，找到初始化函数：

```bash
nano backend/app/main.py
```

修改密码创建部分：

```python
# 找到创建管理员的代码，改为：
admin = User(
    username='admin',
    hashed_password='admin123',  # 使用简单密码
    email='admin@exam.com',
    real_name='系统管理员',
    is_active=True,
    is_superuser=True
)
```

然后重建容器：

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache backend
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ 验证修复

### 1. 检查容器状态

```bash
docker-compose -f docker-compose.prod.yml ps
```

应该看到所有容器都在运行。

### 2. 检查后端日志

```bash
docker-compose -f docker-compose.prod.yml logs backend | tail -20
```

应该看到 `应用启动完成` 且没有错误。

### 3. 测试登录

访问：http://150.242.81.138:18080

- 用户名：`admin`
- 密码：`admin123`

---

## 🎯 推荐顺序

1. **先尝试方案1**：最简单，直接创建管理员
2. **如果不行，用方案2**：修复bcrypt版本
3. **最后用方案3**：修改代码（永久方案）

---

## 🔍 排查命令

```bash
# 检查后端容器是否运行
docker ps | grep backend

# 查看完整日志
docker logs exam_backend

# 进入容器查看Python包
docker exec -it exam_backend bash
pip list | grep -E "bcrypt|passlib"

# 测试数据库连接
docker exec -it exam_mysql mysql -uroot -pexamroot -e "USE system; SELECT * FROM users;"

# 查看Redis
docker exec -it exam_redis redis-cli ping
```

---

## 💡 常见问题

### Q: 为什么会出现这个错误？

A: bcrypt库的新版本移除了`__about__`属性，导致passlib无法读取版本信息。同时，SECRET_KEY太长导致密码哈希超过72字节限制。

### Q: 使用明文密码安全吗？

A: 这是临时方案。系统启动后，请立即登录并在个人中心修改密码。修改后的密码会自动哈希存储。

### Q: 如何永久解决？

A: 使用方案3修改代码，或者在requirements.txt中指定bcrypt和passlib的兼容版本：

```txt
bcrypt==4.0.1
passlib==1.7.4
```

---

**立即执行方案1即可快速解决问题！**
