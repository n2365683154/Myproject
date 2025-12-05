"""创建或重置管理员账号"""
import bcrypt
from app.database import SessionLocal
from app.models.user import User, Role, UserRole

def hash_password(password: str) -> str:
    """使用bcrypt直接加密密码"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

db = SessionLocal()

try:
    # 检查admin是否存在
    admin = db.query(User).filter(User.username == 'admin').first()
    if admin:
        print('Admin exists, updating password...')
        admin.hashed_password = hash_password('admin123')
        admin.is_active = True
        admin.is_superuser = True
    else:
        print('Creating admin user...')
        admin = User(
            username='admin',
            hashed_password=hash_password('admin123'),
            real_name='系统管理员',
            is_superuser=True,
            is_active=True
        )
        db.add(admin)
        db.flush()
        
        # 分配管理员角色
        admin_role = db.query(Role).filter(Role.code == 'admin').first()
        if admin_role:
            user_role = UserRole(user_id=admin.id, role_id=admin_role.id)
            db.add(user_role)

    db.commit()
    print('Admin account ready: admin / admin123')
except Exception as e:
    db.rollback()
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
