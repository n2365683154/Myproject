"""
楚然智考系统 - API依赖注入模块
"""
from typing import Optional, List
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.redis_client import get_redis, RedisClient
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import TokenData


# Bearer Token认证
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    从JWT Token中解析用户信息
    """
    token = credentials.credentials
    token_data = AuthService.decode_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前超级管理员"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    return current_user


def get_token_data(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """获取Token数据"""
    token = credentials.credentials
    token_data = AuthService.decode_token(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )
    
    return token_data


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    def __call__(
        self,
        token_data: TokenData = Depends(get_token_data),
        current_user: User = Depends(get_current_user)
    ) -> User:
        # 超级管理员跳过权限检查
        if current_user.is_superuser:
            return current_user
        
        # 检查是否拥有所需权限
        user_permissions = token_data.permissions
        for perm in self.required_permissions:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少权限: {perm}"
                )
        
        return current_user


def requires_permission(*permissions: str):
    """
    权限装饰器
    用法: @requires_permission("question:create", "question:update")
    """
    return Depends(PermissionChecker(list(permissions)))


def requires_any_permission(*permissions: str):
    """
    任一权限装饰器
    只需要拥有其中一个权限即可
    """
    class AnyPermissionChecker:
        def __call__(
            self,
            token_data: TokenData = Depends(get_token_data),
            current_user: User = Depends(get_current_user)
        ) -> User:
            if current_user.is_superuser:
                return current_user
            
            user_permissions = token_data.permissions
            for perm in permissions:
                if perm in user_permissions:
                    return current_user
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {', '.join(permissions)}"
            )
    
    return Depends(AnyPermissionChecker())
