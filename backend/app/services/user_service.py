"""
楚然智考系统 - 用户服务
处理用户CRUD、角色管理等功能
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User, Role, Permission, UserRole, RolePermission
from app.schemas.user import UserCreate, UserUpdate, RoleCreate, RoleUpdate
from app.services.auth_service import AuthService


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== 用户管理 ====================
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return self.db.query(User).filter(User.phone == phone).first()
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 20,
        keyword: str = None,
        role_id: int = None,
        is_active: bool = None
    ) -> Tuple[List[User], int]:
        """
        获取用户列表
        返回: (用户列表, 总数)
        """
        query = self.db.query(User)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    User.username.contains(keyword),
                    User.real_name.contains(keyword),
                    User.phone.contains(keyword)
                )
            )
        
        # 角色筛选
        if role_id:
            query = query.join(UserRole).filter(UserRole.role_id == role_id)
        
        # 状态筛选
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        # 加密密码
        hashed_password = AuthService.hash_password(user_data.password)
        
        # 创建用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            hashed_password=hashed_password,
            real_name=user_data.real_name,
            gender=user_data.gender
        )
        
        self.db.add(user)
        self.db.flush()
        
        # 分配角色
        if user_data.role_ids:
            for role_id in user_data.role_ids:
                user_role = UserRole(user_id=user.id, role_id=role_id)
                self.db.add(user_role)
        else:
            # 默认分配学员角色
            student_role = self.db.query(Role).filter(Role.code == "student").first()
            if student_role:
                user_role = UserRole(user_id=user.id, role_id=student_role.id)
                self.db.add(user_role)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """更新用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """修改密码"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        if not AuthService.verify_password(old_password, user.hashed_password):
            return False, "原密码错误"
        
        user.hashed_password = AuthService.hash_password(new_password)
        self.db.commit()
        
        return True, "密码修改成功"
    
    def reset_password(self, phone: str, new_password: str) -> Tuple[bool, str]:
        """重置密码"""
        user = self.get_user_by_phone(phone)
        if not user:
            return False, "用户不存在"
        
        user.hashed_password = AuthService.hash_password(new_password)
        self.db.commit()
        
        return True, "密码重置成功"
    
    def assign_roles(self, user_id: int, role_ids: List[int]) -> bool:
        """分配角色"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # 删除现有角色
        self.db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        
        # 添加新角色
        for role_id in role_ids:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
        
        self.db.commit()
        
        return True
    
    # ==================== 角色管理 ====================
    
    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_roles(self, skip: int = 0, limit: int = 100) -> Tuple[List[Role], int]:
        """获取角色列表"""
        query = self.db.query(Role)
        total = query.count()
        roles = query.offset(skip).limit(limit).all()
        return roles, total
    
    def create_role(self, role_data: RoleCreate) -> Role:
        """创建角色"""
        role = Role(
            name=role_data.name,
            code=role_data.code,
            description=role_data.description
        )
        
        self.db.add(role)
        self.db.flush()
        
        # 分配权限
        if role_data.permission_ids:
            for perm_id in role_data.permission_ids:
                role_perm = RolePermission(role_id=role.id, permission_id=perm_id)
                self.db.add(role_perm)
        
        self.db.commit()
        self.db.refresh(role)
        
        return role
    
    def update_role(self, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        role = self.get_role_by_id(role_id)
        if not role:
            return None
        
        update_data = role_data.model_dump(exclude_unset=True, exclude={"permission_ids"})
        for field, value in update_data.items():
            setattr(role, field, value)
        
        # 更新权限
        if role_data.permission_ids is not None:
            self.db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
            for perm_id in role_data.permission_ids:
                role_perm = RolePermission(role_id=role_id, permission_id=perm_id)
                self.db.add(role_perm)
        
        self.db.commit()
        self.db.refresh(role)
        
        return role
    
    def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        role = self.get_role_by_id(role_id)
        if not role:
            return False
        
        self.db.delete(role)
        self.db.commit()
        
        return True
    
    # ==================== 权限管理 ====================
    
    def get_permissions(self) -> List[Permission]:
        """获取所有权限"""
        return self.db.query(Permission).all()
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户所有权限编码"""
        user = self.get_user_by_id(user_id)
        if not user:
            return []
        
        permissions = []
        for role in user.roles:
            for perm in role.permissions:
                if perm.code not in permissions:
                    permissions.append(perm.code)
        
        return permissions
