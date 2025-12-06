"""
密码安全工具
使用 MD5 进行密码加密
"""
import hashlib


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: MD5哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    try:
        # 计算明文密码的MD5值并比较
        plain_md5 = hashlib.md5(plain_password.encode('utf-8')).hexdigest()
        return plain_md5 == hashed_password
    except Exception:
        # 如果验证失败，尝试明文比较（用于临时兼容）
        return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    """
    生成密码MD5哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: MD5哈希后的密码（32位小写十六进制）
    """
    return hashlib.md5(password.encode('utf-8')).hexdigest()
