"""
楚然智考系统 - 考试相关Pydantic模式
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.exam import ExamType, ExamStatus, RecordStatus
from app.schemas.question import QuestionBrief, QuestionResponse


# ==================== 考试模式 ====================

class ExamBase(BaseModel):
    """考试基础模式"""
    title: str = Field(..., max_length=200, description="考试标题")
    description: Optional[str] = Field(None, description="考试描述")
    exam_type: ExamType = Field(ExamType.MOCK, description="考试类型")
    total_score: int = Field(100, ge=1, description="总分")
    pass_score: int = Field(60, ge=0, description="及格分数")
    duration: int = Field(120, ge=0, description="考试时长(分钟)，0表示不限时")


class ExamCreate(ExamBase):
    """创建考试模式"""
    is_random: int = Field(0, description="是否随机组卷")
    random_config: Optional[Dict[str, Any]] = Field(None, description="随机组卷配置")
    question_ids: Optional[List[int]] = Field(default=[], description="题目ID列表(固定组卷)")
    random_question_count: int = Field(0, ge=0, description="随机抽题数量，0表示不使用统一随机数量")
    question_type_filter: str = Field("all", description="题型过滤: all/single/multiple")
    bank_ids: List[int] = Field(default=[], description="题库ID列表，可多选")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    allow_review: int = Field(1, description="是否允许查看解析")
    show_answer: int = Field(1, description="交卷后是否显示答案")
    max_attempts: int = Field(0, description="最大尝试次数")


class ExamUpdate(BaseModel):
    """更新考试模式"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    exam_type: Optional[ExamType] = None
    status: Optional[ExamStatus] = None
    total_score: Optional[int] = Field(None, ge=1)
    pass_score: Optional[int] = Field(None, ge=0)
    duration: Optional[int] = Field(None, ge=0)
    is_random: Optional[int] = None
    random_config: Optional[Dict[str, Any]] = None
    question_ids: Optional[List[int]] = None
    random_question_count: Optional[int] = Field(None, ge=0)
    question_type_filter: Optional[str] = None
    bank_ids: Optional[List[int]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    allow_review: Optional[int] = None
    show_answer: Optional[int] = None
    max_attempts: Optional[int] = None


class ExamResponse(ExamBase):
    """考试响应模式"""
    id: int
    status: ExamStatus
    question_count: int
    is_random: int
    random_question_count: int
    question_type_filter: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    allow_review: int
    show_answer: int
    max_attempts: int
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExamListResponse(BaseModel):
    """考试列表响应模式"""
    total: int
    items: List[ExamResponse]


class ExamDetail(ExamResponse):
    """考试详情（含题目）"""
    questions: List[QuestionBrief] = []


# ==================== 随机组卷配置模式 ====================

class RandomQuestionConfig(BaseModel):
    """随机题目配置"""
    question_type: str = Field(description="题目类型")
    count: int = Field(ge=1, description="数量")
    score: int = Field(ge=1, description="每题分值")
    knowledge_ids: Optional[List[int]] = Field(None, description="知识点ID列表")
    difficulty: Optional[str] = Field(None, description="难度")


class RandomExamConfig(BaseModel):
    """随机组卷配置"""
    questions: List[RandomQuestionConfig] = Field(description="题目配置列表")


# ==================== 考试记录模式 ====================

class StartExamRequest(BaseModel):
    """开始考试请求"""
    exam_id: int = Field(description="考试ID")


class StartExamResponse(BaseModel):
    """开始考试响应"""
    record_id: int = Field(description="考试记录ID")
    exam: ExamResponse
    questions: List[QuestionBrief]
    start_time: datetime
    end_time: datetime = Field(description="截止时间")


class SubmitAnswerRequest(BaseModel):
    """提交答案请求"""
    question_id: int = Field(description="题目ID")
    answer: str = Field(description="用户答案")


class SubmitExamRequest(BaseModel):
    """交卷请求"""
    record_id: int = Field(description="考试记录ID")
    answers: List[SubmitAnswerRequest] = Field(description="答案列表")


class ExamRecordResponse(BaseModel):
    """考试记录响应"""
    id: int
    user_id: int
    exam_id: int
    exam_title: str
    status: RecordStatus
    score: float
    correct_count: int
    wrong_count: int
    unanswered_count: int
    accuracy: float
    duration: int
    is_passed: int
    start_time: datetime
    submit_time: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExamRecordListResponse(BaseModel):
    """考试记录列表响应"""
    total: int
    items: List[ExamRecordResponse]


class ExamAnswerDetail(BaseModel):
    """答题详情"""
    question_id: int
    question: QuestionResponse
    user_answer: Optional[str] = None
    is_correct: int
    score: float
    
    class Config:
        from_attributes = True


class ExamRecordDetail(ExamRecordResponse):
    """考试记录详情（含答题详情）"""
    answers: List[ExamAnswerDetail] = []


# ==================== 错题本模式 ====================

class WrongQuestionResponse(BaseModel):
    """错题响应"""
    id: int
    user_id: int
    question_id: int
    question: QuestionResponse
    wrong_count: int
    last_wrong_answer: Optional[str] = None
    is_mastered: int
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WrongQuestionListResponse(BaseModel):
    """错题列表响应"""
    total: int
    items: List[WrongQuestionResponse]


class WrongQuestionUpdate(BaseModel):
    """更新错题"""
    is_mastered: Optional[int] = None
    note: Optional[str] = None


# ==================== 学习统计模式 ====================

class StudyStatistics(BaseModel):
    """学习统计"""
    total_study_days: int = Field(description="学习天数")
    total_study_duration: int = Field(description="总学习时长(分钟)")
    total_questions: int = Field(description="练习题数")
    total_correct: int = Field(description="正确题数")
    total_exams: int = Field(description="参加考试次数")
    average_accuracy: float = Field(description="平均正确率")
    wrong_question_count: int = Field(description="错题数量")


class DailyStudyRecord(BaseModel):
    """每日学习记录"""
    date: str
    study_duration: int
    question_count: int
    correct_count: int
    exam_count: int


class StudyTrend(BaseModel):
    """学习趋势"""
    dates: List[str]
    study_durations: List[int]
    question_counts: List[int]
    accuracies: List[float]
