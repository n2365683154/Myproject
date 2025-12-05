"""
楚然智考系统 - 认证相关Pydantic模式
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token响应模式"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="过期时间(秒)")


class TokenData(BaseModel):
    """Token数据模式"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []


class LoginRequest(BaseModel):
    """登录请求模式（支持用户名或手机号）"""
    username: str = Field(..., description="用户名或手机号")
    password: str = Field(..., description="密码")
    captcha_key: str = Field(..., description="验证码Key")
    captcha_code: str = Field(..., description="验证码")


class RegisterRequest(BaseModel):
    """注册请求模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号（选填）")
    captcha_key: str = Field(..., description="图形验证码Key")
    captcha_code: str = Field(..., description="图形验证码")


class CaptchaResponse(BaseModel):
    """图形验证码响应模式"""
    captcha_key: str = Field(description="验证码Key")
    captcha_image: str = Field(description="验证码图片Base64")


class SendSmsRequest(BaseModel):
    """发送短信验证码请求模式"""
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    captcha_key: str = Field(..., description="图形验证码Key")
    captcha_code: str = Field(..., description="图形验证码")


class SendSmsResponse(BaseModel):
    """发送短信验证码响应模式"""
    success: bool
    message: str


class ResetPasswordRequest(BaseModel):
    """重置密码请求模式"""
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    sms_code: str = Field(..., min_length=4, max_length=6, description="短信验证码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class UserInfo(BaseModel):
    """当前用户信息模式"""
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    gender: int = 0
    is_superuser: bool = False
    roles: List[str] = []
    permissions: List[str] = []
