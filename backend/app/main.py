"""
楚然智考系统 - FastAPI主应用
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import os

from app.config import settings
from app.database import init_db
from app.redis_client import redis_client
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("楚然智考系统启动中...")
    
    # 初始化数据库
    init_db()
    logger.info("数据库初始化完成")
    
    # 连接Redis
    await redis_client.connect()
    logger.info("Redis连接成功")
    
    # 创建上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 初始化默认数据
    await init_default_data()
    
    logger.info("楚然智考系统启动完成")
    
    yield
    
    # 关闭时执行
    await redis_client.disconnect()
    logger.info("楚然智考系统已关闭")


async def init_default_data():
    """初始化默认数据（角色、权限等）"""
    from app.database import SessionLocal
    from app.models.user import User, Role, Permission, UserRole, RolePermission
    from app.models.permission import DEFAULT_ROLE_PERMISSIONS, PERMISSION_DESCRIPTIONS, PermissionCode
    from app.services.auth_service import AuthService
    
    db = SessionLocal()
    
    try:
        # 检查是否已初始化
        if db.query(Role).count() > 0:
            return
        
        logger.info("初始化默认数据...")
        
        # 创建权限
        permissions = {}
        for code, name in PERMISSION_DESCRIPTIONS.items():
            module = code.split(":")[0]
            perm = Permission(
                name=name,
                code=code,
                description=name,
                module=module
            )
            db.add(perm)
            db.flush()
            permissions[code] = perm
        
        # 创建角色
        roles = {}
        role_configs = [
            ("admin", "管理员", "系统管理员，拥有所有权限"),
            ("student", "学员", "普通学员，可参加考试")
        ]
        
        for code, name, desc in role_configs:
            role = Role(name=name, code=code, description=desc)
            db.add(role)
            db.flush()
            roles[code] = role
            
            # 分配权限
            for perm_code in DEFAULT_ROLE_PERMISSIONS.get(code, []):
                if perm_code in permissions:
                    role_perm = RolePermission(
                        role_id=role.id,
                        permission_id=permissions[perm_code].id
                    )
                    db.add(role_perm)
        
        # 创建默认管理员
        from app.core.security import get_password_hash
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            real_name="系统管理员",
            is_superuser=True,
            is_active=True
        )
        db.add(admin_user)
        db.flush()
        
        # 分配管理员角色
        user_role = UserRole(user_id=admin_user.id, role_id=roles["admin"].id)
        db.add(user_role)
        
        db.commit()
        logger.info("默认数据初始化完成")
        logger.info("默认管理员账号: admin / admin123")
        
    except Exception as e:
        db.rollback()
        logger.error(f"初始化默认数据失败: {e}")
    finally:
        db.close()


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="楚然智考系统 - 在线考试平台API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# 静态文件服务
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/", tags=["健康检查"])
async def root():
    """API根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
