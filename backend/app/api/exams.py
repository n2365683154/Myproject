"""
楚然智考系统 - 考试管理API路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.exam_service import ExamService
from app.services.question_service import QuestionService
from app.schemas.exam import (
    ExamCreate, ExamUpdate, ExamResponse, ExamListResponse, ExamDetail,
    StartExamResponse, SubmitExamRequest, ExamRecordResponse,
    ExamRecordListResponse, ExamRecordDetail, ExamAnswerDetail,
    WrongQuestionResponse, WrongQuestionListResponse, WrongQuestionUpdate
)
from app.schemas.question import QuestionBrief, QuestionResponse
from app.api.deps import get_current_user, requires_permission
from app.models.user import User
from app.models.exam import RecordStatus
from app.models.permission import PermissionCode
import json


router = APIRouter()


# ==================== 考试管理 ====================

@router.get("", response_model=ExamListResponse, summary="获取考试列表")
async def get_exams(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    exam_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.EXAM_VIEW)
):
    """获取考试列表"""
    exam_service = ExamService(db)
    exams, total = exam_service.get_exams(
        skip=skip,
        limit=limit,
        keyword=keyword,
        exam_type=exam_type,
        status=status
    )
    
    return ExamListResponse(total=total, items=exams)


@router.get("/available", response_model=List[ExamResponse], summary="获取可参加的考试")
async def get_available_exams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户可参加的考试"""
    exam_service = ExamService(db)
    return exam_service.get_available_exams(current_user.id)


@router.get("/{exam_id}", response_model=ExamDetail, summary="获取考试详情")
async def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.EXAM_VIEW)
):
    """获取考试详情（含题目列表）"""
    exam_service = ExamService(db)
    exam = exam_service.get_exam_by_id(exam_id)
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )
    
    # 获取题目列表
    questions = exam_service.generate_exam_questions(exam)
    question_briefs = []
    for q in questions:
        options = None
        if q.options:
            try:
                options = json.loads(q.options)
            except:
                pass
        question_briefs.append(QuestionBrief(
            id=q.id,
            question_type=q.question_type,
            title=q.title,
            options=options,
            score=q.score,
            image_url=q.image_url
        ))
    
    return ExamDetail(
        id=exam.id,
        title=exam.title,
        description=exam.description,
        exam_type=exam.exam_type,
        status=exam.status,
        total_score=exam.total_score,
        pass_score=exam.pass_score,
        duration=exam.duration,
        question_count=exam.question_count,
        is_random=exam.is_random,
        start_time=exam.start_time,
        end_time=exam.end_time,
        allow_review=exam.allow_review,
        show_answer=exam.show_answer,
        max_attempts=exam.max_attempts,
        creator_id=exam.creator_id,
        created_at=exam.created_at,
        updated_at=exam.updated_at,
        questions=question_briefs
    )


@router.post("", response_model=ExamResponse, summary="创建考试")
async def create_exam(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.EXAM_CREATE)
):
    """创建考试"""
    exam_service = ExamService(db)
    exam = exam_service.create_exam(exam_data, current_user.id)
    return exam


@router.put("/{exam_id}", response_model=ExamResponse, summary="更新考试")
async def update_exam(
    exam_id: int,
    exam_data: ExamUpdate,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.EXAM_UPDATE)
):
    """更新考试"""
    exam_service = ExamService(db)
    exam = exam_service.update_exam(exam_id, exam_data)
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )
    
    return exam


@router.delete("/{exam_id}", summary="删除考试")
async def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.EXAM_DELETE)
):
    """删除考试"""
    exam_service = ExamService(db)
    success = exam_service.delete_exam(exam_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )
    
    return {"message": "删除成功"}


@router.post("/{exam_id}/publish", response_model=ExamResponse, summary="发布考试")
async def publish_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.EXAM_PUBLISH)
):
    """发布考试"""
    exam_service = ExamService(db)
    exam = exam_service.publish_exam(exam_id)
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )
    
    return exam


# ==================== 考试流程 ====================

@router.post("/{exam_id}/start", response_model=StartExamResponse, summary="开始考试")
async def start_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.EXAM_TAKE)
):
    """开始考试"""
    exam_service = ExamService(db)
    record, error = exam_service.start_exam(current_user.id, exam_id)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    exam = exam_service.get_exam_by_id(exam_id)
    questions = exam_service.generate_exam_questions(exam)
    
    # 判断是否练习模式
    is_practice = exam.exam_type == 'practice'
    
    # 转换题目格式（练习模式包含答案）
    question_briefs = []
    for q in questions:
        options = None
        if q.options:
            try:
                options = json.loads(q.options)
            except:
                pass
        question_briefs.append(QuestionBrief(
            id=q.id,
            question_type=q.question_type,
            title=q.title,
            options=options,
            score=q.score,
            image_url=q.image_url,
            answer=q.answer if is_practice else None,
            analysis=q.analysis if is_practice else None
        ))
    
    from datetime import timedelta
    end_time = record.start_time + timedelta(minutes=exam.duration)
    
    return StartExamResponse(
        record_id=record.id,
        exam=exam,
        questions=question_briefs,
        start_time=record.start_time,
        end_time=end_time
    )


