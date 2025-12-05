"""
楚然智考系统 - 认证服务
处理用户认证、JWT令牌、验证码等功能
"""
import io
import base64
import random
import string
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User, Role
from app.schemas.auth import TokenData
from app.redis_client import RedisClient


class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session, redis: RedisClient):
        self.db = db
        self.redis = redis
    
    # ==================== 密码处理 ====================
    
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    # ==================== JWT令牌 ====================
    
    def create_access_token(self, user: User) -> Tuple[str, int]:
        """
        创建访问令牌
        返回: (token, expires_in)
        """
        # 获取用户角色和权限
        roles = [role.code for role in user.roles]
        permissions = []
        for role in user.roles:
            for perm in role.permissions:
                if perm.code not in permissions:
                    permissions.append(perm.code)
        
        # 构建令牌数据
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "roles": roles,
            "permissions": permissions,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt, int(expires_delta.total_seconds())
    
    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """解析令牌"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub")
            if user_id is None:
                return None
            
            return TokenData(
                user_id=int(user_id),
                username=payload.get("username"),
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", [])
            )
        except JWTError:
            return None
    
    # ==================== 图形验证码 ====================
    
    async def generate_captcha(self) -> Tuple[str, str]:
        """
        生成图形验证码（4位纯数字）
        返回: (captcha_key, captcha_image_base64)
        """
        # 生成4位纯数字验证码
        code = ''.join(random.choices(string.digits, k=4))
        
        # 生成唯一key
        captcha_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        
        # 创建大尺寸图片，最后再缩小
        width, height = 160, 60
        bg_color = (random.randint(245, 255), random.randint(245, 255), random.randint(245, 255))
        image = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(image)
        
        # 添加少量干扰线
        for _ in range(2):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(200, 200, 200), width=1)
        
        # 定义大号数字的像素图案 (每个数字 12x20 像素)
        digit_patterns = {
            '0': [
                "  ######  ",
                " ##    ## ",
                "##      ##",
                "##      ##",
                "##      ##",
                "##      ##",
                "##      ##",
                "##      ##",
                " ##    ## ",
                "  ######  ",
            ],
            '1': [
                "    ##    ",
                "   ###    ",
                "  # ##    ",
                "    ##    ",
                "    ##    ",
                "    ##    ",
                "    ##    ",
                "    ##    ",
                "    ##    ",
                " ######## ",
            ],
            '2': [
                " ######## ",
                "##      ##",
                "        ##",
                "       ## ",
                "     ##   ",
                "   ##     ",
                " ##       ",
                "##        ",
                "##        ",
                "##########",
            ],
            '3': [
                " ######## ",
                "##      ##",
                "        ##",
                "       ## ",
                "   #####  ",
                "       ## ",
                "        ##",
                "        ##",
                "##      ##",
                " ######## ",
            ],
            '4': [
                "      ##  ",
                "     ###  ",
                "    # ##  ",
                "   #  ##  ",
                "  #   ##  ",
                " #    ##  ",
                "##########",
                "      ##  ",
                "      ##  ",
                "      ##  ",
            ],
            '5': [
                "##########",
                "##        ",
                "##        ",
                "##        ",
                "#######   ",
                "       ## ",
                "        ##",
                "        ##",
                "##      ##",
                " ######## ",
            ],
            '6': [
                "  ######  ",
                " ##       ",
                "##        ",
                "##        ",
                "########  ",
                "##      ##",
                "##      ##",
                "##      ##",
                " ##    ## ",
                "  ######  ",
            ],
            '7': [
                "##########",
                "        ##",
                "       ## ",
                "      ##  ",
                "     ##   ",
                "    ##    ",
                "   ##     ",
                "   ##     ",
                "   ##     ",
                "   ##     ",
            ],
            '8': [
                "  ######  ",
                " ##    ## ",
                "##      ##",
                " ##    ## ",
                "  ######  ",
                " ##    ## ",
                "##      ##",
                "##      ##",
                " ##    ## ",
                "  ######  ",
            ],
            '9': [
                "  ######  ",
                " ##    ## ",
                "##      ##",
                "##      ##",
                " ########",
                "        ##",
                "        ##",
                "       ## ",
                "      ##  ",
                "  ####    ",
            ],
        }
        
        # 绘制每个数字
        for i, char in enumerate(code):
            x_offset = 10 + i * 38
            y_offset = random.randint(5, 15)
            color = (random.randint(20, 80), random.randint(20, 80), random.randint(20, 80))
            
            pattern = digit_patterns.get(char, digit_patterns['0'])
            for row_idx, row in enumerate(pattern):
                for col_idx, pixel in enumerate(row):
                    if pixel == '#':
                        # 绘制2x2像素块使数字更粗
                        px = x_offset + col_idx * 3
                        py = y_offset + row_idx * 4
                        draw.rectangle([px, py, px+2, py+3], fill=color)
        
        # 缩放到目标尺寸
        image = image.resize((120, 40), Image.Resampling.LANCZOS)
        
        # 转换为base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 存储到缓存
        await self.redis.set(
            f"captcha:{captcha_key}",
            code,
            expire=settings.CAPTCHA_EXPIRE_SECONDS
        )
        
        return captcha_key, f"data:image/png;base64,{image_base64}"
    
    async def verify_captcha(self, captcha_key: str, captcha_code: str) -> bool:
        """验证图形验证码"""
        stored_code = await self.redis.get(f"captcha:{captcha_key}")
        if not stored_code:
            return False
        
        # 验证后删除
        await self.redis.delete(f"captcha:{captcha_key}")
        
        return stored_code.lower() == captcha_code.lower()
    
    # ==================== 短信验证码 ====================
    
    async def send_sms_code(self, phone: str) -> Tuple[bool, str]:
        """
        发送短信验证码
        返回: (success, message)
        """
        # 检查发送频率
        last_send_key = f"sms_last:{phone}"
        last_send = await self.redis.get(last_send_key)
        if last_send:
            ttl = await self.redis.ttl(last_send_key)
            return False, f"请{ttl}秒后再试"
        
        # 生成6位验证码
        code = ''.join(random.choices(string.digits, k=6))
        
        # 存储验证码
        await self.redis.set(
            f"sms_code:{phone}",
            code,
            expire=settings.SMS_CODE_EXPIRE_SECONDS
        )
        
        # 记录发送时间
        await self.redis.set(
            last_send_key,
            "1",
            expire=settings.SMS_SEND_INTERVAL
        )
        
        # 调用阿里云短信API（这里简化处理，实际需要集成阿里云SDK）
        try:
            # TODO: 集成阿里云短信SDK
            # from alibabacloud_dysmsapi20170525.client import Client
            # ...
            
            # 开发环境直接打印验证码
            if settings.DEBUG:
                print(f"[DEBUG] 短信验证码 {phone}: {code}")
            
            return True, "验证码发送成功"
        except Exception as e:
            return False, f"发送失败: {str(e)}"
    
    async def verify_sms_code(self, phone: str, code: str) -> bool:
        """验证短信验证码"""
        stored_code = await self.redis.get(f"sms_code:{phone}")
        if not stored_code:
            return False
        
        if stored_code == code:
            # 验证成功后删除
            await self.redis.delete(f"sms_code:{phone}")
            return True
        
        return False
    
    # ==================== 用户认证 ====================
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """通过用户名密码认证"""
        user = self.db.query(User).filter(
            (User.username == username) | (User.phone == username)
        ).first()
        
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        
        return user
    
    def get_user_by_phone(self, phone: str) -> Optional[User]:
        """通过手机号获取用户"""
        return self.db.query(User).filter(User.phone == phone).first()
    
    def update_last_login(self, user: User):
        """更新最后登录时间"""
        user.last_login = datetime.now()
        self.db.commit()
