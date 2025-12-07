"""
楚然智考系统 - 考试相关数据模型
包含：考试表、考试题目表、考试记录表、答题详情表、错题本表、学习记录表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, Enum, Float
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ExamType(str, enum.Enum):
    """考试类型枚举"""
    PRACTICE = "practice"  # 顺序练习
    MOCK = "mock"  # 模拟考试
    FORMAL = "formal"  # 正式考试


class ExamStatus(str, enum.Enum):
    """考试状态枚举"""
    DRAFT = "draft"  # 草稿
    PUBLISHED = "published"  # 已发布
    CLOSED = "closed"  # 已关闭


class RecordStatus(str, enum.Enum):
    """考试记录状态枚举"""
    IN_PROGRESS = "in_progress"  # 进行中
    SUBMITTED = "submitted"  # 已提交
    GRADED = "graded"  # 已判分


class Exam(Base):
    """考试表"""
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True, comment="考试ID")
    title = Column(String(200), nullable=False, comment="考试标题")
    description = Column(Text, nullable=True, comment="考试描述")
    exam_type = Column(
        Enum(ExamType),
        nullable=False,
        default=ExamType.MOCK,
        comment="考试类型"
    )
    status = Column(
        Enum(ExamStatus),
        nullable=False,
        default=ExamStatus.DRAFT,
        comment="考试状态"
    )
    total_score = Column(Integer, default=100, comment="总分")
    pass_score = Column(Integer, default=60, comment="及格分数")
    duration = Column(Integer, default=120, comment="考试时长(分钟)")
    question_count = Column(Integer, default=0, comment="题目数量")
    
    # 组卷策略
    is_random = Column(Integer, default=0, comment="是否随机组卷：0固定 1随机")
    random_config = Column(Text, nullable=True, comment="随机组卷配置JSON")
    random_question_count = Column(Integer, default=0, comment="随机抽题数量，0表示不使用统一随机数量")
    question_type_filter = Column(String(20), default="all", comment="题型过滤: all/single/multiple")
    
    # 时间限制
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    
    # 其他配置
    allow_review = Column(Integer, default=1, comment="是否允许查看解析")
    show_answer = Column(Integer, default=1, comment="交卷后是否显示答案")
    max_attempts = Column(Integer, default=0, comment="最大尝试次数，0表示不限")
    
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    questions = relationship("ExamQuestion", back_populates="exam")
    records = relationship("ExamRecord", back_populates="exam")
    banks = relationship("ExamQuestionBank", back_populates="exam")
    
    __table_args__ = (
        Index("idx_exam_type", "exam_type"),
        Index("idx_exam_status", "status"),
        {"comment": "考试表"}
    )


class ExamQuestion(Base):
    """考试题目关联表"""
    __tablename__ = "exam_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(
        Integer, 
        ForeignKey("exams.id", ondelete="CASCADE"), 
        nullable=False,
        comment="考试ID"
    )
    question_id = Column(
        Integer, 
        ForeignKey("questions.id", ondelete="CASCADE"), 
        nullable=False,
        comment="题目ID"
    )
    sort_order = Column(Integer, default=0, comment="题目顺序")
    score = Column(Integer, default=1, comment="该题分值")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    exam = relationship("Exam", back_populates="questions")
    question = relationship("Question", back_populates="exam_questions")
    
    __table_args__ = (
        Index("idx_exam_question", "exam_id", "question_id"),
        {"comment": "考试题目关联表"}
    )


class ExamQuestionBank(Base):
    """考试与题库关联表"""
    __tablename__ = "exam_question_banks"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(
        Integer,
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        comment="考试ID"
    )
    bank_id = Column(
        Integer,
        ForeignKey("question_banks.id", ondelete="CASCADE"),
        nullable=False,
        comment="题库ID"
    )
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    exam = relationship("Exam", back_populates="banks")
    
    __table_args__ = (
        Index("idx_exam_bank", "exam_id", "bank_id"),
        {"comment": "考试与题库关联表"}
    )


class ExamRecord(Base):
    """考试记录表"""
    __tablename__ = "exam_records"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        comment="用户ID"
    )
    exam_id = Column(
        Integer, 
        ForeignKey("exams.id", ondelete="CASCADE"), 
        nullable=False,
        comment="考试ID"
    )
    status = Column(
        Enum(RecordStatus),
        nullable=False,
        default=RecordStatus.IN_PROGRESS,
        comment="记录状态"
    )
    score = Column(Float, default=0, comment="得分")
    correct_count = Column(Integer, default=0, comment="正确题数")
    wrong_count = Column(Integer, default=0, comment="错误题数")
    unanswered_count = Column(Integer, default=0, comment="未答题数")
    accuracy = Column(Float, default=0, comment="正确率")
    duration = Column(Integer, default=0, comment="实际用时(秒)")
    start_time = Column(DateTime, default=datetime.now, comment="开始时间")
    submit_time = Column(DateTime, nullable=True, comment="提交时间")
    is_passed = Column(Integer, default=0, comment="是否及格")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    user = relationship("User", back_populates="exam_records")
    exam = relationship("Exam", back_populates="records")
    answers = relationship("ExamAnswer", back_populates="record")
    
    __table_args__ = (
        Index("idx_record_user", "user_id"),
        Index("idx_record_exam", "exam_id"),
        Index("idx_record_status", "status"),
        {"comment": "考试记录表"}
    )


class ExamAnswer(Base):
    """答题详情表"""
    __tablename__ = "exam_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(
        Integer, 
        ForeignKey("exam_records.id", ondelete="CASCADE"), 
        nullable=False,
        comment="考试记录ID"
    )
    question_id = Column(
        Integer, 
        ForeignKey("questions.id", ondelete="CASCADE"), 
        nullable=False,
        comment="题目ID"
    )
    user_answer = Column(Text, nullable=True, comment="用户答案")
    is_correct = Column(Integer, default=0, comment="是否正确：0错误 1正确 2部分正确")
    score = Column(Float, default=0, comment="得分")
    answer_time = Column(Integer, default=0, comment="答题用时(秒)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    record = relationship("ExamRecord", back_populates="answers")
    
    __table_args__ = (
        Index("idx_answer_record", "record_id"),
        Index("idx_answer_question", "question_id"),
        {"comment": "答题详情表"}
    )


class WrongQuestion(Base):
    """错题本表"""
    __tablename__ = "wrong_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        comment="用户ID"
    )
    question_id = Column(
        Integer, 
        ForeignKey("questions.id", ondelete="CASCADE"), 
        nullable=False,
        comment="题目ID"
    )
    wrong_count = Column(Integer, default=1, comment="错误次数")
    last_wrong_answer = Column(Text, nullable=True, comment="最近一次错误答案")
    is_mastered = Column(Integer, default=0, comment="是否已掌握")
    note = Column(Text, nullable=True, comment="用户笔记")
    created_at = Column(DateTime, default=datetime.now, comment="首次错误时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="wrong_questions")
    question = relationship("Question", back_populates="wrong_records")
    
    __table_args__ = (
        Index("idx_wrong_user", "user_id"),
        Index("idx_wrong_question", "question_id"),
        Index("idx_wrong_user_question", "user_id", "question_id", unique=True),
        {"comment": "错题本表"}
    )


class StudyRecord(Base):
    """学习记录表"""
    __tablename__ = "study_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        comment="用户ID"
    )
    study_date = Column(DateTime, default=datetime.now, comment="学习日期")
    study_duration = Column(Integer, default=0, comment="学习时长(分钟)")
    question_count = Column(Integer, default=0, comment="练习题数")
    correct_count = Column(Integer, default=0, comment="正确题数")
    exam_count = Column(Integer, default=0, comment="参加考试次数")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="study_records")
    
    __table_args__ = (
        Index("idx_study_user", "user_id"),
        Index("idx_study_date", "study_date"),
        {"comment": "学习记录表"}
    )
