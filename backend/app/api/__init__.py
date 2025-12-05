"""
楚然智考系统 - API路由模块
"""
from fastapi import APIRouter
from app.api import auth, users, questions, exams, imports, statistics

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(questions.router, prefix="/questions", tags=["题库管理"])
api_router.include_router(exams.router, prefix="/exams", tags=["考试管理"])
api_router.include_router(imports.router, prefix="/imports", tags=["题库导入"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["统计分析"])
