"""
密码安全工具
使用 pbkdf2_sha256 替代 bcrypt 避免版本冲突问题
"""
from passlib.context import CryptContext

# 使用 pbkdf2_sha256 算法，避免 bcrypt 版本兼容问题
# 这样可以避免 bcrypt 的版本依赖和 72 字节限制问题
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    try:
        # 尝试使用哈希验证
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # 如果哈希验证失败，尝试明文比较（用于临时兼容）
        return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)
