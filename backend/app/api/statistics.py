"""
楚然智考系统 - 统计分析API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.exam_service import ExamService
from app.schemas.exam import StudyStatistics, StudyTrend
from app.api.deps import get_current_user, requires_permission
from app.models.user import User
from app.models.permission import PermissionCode


router = APIRouter()


@router.get("/study", response_model=StudyStatistics, summary="学习统计")
async def get_study_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的学习统计"""
    exam_service = ExamService(db)
    return exam_service.get_study_statistics(current_user.id)


@router.get("/study/trend", response_model=StudyTrend, summary="学习趋势")
async def get_study_trend(
    days: int = Query(30, ge=7, le=90, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取学习趋势数据"""
    exam_service = ExamService(db)
    return exam_service.get_study_trend(current_user.id, days)


@router.get("/overview", summary="系统概览统计")
async def get_system_overview(
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.STATS_VIEW)
):
    """
    获取系统概览统计（管理员）
    包含：用户数、题目数、考试数、今日活跃等
    """
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from app.models.user import User as UserModel
    from app.models.question import Question
    from app.models.exam import Exam, ExamRecord, StudyRecord
    
    today = datetime.now().date()
    
    # 用户统计
    total_users = db.query(func.count(UserModel.id)).scalar()
    active_users = db.query(func.count(UserModel.id)).filter(
        UserModel.is_active == True
    ).scalar()
    
    # 今日新增用户
    new_users_today = db.query(func.count(UserModel.id)).filter(
        func.date(UserModel.created_at) == today
    ).scalar()
    
    # 题目统计
    total_questions = db.query(func.count(Question.id)).filter(
        Question.is_active == 1
    ).scalar()
    
    # 考试统计
    total_exams = db.query(func.count(Exam.id)).scalar()
    published_exams = db.query(func.count(Exam.id)).filter(
        Exam.status == "published"
    ).scalar()
    
    # 考试记录统计
    total_records = db.query(func.count(ExamRecord.id)).scalar()
    today_records = db.query(func.count(ExamRecord.id)).filter(
        func.date(ExamRecord.created_at) == today
    ).scalar()
    
    # 今日活跃用户
    today_active = db.query(func.count(func.distinct(StudyRecord.user_id))).filter(
        func.date(StudyRecord.study_date) == today
    ).scalar()
    
    # 最近7天趋势
    week_ago = today - timedelta(days=6)
    daily_records = db.query(
        func.date(ExamRecord.created_at).label('date'),
        func.count(ExamRecord.id).label('count')
    ).filter(
        func.date(ExamRecord.created_at) >= week_ago
    ).group_by(
        func.date(ExamRecord.created_at)
    ).all()
    
    # 构建7天数据
    record_trend = {}
    for r in daily_records:
        record_trend[str(r.date)] = r.count
    
    dates = []
    counts = []
    current = week_ago
    while current <= today:
        date_str = str(current)
        dates.append(date_str)
        counts.append(record_trend.get(date_str, 0))
        current += timedelta(days=1)
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "new_today": new_users_today
        },
        "questions": {
            "total": total_questions
        },
        "exams": {
            "total": total_exams,
            "published": published_exams
        },
        "records": {
            "total": total_records,
            "today": today_records
        },
        "today_active_users": today_active,
        "record_trend": {
            "dates": dates,
            "counts": counts
        }
    }


@router.get("/exam/{exam_id}", summary="考试统计")
async def get_exam_statistics(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = requires_permission(PermissionCode.STATS_VIEW)
):
    """
    获取指定考试的统计数据
    包含：参与人数、平均分、及格率、分数分布等
    """
    from sqlalchemy import func
    from app.models.exam import Exam, ExamRecord, RecordStatus
    
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试不存在"
        )
    
    # 基础统计
    records = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam_id,
        ExamRecord.status == RecordStatus.GRADED
    )
    
    total_participants = records.count()
    
    if total_participants == 0:
        return {
            "exam_id": exam_id,
            "exam_title": exam.title,
            "total_participants": 0,
            "average_score": 0,
            "highest_score": 0,
            "lowest_score": 0,
            "pass_rate": 0,
            "average_duration": 0,
            "score_distribution": []
        }
    
    # 分数统计
    stats = db.query(
        func.avg(ExamRecord.score).label('avg_score'),
        func.max(ExamRecord.score).label('max_score'),
        func.min(ExamRecord.score).label('min_score'),
        func.avg(ExamRecord.duration).label('avg_duration'),
        func.sum(ExamRecord.is_passed).label('pass_count')
    ).filter(
        ExamRecord.exam_id == exam_id,
        ExamRecord.status == RecordStatus.GRADED
    ).first()
    
    pass_rate = (stats.pass_count / total_participants * 100) if total_participants > 0 else 0
    
    # 分数分布（按10分一档）
    score_ranges = [
        (0, 60, "0-59"),
        (60, 70, "60-69"),
        (70, 80, "70-79"),
        (80, 90, "80-89"),
        (90, 101, "90-100")
    ]
    
    score_distribution = []
    for low, high, label in score_ranges:
        count = db.query(func.count(ExamRecord.id)).filter(
            ExamRecord.exam_id == exam_id,
            ExamRecord.status == RecordStatus.GRADED,
            ExamRecord.score >= low,
            ExamRecord.score < high
        ).scalar()
        score_distribution.append({
            "range": label,
            "count": count
        })
    
    return {
        "exam_id": exam_id,
        "exam_title": exam.title,
        "total_participants": total_participants,
        "average_score": round(stats.avg_score or 0, 2),
        "highest_score": stats.max_score or 0,
        "lowest_score": stats.min_score or 0,
        "pass_rate": round(pass_rate, 2),
        "average_duration": int(stats.avg_duration or 0),
        "score_distribution": score_distribution
    }
