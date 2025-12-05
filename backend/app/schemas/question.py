"""
楚然智考系统 - 题库相关Pydantic模式
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.question import QuestionType, DifficultyLevel


# ==================== 题目模式 ====================

class QuestionBase(BaseModel):
    """题目基础模式"""
    question_type: QuestionType = Field(..., description="题目类型")
    title: str = Field(..., min_length=1, description="题干内容")
    options: Optional[Dict[str, str]] = Field(None, description="选项")
    answer: str = Field(..., description="正确答案")
    analysis: Optional[str] = Field(None, description="答案解析")
    difficulty: DifficultyLevel = Field(DifficultyLevel.MEDIUM, description="难度等级")
    score: int = Field(1, ge=1, description="题目分值")
    image_url: Optional[str] = Field(None, description="题目图片URL")
    source: Optional[str] = Field(None, description="题目来源")


class QuestionCreate(QuestionBase):
    """创建题目模式"""
    knowledge_ids: Optional[List[int]] = Field(default=[], description="知识点ID列表")


class QuestionUpdate(BaseModel):
    """更新题目模式"""
    question_type: Optional[QuestionType] = None
    title: Optional[str] = None
    options: Optional[Dict[str, str]] = None
    answer: Optional[str] = None
    analysis: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    score: Optional[int] = Field(None, ge=1)
    image_url: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[int] = None
    knowledge_ids: Optional[List[int]] = None


class QuestionResponse(QuestionBase):
    """题目响应模式"""
    id: int
    is_active: int
    use_count: int
    correct_count: int
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    knowledge_points: List["KnowledgePointResponse"] = []
    
    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """题目列表响应模式"""
    total: int
    items: List[QuestionResponse]


class QuestionBrief(BaseModel):
    """题目简要信息（考试用）"""
    id: int
    question_type: QuestionType
    title: str
    options: Optional[Dict[str, str]] = None
    score: int
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== 知识点模式 ====================

class KnowledgePointBase(BaseModel):
    """知识点基础模式"""
    name: str = Field(..., max_length=100, description="知识点名称")
    code: Optional[str] = Field(None, max_length=50, description="知识点编码")
    parent_id: Optional[int] = Field(None, description="父级ID")
    sort_order: int = Field(0, description="排序序号")
    description: Optional[str] = Field(None, max_length=500, description="知识点描述")


class KnowledgePointCreate(KnowledgePointBase):
    """创建知识点模式"""
    pass


class KnowledgePointUpdate(BaseModel):
    """更新知识点模式"""
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=50)
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[int] = None


class KnowledgePointResponse(KnowledgePointBase):
    """知识点响应模式"""
    id: int
    level: int
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgePointTree(KnowledgePointResponse):
    """知识点树形结构"""
    children: List["KnowledgePointTree"] = []


# ==================== 题库模式 ====================

class QuestionBankBase(BaseModel):
    """题库基础模式"""
    name: str = Field(..., max_length=200, description="题库名称")
    description: Optional[str] = Field(None, max_length=500, description="题库描述")


class QuestionBankCreate(QuestionBankBase):
    """创建题库模式"""
    pass


class QuestionBankResponse(QuestionBankBase):
    """题库响应模式"""
    id: int
    question_count: int
    is_active: int
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class QuestionBankListResponse(BaseModel):
    """题库列表响应模式"""
    total: int
    items: List[QuestionBankResponse]


# ==================== 题库导入模式 ====================

class ImportResult(BaseModel):
    """导入结果模式"""
    success: bool
    total: int = Field(description="总数")
    success_count: int = Field(description="成功数")
    fail_count: int = Field(description="失败数")
    errors: List[Dict[str, Any]] = Field(default=[], description="错误详情")
    bank_id: Optional[int] = Field(None, description="创建的题库ID")


class ExcelImportRow(BaseModel):
    """Excel导入行数据"""
    row_number: int
    question_type: str
    title: str
    options: Optional[str] = None
    answer: str
    analysis: Optional[str] = None
    knowledge_point: Optional[str] = None
    difficulty: Optional[str] = None


class OCRResult(BaseModel):
    """OCR识别结果"""
    success: bool
    questions: List[QuestionCreate] = []
    raw_text: str = Field(description="原始识别文本")
    errors: List[str] = []


# 解决循环引用
QuestionResponse.model_rebuild()
KnowledgePointTree.model_rebuild()