@router.post("/submit", response_model=ExamRecordResponse, summary="提交考试")
async def submit_exam(
    submit_data: SubmitExamRequest,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.EXAM_TAKE)
):
    """提交考试答案"""
    exam_service = ExamService(db)
    
    # 验证记录属于当前用户
    record = exam_service.get_exam_record_detail(submit_data.record_id)
    if not record or record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此考试记录"
        )
    
    # 转换答案格式
    answers = [{"question_id": a.question_id, "answer": a.answer} for a in submit_data.answers]
    
    record, error = exam_service.submit_exam(submit_data.record_id, answers)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    exam = exam_service.get_exam_by_id(record.exam_id)
    
    return ExamRecordResponse(
        id=record.id,
        user_id=record.user_id,
        exam_id=record.exam_id,
        exam_title=exam.title,
        status=record.status,
        score=record.score,
        correct_count=record.correct_count,
        wrong_count=record.wrong_count,
        unanswered_count=record.unanswered_count,
        accuracy=record.accuracy,
        duration=record.duration,
        is_passed=record.is_passed,
        start_time=record.start_time,
        submit_time=record.submit_time,
        created_at=record.created_at
    )


# ==================== 考试记录 ====================

@router.get("/records/my", response_model=ExamRecordListResponse, summary="我的考试记录")
async def get_my_exam_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的考试记录"""
    exam_service = ExamService(db)
    records, total = exam_service.get_exam_records(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    # 添加考试标题
    items = []
    for record in records:
        exam = exam_service.get_exam_by_id(record.exam_id)
        items.append(ExamRecordResponse(
            id=record.id,
            user_id=record.user_id,
            exam_id=record.exam_id,
            exam_title=exam.title if exam else "",
            status=record.status,
            score=record.score,
            correct_count=record.correct_count,
            wrong_count=record.wrong_count,
            unanswered_count=record.unanswered_count,
            accuracy=record.accuracy,
            duration=record.duration,
            is_passed=record.is_passed,
            start_time=record.start_time,
            submit_time=record.submit_time,
            created_at=record.created_at
        ))
    
    return ExamRecordListResponse(total=total, items=items)


@router.get("/records/{record_id}", response_model=ExamRecordDetail, summary="考试记录详情")
async def get_exam_record_detail(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取考试记录详情（含答题详情）"""
    exam_service = ExamService(db)
    question_service = QuestionService(db)
    
    record = exam_service.get_exam_record_detail(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 验证权限
    if record.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此记录"
        )
    
    exam = exam_service.get_exam_by_id(record.exam_id)
    
    # 获取答题详情
    answer_details = []
    for answer in record.answers:
        question = question_service.get_question_by_id(answer.question_id)
        if question:
            # 处理选项
            options = None
            if question.options:
                try:
                    options = json.loads(question.options)
                except:
                    pass
            
            answer_details.append(ExamAnswerDetail(
                question_id=answer.question_id,
                question=QuestionResponse(
                    id=question.id,
                    question_type=question.question_type,
                    title=question.title,
                    options=options,
                    answer=question.answer,  # 已提交的考试记录始终显示答案
                    analysis=question.analysis,  # 已提交的考试记录始终显示解析
                    difficulty=question.difficulty,
                    score=question.score,
                    image_url=question.image_url,
                    source=question.source,
                    is_active=question.is_active,
                    use_count=question.use_count,
                    correct_count=question.correct_count,
                    creator_id=question.creator_id,
                    created_at=question.created_at,
                    updated_at=question.updated_at,
                    knowledge_points=[]
                ),
                user_answer=answer.user_answer,
                is_correct=answer.is_correct,
                score=answer.score
            ))
    
    return ExamRecordDetail(
        id=record.id,
        user_id=record.user_id,
        exam_id=record.exam_id,
        exam_title=exam.title if exam else "",
        status=record.status,
        score=record.score,
        correct_count=record.correct_count,
        wrong_count=record.wrong_count,
        unanswered_count=record.unanswered_count,
        accuracy=record.accuracy,
        duration=record.duration,
        is_passed=record.is_passed,
        start_time=record.start_time,
        submit_time=record.submit_time,
        created_at=record.created_at,
        answers=answer_details
    )


# ==================== 错题本 ====================

@router.get("/wrong/list", response_model=WrongQuestionListResponse, summary="错题列表")
async def get_wrong_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_mastered: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取错题列表"""
    exam_service = ExamService(db)
    question_service = QuestionService(db)
    
    wrongs, total = exam_service.get_wrong_questions(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_mastered=is_mastered
    )
    
    # 添加题目详情
    items = []
    for wrong in wrongs:
        question = question_service.get_question_by_id(wrong.question_id)
        if question:
            options = None
            if question.options:
                try:
                    options = json.loads(question.options)
                except:
                    pass
            
            items.append(WrongQuestionResponse(
                id=wrong.id,
                user_id=wrong.user_id,
                question_id=wrong.question_id,
                question=QuestionResponse(
                    id=question.id,
                    question_type=question.question_type,
                    title=question.title,
                    options=options,
                    answer=question.answer,
                    analysis=question.analysis,
                    difficulty=question.difficulty,
                    score=question.score,
                    image_url=question.image_url,
                    source=question.source,
                    is_active=question.is_active,
                    use_count=question.use_count,
                    correct_count=question.correct_count,
                    creator_id=question.creator_id,
                    created_at=question.created_at,
                    updated_at=question.updated_at,
                    knowledge_points=[]
                ),
                wrong_count=wrong.wrong_count,
                last_wrong_answer=wrong.last_wrong_answer,
                is_mastered=wrong.is_mastered,
                note=wrong.note,
                created_at=wrong.created_at,
                updated_at=wrong.updated_at
            ))
    
    return WrongQuestionListResponse(total=total, items=items)


@router.put("/wrong/{wrong_id}", summary="更新错题状态")
async def update_wrong_question(
    wrong_id: int,
    update_data: WrongQuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新错题状态（标记已掌握/添加笔记）"""
    exam_service = ExamService(db)
    
    if update_data.is_mastered is not None:
        success = exam_service.mark_mastered(
            current_user.id, 
            wrong_id, 
            update_data.is_mastered
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="错题记录不存在"
            )
    
    return {"message": "更新成功"}
