"""
楚然智考系统 - 认证API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.redis_client import get_redis, RedisClient
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.auth import (
    Token, LoginRequest, RegisterRequest,
    CaptchaResponse, SendSmsRequest, SendSmsResponse,
    ResetPasswordRequest, UserInfo
)
from app.schemas.user import UserCreate
from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter()


@router.get("/captcha", response_model=CaptchaResponse, summary="获取图形验证码")
async def get_captcha(
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis)
):
    """
    获取图形验证码
    返回验证码Key和Base64图片
    """
    try:
        auth_service = AuthService(db, redis)
        captcha_key, captcha_image = await auth_service.generate_captcha()
        
        return CaptchaResponse(
            captcha_key=captcha_key,
            captcha_image=captcha_image
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sms/send", response_model=SendSmsResponse, summary="发送短信验证码")
async def send_sms_code(
    request: SendSmsRequest,
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis)
):
    """
    发送短信验证码
    需要先验证图形验证码
    """
    auth_service = AuthService(db, redis)
    
    # 验证图形验证码
    if not await auth_service.verify_captcha(request.captcha_key, request.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图形验证码错误"
        )
    
    # 发送短信
    success, message = await auth_service.send_sms_code(request.phone)
    
    return SendSmsResponse(success=success, message=message)


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis)
):
    """
    用户登录（支持用户名或手机号 + 密码）
    需要验证图形验证码
    """
    auth_service = AuthService(db, redis)
    user_service = UserService(db)
    
    # 验证图形验证码
    if not await auth_service.verify_captcha(request.captcha_key, request.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图形验证码错误"
        )
    
    # 尝试用户名登录
    user = auth_service.authenticate_user(request.username, request.password)
    
    # 如果用户名登录失败，尝试手机号登录
    if not user:
        user = user_service.get_user_by_phone(request.username)
        if user and not auth_service.verify_password(request.password, user.hashed_password):
            user = None
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/手机号或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 更新登录时间
    auth_service.update_last_login(user)
    
    # 生成Token
    access_token, expires_in = auth_service.create_access_token(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in
    )


@router.post("/register", summary="用户注册")
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis)
):
    """
    用户注册
    需要验证图形验证码
    """
    auth_service = AuthService(db, redis)
    user_service = UserService(db)
    
    # 验证图形验证码
    if not await auth_service.verify_captcha(request.captcha_key, request.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图形验证码错误"
        )
    
    # 检查用户名是否存在
    if user_service.get_user_by_username(request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查手机号是否存在（如果提供了手机号）
    if request.phone and user_service.get_user_by_phone(request.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已注册"
        )
    
    # 创建用户
    user_data = UserCreate(
        username=request.username,
        password=request.password,
        phone=request.phone
    )
    user = user_service.create_user(user_data)
    
    return {"message": "注册成功"}


@router.post("/password/reset", summary="重置密码")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis)
):
    """
    通过短信验证码重置密码
    """
    auth_service = AuthService(db, redis)
    user_service = UserService(db)
    
    # 验证短信验证码
    if not await auth_service.verify_sms_code(request.phone, request.sms_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="短信验证码错误或已过期"
        )
    
    # 重置密码
    success, message = user_service.reset_password(request.phone, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"message": message}


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户信息
    """
    user_service = UserService(db)
    permissions = user_service.get_user_permissions(current_user.id)
    roles = [role.code for role in current_user.roles]
    
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        real_name=current_user.real_name,
        avatar=current_user.avatar,
        gender=current_user.gender,
        is_superuser=current_user.is_superuser,
        roles=roles,
        permissions=permissions
    )
