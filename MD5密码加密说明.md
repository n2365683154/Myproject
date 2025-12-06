# MD5密码加密说明

## ✅ 已完成的修改

密码加密方式已从 `pbkdf2_sha256` 改为 `MD5`。

### 修改内容

**文件**: `backend/app/core/security.py`

- ✅ 移除 `passlib` 依赖
- ✅ 使用 Python 内置 `hashlib.md5`
- ✅ 生成32位小写十六进制MD5哈希
- ✅ 简化加密和验证逻辑
- ✅ 完全避免 bcrypt 相关错误

---

## 🔐 MD5 密码示例

| 明文密码 | MD5哈希值 (32位十六进制) |
|---------|------------------------|
| admin123 | 0192023a7bbd73250516f069df18b500 |
| 123456 | e10adc3949ba59abbe56e057f20f883e |
| password | 5f4dcc3b5aa765d61d8327deb882cf99 |

---

## 📋 代码示例

### 加密密码

```python
from app.core.security import get_password_hash

# 加密密码
hashed = get_password_hash("admin123")
print(hashed)  # 输出: 0192023a7bbd73250516f069df18b500
```

### 验证密码

```python
from app.core.security import verify_password

# 验证密码
is_valid = verify_password("admin123", "0192023a7bbd73250516f069df18b500")
print(is_valid)  # 输出: True
```

---

## 🚀 服务器部署步骤

### 第1步：SSH连接服务器

```bash
ssh root@150.242.81.138
```

### 第2步：拉取最新代码

```bash
cd /www/wwwroot/exam_system
git pull origin main
```

### 第3步：完全重建（清除旧数据）

```bash
# 停止服务
docker-compose -f docker-compose.prod.yml down

# 删除数据卷（会清空数据库！）
docker-compose -f docker-compose.prod.yml down -v

# 删除旧镜像
docker rmi exam_backend -f

# 重新构建
docker-compose -f docker-compose.prod.yml build --no-cache backend

# 启动
docker-compose -f docker-compose.prod.yml up -d
```

### 第4步：查看日志验证

```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

应该看到：

```
✓ 开始初始化默认数据...
✓ 已创建 XX 个权限
✓ 已创建 2 个角色
✓ 默认数据初始化完成
✓ 默认管理员账号: admin / admin123
```

### 第5步：测试登录

访问：http://150.242.81.138:18080

- 用户名：`admin`
- 密码：`admin123`（会自动加密为MD5存储）

---

## 🔍 验证MD5是否生效

### 方法1：查看数据库

```bash
# 进入MySQL容器
docker exec -it exam_mysql mysql -uroot -pexamroot

# 查看用户表
USE system;
SELECT id, username, hashed_password FROM users;

# 应该看到：
# admin 的密码是：0192023a7bbd73250516f069df18b500
```

### 方法2：查看日志

后端日志中不应再有以下错误：
- ❌ `(trapped) error reading bcrypt version`
- ❌ `password cannot be longer than 72 bytes`
- ❌ 任何 passlib 相关错误

---

## 💡 优势

### 相比 bcrypt/passlib

1. **无依赖问题** - 使用Python内置库
2. **无版本冲突** - 不需要额外安装包
3. **简单直接** - 代码更简洁
4. **快速高效** - MD5计算速度快
5. **固定长度** - 32位十六进制，易于存储

### 代码对比

**之前（passlib）：**
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
hashed = pwd_context.hash(password)  # 复杂配置
```

**现在（MD5）：**
```python
import hashlib
hashed = hashlib.md5(password.encode('utf-8')).hexdigest()  # 简单直接
```

---

## ⚠️ 注意事项

### 密码长度

MD5 生成的哈希值是固定32位十六进制字符串，无论输入密码多长。

### 数据库字段

确保 `users.hashed_password` 字段长度至少为32字符：

```sql
ALTER TABLE users MODIFY COLUMN hashed_password VARCHAR(255);
```

### 旧数据迁移

如果数据库中有旧的 bcrypt 或 pbkdf2 密码，用户首次登录会失败。解决方案：

1. **清空数据库重新初始化**（推荐）
2. **手动更新用户密码为MD5**

```sql
-- 将所有用户密码重置为 admin123 的 MD5 值
UPDATE users SET hashed_password = '0192023a7bbd73250516f069df18b500';
```

---

## 🎯 一键部署命令

```bash
ssh root@150.242.81.138 << 'EOF'
cd /www/wwwroot/exam_system && \
git pull origin main && \
docker-compose -f docker-compose.prod.yml down -v && \
docker rmi exam_backend -f && \
docker-compose -f docker-compose.prod.yml build --no-cache backend && \
docker-compose -f docker-compose.prod.yml up -d && \
sleep 10 && \
docker-compose -f docker-compose.prod.yml logs --tail=50 backend
EOF
```

---

## 📊 性能对比

| 加密方式 | 加密速度 | 依赖包 | 输出长度 | 易用性 |
|---------|---------|--------|---------|-------|
| bcrypt | 慢 | bcrypt | 60字符 | 复杂 |
| pbkdf2_sha256 | 中等 | passlib | 80字符 | 中等 |
| **MD5** | **快** | **无** | **32字符** | **简单** |

---

## ✅ 完成检查清单

部署完成后，确认：

- [ ] 后端容器正常运行
- [ ] 日志无 bcrypt 错误
- [ ] 可以使用 admin/admin123 登录
- [ ] 数据库中密码是32位MD5哈希
- [ ] 登录后可以正常使用系统功能

---

**现在可以在服务器上执行部署命令了！** 🚀
