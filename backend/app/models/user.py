"""
楚然智考系统 - 用户相关数据模型
包含：用户表、角色表、权限表、用户角色关联表、角色权限关联表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    gender = Column(Integer, default=0, comment="性别：0未知 1男 2女")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否超级管理员")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    exam_records = relationship("ExamRecord", back_populates="user")
    wrong_questions = relationship("WrongQuestion", back_populates="user")
    study_records = relationship("StudyRecord", back_populates="user")
    
    __table_args__ = (
        Index("idx_user_phone", "phone"),
        Index("idx_user_username", "username"),
        {"comment": "用户表"}
    )


class Role(Base):
    """角色表"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True, comment="角色ID")
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    code = Column(String(50), unique=True, nullable=False, comment="角色编码")
    description = Column(String(255), nullable=True, comment="角色描述")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    
    __table_args__ = (
        {"comment": "角色表"}
    )


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True, comment="权限ID")
    name = Column(String(100), nullable=False, comment="权限名称")
    code = Column(String(100), unique=True, nullable=False, comment="权限编码，如：question:import")
    description = Column(String(255), nullable=True, comment="权限描述")
    module = Column(String(50), nullable=True, comment="所属模块")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    __table_args__ = (
        Index("idx_permission_code", "code"),
        {"comment": "权限表"}
    )


class UserRole(Base):
    """用户角色关联表"""
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, comment="角色ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    __table_args__ = (
        Index("idx_user_role", "user_id", "role_id", unique=True),
        {"comment": "用户角色关联表"}
    )


class RolePermission(Base):
    """角色权限关联表"""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, comment="角色ID")
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, comment="权限ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    __table_args__ = (
        Index("idx_role_permission", "role_id", "permission_id", unique=True),
        {"comment": "角色权限关联表"}
    )
