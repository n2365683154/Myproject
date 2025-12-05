"""
楚然智考系统 - 题库管理API路由
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.question_service import QuestionService
from app.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionListResponse,
    KnowledgePointCreate, KnowledgePointUpdate, KnowledgePointResponse,
    KnowledgePointTree
)
from app.api.deps import get_current_user, requires_permission
from app.models.user import User
from app.models.permission import PermissionCode


router = APIRouter()


# ==================== 题目管理 ====================

@router.get("", response_model=QuestionListResponse, summary="获取题目列表")
async def get_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    question_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    knowledge_id: Optional[int] = None,
    is_active: Optional[int] = None,
    bank_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.QUESTION_VIEW)
):
    """获取题目列表"""
    question_service = QuestionService(db)
    questions, total = question_service.get_questions(
        skip=skip,
        limit=limit,
        keyword=keyword,
        question_type=question_type,
        difficulty=difficulty,
        knowledge_id=knowledge_id,
        is_active=is_active,
        bank_id=bank_id
    )
    
    # 处理选项JSON
    for q in questions:
        if q.options:
            import json
            try:
                q.options = json.loads(q.options)
            except:
                pass
    
    return QuestionListResponse(total=total, items=questions)


@router.get("/statistics", summary="获取题库统计")
async def get_question_statistics(
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.QUESTION_VIEW)
):
    """获取题库统计信息"""
    question_service = QuestionService(db)
    return question_service.get_question_statistics()


@router.get("/{question_id}", response_model=QuestionResponse, summary="获取题目详情")
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.QUESTION_VIEW)
):
    """获取题目详情"""
    question_service = QuestionService(db)
    question = question_service.get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    # 处理选项JSON
    if question.options:
        import json
        try:
            question.options = json.loads(question.options)
        except:
            pass
    
    return question


@router.post("", response_model=QuestionResponse, summary="创建题目")
async def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.QUESTION_CREATE)
):
    """创建题目"""
    question_service = QuestionService(db)
    question = question_service.create_question(question_data, current_user.id)
    
    # 处理选项JSON
    if question.options:
        import json
        try:
            question.options = json.loads(question.options)
        except:
            pass
    
    return question


@router.post("/batch", summary="批量创建题目")
async def create_questions_batch(
    questions_data: List[QuestionCreate],
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.QUESTION_CREATE)
):
    """批量创建题目"""
    question_service = QuestionService(db)
    questions = question_service.create_questions_batch(questions_data, current_user.id)
    
    return {
        "message": f"成功创建{len(questions)}道题目",
        "count": len(questions)
    }


@router.put("/{question_id}", response_model=QuestionResponse, summary="更新题目")
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.QUESTION_UPDATE)
):
    """更新题目"""
    question_service = QuestionService(db)
    question = question_service.update_question(question_id, question_data)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    # 处理选项JSON
    if question.options:
        import json
        try:
            question.options = json.loads(question.options)
        except:
            pass
    
    return question


@router.delete("/all", summary="删除所有题目")
async def delete_all_questions(
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.QUESTION_DELETE)
):
    """删除所有题目（清空题库）"""
    question_service = QuestionService(db)
    count = question_service.delete_all_questions()
    return {"message": f"已删除{count}道题目", "count": count}


@router.delete("/{question_id}", summary="删除题目")
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.QUESTION_DELETE)
):
    """删除题目"""
    question_service = QuestionService(db)
    success = question_service.delete_question(question_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    return {"message": "删除成功"}


# ==================== 知识点管理 ====================

@router.get("/knowledge/tree", summary="获取知识点树")
async def get_knowledge_tree(
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.KNOWLEDGE_VIEW)
):
    """获取知识点树形结构"""
    question_service = QuestionService(db)
    return question_service.get_knowledge_tree()


@router.get("/knowledge/list", response_model=List[KnowledgePointResponse], summary="获取知识点列表")
async def get_knowledge_points(
    parent_id: Optional[int] = None,
    is_active: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.KNOWLEDGE_VIEW)
):
    """获取知识点列表"""
    question_service = QuestionService(db)
    return question_service.get_knowledge_points(parent_id, is_active)


@router.post("/knowledge", response_model=KnowledgePointResponse, summary="创建知识点")
async def create_knowledge_point(
    kp_data: KnowledgePointCreate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.KNOWLEDGE_CREATE)
):
    """创建知识点"""
    question_service = QuestionService(db)
    return question_service.create_knowledge_point(kp_data)


@router.put("/knowledge/{kp_id}", response_model=KnowledgePointResponse, summary="更新知识点")
async def update_knowledge_point(
    kp_id: int,
    kp_data: KnowledgePointUpdate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.KNOWLEDGE_UPDATE)
):
    """更新知识点"""
    question_service = QuestionService(db)
    kp = question_service.update_knowledge_point(kp_id, kp_data)
    
    if not kp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识点不存在"
        )
    
    return kp


@router.delete("/knowledge/{kp_id}", summary="删除知识点")
async def delete_knowledge_point(
    kp_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.KNOWLEDGE_DELETE)
):
    """删除知识点"""
    question_service = QuestionService(db)
    success = question_service.delete_knowledge_point(kp_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="知识点不存在或存在子节点"
        )
    
    return {"message": "删除成功"}
