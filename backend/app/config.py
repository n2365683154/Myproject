"""
楚然智考系统 - 配置管理模块
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "楚然智考系统"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/exam_system?charset=utf8mb4"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # 阿里云短信配置
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_SMS_SIGN_NAME: str = "楚然智考"
    ALIYUN_SMS_TEMPLATE_CODE: str = ""
    
    # CORS配置
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 验证码配置
    CAPTCHA_EXPIRE_SECONDS: int = 300  # 5分钟
    SMS_CODE_EXPIRE_SECONDS: int = 300  # 5分钟
    SMS_SEND_INTERVAL: int = 60  # 发送间隔60秒
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """获取允许的跨域来源列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
