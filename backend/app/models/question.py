"""
楚然智考系统 - 题库相关数据模型
包含：题目表、知识点表、题目知识点关联表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class QuestionType(str, enum.Enum):
    """题目类型枚举"""
    SINGLE_CHOICE = "single_choice"  # 单选题
    MULTIPLE_CHOICE = "multiple_choice"  # 多选题
    TRUE_FALSE = "true_false"  # 判断题
    FILL_BLANK = "fill_blank"  # 填空题
    SHORT_ANSWER = "short_answer"  # 简答题


class DifficultyLevel(str, enum.Enum):
    """难度等级枚举"""
    EASY = "easy"  # 简单
    MEDIUM = "medium"  # 中等
    HARD = "hard"  # 困难


class QuestionBank(Base):
    """题库表 - 用于管理题目批次"""
    __tablename__ = "question_banks"
    
    id = Column(Integer, primary_key=True, index=True, comment="题库ID")
    name = Column(String(200), nullable=False, comment="题库名称")
    description = Column(String(500), nullable=True, comment="题库描述")
    question_count = Column(Integer, default=0, comment="题目数量")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    is_active = Column(Integer, default=1, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    questions = relationship("Question", back_populates="bank", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_bank_name", "name"),
        {"comment": "题库表"}
    )


class Question(Base):
    """题目表"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True, comment="题目ID")
    bank_id = Column(Integer, ForeignKey("question_banks.id", ondelete="CASCADE"), nullable=True, comment="所属题库ID")
    question_type = Column(
        Enum(QuestionType), 
        nullable=False, 
        default=QuestionType.SINGLE_CHOICE,
        comment="题目类型"
    )
    title = Column(Text, nullable=False, comment="题干内容")
    options = Column(Text, nullable=True, comment="选项JSON，如：{'A':'选项A','B':'选项B'}")
    answer = Column(Text, nullable=False, comment="正确答案")
    analysis = Column(Text, nullable=True, comment="答案解析")
    difficulty = Column(
        Enum(DifficultyLevel),
        nullable=False,
        default=DifficultyLevel.MEDIUM,
        comment="难度等级"
    )
    score = Column(Integer, default=1, comment="题目分值")
    image_url = Column(String(500), nullable=True, comment="题目图片URL")
    source = Column(String(100), nullable=True, comment="题目来源")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    is_active = Column(Integer, default=1, comment="是否启用：1启用 0禁用")
    use_count = Column(Integer, default=0, comment="使用次数")
    correct_count = Column(Integer, default=0, comment="正确次数")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    bank = relationship("QuestionBank", back_populates="questions")
    knowledge_points = relationship(
        "KnowledgePoint", 
        secondary="question_knowledge",
        back_populates="questions"
    )
    exam_questions = relationship("ExamQuestion", back_populates="question")
    wrong_records = relationship("WrongQuestion", back_populates="question")
    
    __table_args__ = (
        Index("idx_question_type", "question_type"),
        Index("idx_question_difficulty", "difficulty"),
        Index("idx_question_active", "is_active"),
        Index("idx_question_bank", "bank_id"),
        {"comment": "题目表"}
    )


class KnowledgePoint(Base):
    """知识点表（树状结构）"""
    __tablename__ = "knowledge_points"
    
    id = Column(Integer, primary_key=True, index=True, comment="知识点ID")
    name = Column(String(100), nullable=False, comment="知识点名称")
    code = Column(String(50), unique=True, nullable=True, comment="知识点编码")
    parent_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True, comment="父级ID")
    level = Column(Integer, default=1, comment="层级深度")
    sort_order = Column(Integer, default=0, comment="排序序号")
    description = Column(String(500), nullable=True, comment="知识点描述")
    is_active = Column(Integer, default=1, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 自关联关系
    children = relationship("KnowledgePoint", backref="parent", remote_side=[id])
    
    # 关联关系
    questions = relationship(
        "Question",
        secondary="question_knowledge",
        back_populates="knowledge_points"
    )
    
    __table_args__ = (
        Index("idx_knowledge_parent", "parent_id"),
        Index("idx_knowledge_level", "level"),
        {"comment": "知识点表"}
    )


class QuestionKnowledge(Base):
    """题目知识点关联表"""
    __tablename__ = "question_knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(
        Integer, 
        ForeignKey("questions.id", ondelete="CASCADE"), 
        nullable=False,
        comment="题目ID"
    )
    knowledge_id = Column(
        Integer, 
        ForeignKey("knowledge_points.id", ondelete="CASCADE"), 
        nullable=False,
        comment="知识点ID"
    )
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    __table_args__ = (
        Index("idx_question_knowledge", "question_id", "knowledge_id", unique=True),
        {"comment": "题目知识点关联表"}
    )
