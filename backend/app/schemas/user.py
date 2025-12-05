"""
楚然智考系统 - 用户相关Pydantic模式
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ==================== 用户模式 ====================

class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    gender: Optional[int] = Field(0, ge=0, le=2, description="性别：0未知 1男 2女")


class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role_ids: Optional[List[int]] = Field(default=[], description="角色ID列表")


class UserUpdate(BaseModel):
    """更新用户模式"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")
    real_name: Optional[str] = Field(None, max_length=50)
    gender: Optional[int] = Field(None, ge=0, le=2)
    avatar: Optional[str] = None
    is_active: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    """修改密码模式"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    avatar: Optional[str] = None
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    roles: List["RoleResponse"] = []
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应模式"""
    total: int
    items: List[UserResponse]


# ==================== 角色模式 ====================

class RoleBase(BaseModel):
    """角色基础模式"""
    name: str = Field(..., max_length=50, description="角色名称")
    code: str = Field(..., max_length=50, description="角色编码")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")


class RoleCreate(RoleBase):
    """创建角色模式"""
    permission_ids: Optional[List[int]] = Field(default=[], description="权限ID列表")


class RoleUpdate(BaseModel):
    """更新角色模式"""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """角色响应模式"""
    id: int
    is_active: bool
    created_at: datetime
    permissions: List["PermissionResponse"] = []
    
    class Config:
        from_attributes = True


# ==================== 权限模式 ====================

class PermissionBase(BaseModel):
    """权限基础模式"""
    name: str = Field(..., max_length=100, description="权限名称")
    code: str = Field(..., max_length=100, description="权限编码")
    description: Optional[str] = Field(None, max_length=255, description="权限描述")
    module: Optional[str] = Field(None, max_length=50, description="所属模块")


class PermissionCreate(PermissionBase):
    """创建权限模式"""
    pass


class PermissionResponse(PermissionBase):
    """权限响应模式"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 解决循环引用
UserResponse.model_rebuild()
RoleResponse.model_rebuild()
