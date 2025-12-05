"""
楚然智考系统 - 题库服务
处理题目CRUD、知识点管理等功能
"""
import json
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.question import Question, KnowledgePoint, QuestionKnowledge, QuestionType, DifficultyLevel
from app.schemas.question import QuestionCreate, QuestionUpdate, KnowledgePointCreate, KnowledgePointUpdate


class QuestionService:
    """题库服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== 题目管理 ====================
    
    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """根据ID获取题目"""
        return self.db.query(Question).filter(Question.id == question_id).first()
    
    def get_questions(
        self,
        skip: int = 0,
        limit: int = 20,
        keyword: str = None,
        question_type: str = None,
        difficulty: str = None,
        knowledge_id: int = None,
        is_active: int = None,
        bank_id: int = None
    ) -> Tuple[List[Question], int]:
        """
        获取题目列表
        返回: (题目列表, 总数)
        """
        query = self.db.query(Question)
        
        # 关键词搜索
        if keyword:
            query = query.filter(Question.title.contains(keyword))
        
        # 题型筛选
        if question_type:
            query = query.filter(Question.question_type == question_type)
        
        # 难度筛选
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # 知识点筛选
        if knowledge_id:
            query = query.join(QuestionKnowledge).filter(
                QuestionKnowledge.knowledge_id == knowledge_id
            )
        
        # 状态筛选
        if is_active is not None:
            query = query.filter(Question.is_active == is_active)
        
        # 题库筛选
        if bank_id is not None:
            query = query.filter(Question.bank_id == bank_id)
        
        total = query.count()
        questions = query.order_by(Question.id.desc()).offset(skip).limit(limit).all()
        
        return questions, total
    
    def create_question(self, question_data: QuestionCreate, creator_id: int = None, bank_id: int = None) -> Question:
        """创建题目"""
        # 处理选项
        options_json = None
        if question_data.options:
            options_json = json.dumps(question_data.options, ensure_ascii=False)
        
        question = Question(
            question_type=question_data.question_type,
            title=question_data.title,
            options=options_json,
            answer=question_data.answer,
            analysis=question_data.analysis,
            difficulty=question_data.difficulty,
            score=question_data.score,
            image_url=question_data.image_url,
            source=question_data.source,
            creator_id=creator_id,
            bank_id=bank_id
        )
        
        self.db.add(question)
        self.db.flush()
        
        # 关联知识点
        if question_data.knowledge_ids:
            for kp_id in question_data.knowledge_ids:
                qk = QuestionKnowledge(question_id=question.id, knowledge_id=kp_id)
                self.db.add(qk)
        
        self.db.commit()
        self.db.refresh(question)
        
        return question
    
    def create_questions_batch(self, questions_data: List[QuestionCreate], creator_id: int = None, bank_id: int = None) -> List[Question]:
        """批量创建题目"""
        questions = []
        for q_data in questions_data:
            question = self.create_question(q_data, creator_id, bank_id)
            questions.append(question)
        return questions
    
    def update_question(self, question_id: int, question_data: QuestionUpdate) -> Optional[Question]:
        """更新题目"""
        question = self.get_question_by_id(question_id)
        if not question:
            return None
        
        update_data = question_data.model_dump(exclude_unset=True, exclude={"knowledge_ids"})
        
        # 处理选项
        if "options" in update_data and update_data["options"]:
            update_data["options"] = json.dumps(update_data["options"], ensure_ascii=False)
        
        for field, value in update_data.items():
            setattr(question, field, value)
        
        # 更新知识点关联
        if question_data.knowledge_ids is not None:
            self.db.query(QuestionKnowledge).filter(
                QuestionKnowledge.question_id == question_id
            ).delete()
            for kp_id in question_data.knowledge_ids:
                qk = QuestionKnowledge(question_id=question_id, knowledge_id=kp_id)
                self.db.add(qk)
        
        self.db.commit()
        self.db.refresh(question)
        
        return question
    
    def delete_question(self, question_id: int) -> bool:
        """删除题目，如果题库变空则同时删除题库和相关考试"""
        question = self.get_question_by_id(question_id)
        if not question:
            return False
        
        bank_id = question.bank_id
        
        self.db.delete(question)
        self.db.commit()
        
        # 检查题库是否还有题目，如果没有则删除题库和相关考试
        if bank_id:
            remaining_count = self.db.query(Question).filter(Question.bank_id == bank_id).count()
            if remaining_count == 0:
                self._delete_bank_and_related_exams(bank_id)
        
        return True
    
    def _delete_bank_and_related_exams(self, bank_id: int):
        """删除题库及其相关的考试"""
        from app.models.question import QuestionBank
        from app.models.exam import Exam, ExamQuestion, ExamRecord, ExamAnswer
        
        # 获取该题库的所有题目ID（包括已删除的，通过exam_questions关联查找）
        # 查找使用了该题库题目的考试
        bank = self.db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
        if not bank:
            return
        
        # 获取该题库曾经的题目关联的考试ID
        exam_ids = self.db.query(ExamQuestion.exam_id).join(
            Question, ExamQuestion.question_id == Question.id
        ).filter(Question.bank_id == bank_id).distinct().all()
        exam_ids = [e[0] for e in exam_ids]
        
        # 如果没有通过题目找到考试，尝试查找没有题目的考试（可能题目已删除）
        # 删除这些考试的相关数据
        if exam_ids:
            # 删除考试答案
            self.db.query(ExamAnswer).filter(
                ExamAnswer.record_id.in_(
                    self.db.query(ExamRecord.id).filter(ExamRecord.exam_id.in_(exam_ids))
                )
            ).delete(synchronize_session=False)
            
            # 删除考试记录
            self.db.query(ExamRecord).filter(ExamRecord.exam_id.in_(exam_ids)).delete(synchronize_session=False)
            
            # 删除考试题目关联
            self.db.query(ExamQuestion).filter(ExamQuestion.exam_id.in_(exam_ids)).delete(synchronize_session=False)
            
            # 删除考试
            self.db.query(Exam).filter(Exam.id.in_(exam_ids)).delete(synchronize_session=False)
        
        # 删除题库
        self.db.delete(bank)
        self.db.commit()
    
    def delete_all_questions(self) -> int:
        """删除所有题目，同时删除所有题库和相关考试"""
        from app.models.question import QuestionBank
        from app.models.exam import Exam, ExamQuestion, ExamRecord, ExamAnswer
        
        count = self.db.query(Question).count()
        
        # 删除所有考试相关数据
        self.db.query(ExamAnswer).delete(synchronize_session=False)
        self.db.query(ExamRecord).delete(synchronize_session=False)
        self.db.query(ExamQuestion).delete(synchronize_session=False)
        self.db.query(Exam).delete(synchronize_session=False)
        
        # 删除所有题目
        self.db.query(Question).delete(synchronize_session=False)
        
        # 删除所有题库
        self.db.query(QuestionBank).delete(synchronize_session=False)
        
        self.db.commit()
        
        return count
    
    def get_random_questions(
        self,
        count: int,
        question_type: str = None,
        difficulty: str = None,
        knowledge_ids: List[int] = None,
        exclude_ids: List[int] = None
    ) -> List[Question]:
        """
        随机获取题目
        用于随机组卷
        """
        from sqlalchemy.sql.expression import func
        
        query = self.db.query(Question).filter(Question.is_active == 1)
        
        if question_type:
            query = query.filter(Question.question_type == question_type)
        
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        if knowledge_ids:
            query = query.join(QuestionKnowledge).filter(
                QuestionKnowledge.knowledge_id.in_(knowledge_ids)
            )
        
        if exclude_ids:
            query = query.filter(~Question.id.in_(exclude_ids))
        
        # 随机排序并限制数量
        questions = query.order_by(func.random()).limit(count).all()
        
        return questions
    
    # ==================== 知识点管理 ====================
    
    def get_knowledge_point_by_id(self, kp_id: int) -> Optional[KnowledgePoint]:
        """根据ID获取知识点"""
        return self.db.query(KnowledgePoint).filter(KnowledgePoint.id == kp_id).first()
    
    def get_knowledge_points(
        self,
        parent_id: int = None,
        is_active: int = None
    ) -> List[KnowledgePoint]:
        """获取知识点列表"""
        query = self.db.query(KnowledgePoint)
        
        if parent_id is not None:
            query = query.filter(KnowledgePoint.parent_id == parent_id)
        
        if is_active is not None:
            query = query.filter(KnowledgePoint.is_active == is_active)
        
        return query.order_by(KnowledgePoint.sort_order).all()
    
    def get_knowledge_tree(self) -> List[Dict[str, Any]]:
        """获取知识点树形结构"""
        all_points = self.db.query(KnowledgePoint).filter(
            KnowledgePoint.is_active == 1
        ).order_by(KnowledgePoint.sort_order).all()
        
        # 构建树形结构
        def build_tree(parent_id: int = None) -> List[Dict[str, Any]]:
            result = []
            for point in all_points:
                if point.parent_id == parent_id:
                    node = {
                        "id": point.id,
                        "name": point.name,
                        "code": point.code,
                        "level": point.level,
                        "sort_order": point.sort_order,
                        "description": point.description,
                        "children": build_tree(point.id)
                    }
                    result.append(node)
            return result
        
        return build_tree(None)
    
    def create_knowledge_point(self, kp_data: KnowledgePointCreate) -> KnowledgePoint:
        """创建知识点"""
        # 计算层级
        level = 1
        if kp_data.parent_id:
            parent = self.get_knowledge_point_by_id(kp_data.parent_id)
            if parent:
                level = parent.level + 1
        
        kp = KnowledgePoint(
            name=kp_data.name,
            code=kp_data.code,
            parent_id=kp_data.parent_id,
            level=level,
            sort_order=kp_data.sort_order,
            description=kp_data.description
        )
        
        self.db.add(kp)
        self.db.commit()
        self.db.refresh(kp)
        
        return kp
    
    def update_knowledge_point(self, kp_id: int, kp_data: KnowledgePointUpdate) -> Optional[KnowledgePoint]:
        """更新知识点"""
        kp = self.get_knowledge_point_by_id(kp_id)
        if not kp:
            return None
        
        update_data = kp_data.model_dump(exclude_unset=True)
        
        # 如果更新了父级，重新计算层级
        if "parent_id" in update_data:
            if update_data["parent_id"]:
                parent = self.get_knowledge_point_by_id(update_data["parent_id"])
                if parent:
                    update_data["level"] = parent.level + 1
            else:
                update_data["level"] = 1
        
        for field, value in update_data.items():
            setattr(kp, field, value)
        
        self.db.commit()
        self.db.refresh(kp)
        
        return kp
    
    def delete_knowledge_point(self, kp_id: int) -> bool:
        """删除知识点"""
        kp = self.get_knowledge_point_by_id(kp_id)
        if not kp:
            return False
        
        # 检查是否有子节点
        children = self.db.query(KnowledgePoint).filter(
            KnowledgePoint.parent_id == kp_id
        ).count()
        if children > 0:
            return False
        
        self.db.delete(kp)
        self.db.commit()
        
        return True
    
    # ==================== 统计功能 ====================
    
    def get_question_statistics(self) -> Dict[str, Any]:
        """获取题目统计信息"""
        total = self.db.query(Question).filter(Question.is_active == 1).count()
        
        # 按题型统计
        type_stats = {}
        for qt in QuestionType:
            count = self.db.query(Question).filter(
                Question.is_active == 1,
                Question.question_type == qt
            ).count()
            type_stats[qt.value] = count
        
        # 按难度统计
        difficulty_stats = {}
        for dl in DifficultyLevel:
            count = self.db.query(Question).filter(
                Question.is_active == 1,
                Question.difficulty == dl
            ).count()
            difficulty_stats[dl.value] = count
        
        return {
            "total": total,
            "by_type": type_stats,
            "by_difficulty": difficulty_stats
        }
