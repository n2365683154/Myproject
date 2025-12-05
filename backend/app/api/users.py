"""
楚然智考系统 - 用户管理API路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.user_service import UserService
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserPasswordUpdate, RoleCreate, RoleUpdate, RoleResponse,
    PermissionResponse
)
from app.api.deps import get_current_user, requires_permission
from app.models.user import User
from app.models.permission import PermissionCode


router = APIRouter()


# ==================== 用户管理 ====================

@router.get("", response_model=UserListResponse, summary="获取用户列表")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.USER_VIEW)
):
    """获取用户列表（需要用户查看权限）"""
    user_service = UserService(db)
    users, total = user_service.get_users(
        skip=skip,
        limit=limit,
        keyword=keyword,
        role_id=role_id,
        is_active=is_active
    )
    
    return UserListResponse(total=total, items=users)


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户详情")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.USER_VIEW)
):
    """获取用户详情"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


@router.post("", response_model=UserResponse, summary="创建用户")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.USER_CREATE)
):
    """创建用户（需要用户创建权限）"""
    user_service = UserService(db)
    
    # 检查用户名是否存在
    if user_service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查手机号是否存在
    if user_data.phone and user_service.get_user_by_phone(user_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已注册"
        )
    
    user = user_service.create_user(user_data)
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.USER_UPDATE)
):
    """更新用户（需要用户编辑权限）"""
    user_service = UserService(db)
    user = user_service.update_user(user_id, user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.USER_DELETE)
):
    """删除用户（需要用户删除权限）"""
    user_service = UserService(db)
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {"message": "删除成功"}


@router.put("/{user_id}/roles", summary="分配用户角色")
async def assign_user_roles(
    user_id: int,
    role_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.USER_UPDATE)
):
    """分配用户角色"""
    user_service = UserService(db)
    success = user_service.assign_roles(user_id, role_ids)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {"message": "角色分配成功"}


@router.put("/me/password", summary="修改密码")
async def change_password(
    password_data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改当前用户密码"""
    user_service = UserService(db)
    success, message = user_service.change_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"message": message}


@router.put("/me/profile", response_model=UserResponse, summary="更新个人信息")
async def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新当前用户个人信息"""
    user_service = UserService(db)
    
    # 只允许更新部分字段
    allowed_fields = ["email", "phone", "real_name", "gender", "avatar"]
    update_data = user_data.model_dump(exclude_unset=True)
    filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    user = user_service.update_user(current_user.id, UserUpdate(**filtered_data))
    return user


# ==================== 角色管理 ====================

@router.get("/roles/list", response_model=List[RoleResponse], summary="获取角色列表")
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.ROLE_VIEW)
):
    """获取角色列表"""
    user_service = UserService(db)
    roles, _ = user_service.get_roles()
    return roles


@router.post("/roles", response_model=RoleResponse, summary="创建角色")
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.ROLE_CREATE)
):
    """创建角色"""
    user_service = UserService(db)
    role = user_service.create_role(role_data)
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse, summary="更新角色")
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.ROLE_UPDATE)
):
    """更新角色"""
    user_service = UserService(db)
    role = user_service.update_role(role_id, role_data)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return role


@router.delete("/roles/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.ROLE_DELETE)
):
    """删除角色"""
    user_service = UserService(db)
    success = user_service.delete_role(role_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return {"message": "删除成功"}


# ==================== 权限管理 ====================

@router.get("/permissions/list", response_model=List[PermissionResponse], summary="获取权限列表")
async def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.ROLE_VIEW)
):
    """获取所有权限"""
    user_service = UserService(db)
    permissions = user_service.get_permissions()
    return permissions
