"""
楚然智考系统 - 考试服务
处理考试管理、组卷、判分、错题等功能
"""
import json
import re
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.question import Question, QuestionType
from app.models.exam import (
    Exam, ExamQuestion, ExamRecord, ExamAnswer,
    WrongQuestion, StudyRecord, ExamType, ExamStatus, RecordStatus,
    ExamQuestionBank,
)
from app.schemas.exam import ExamCreate, ExamUpdate, RandomExamConfig
from app.services.question_service import QuestionService


class ExamService:
    """考试服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.question_service = QuestionService(db)
    
    # ==================== 考试管理 ====================
    
    def get_exam_by_id(self, exam_id: int) -> Optional[Exam]:
        """根据ID获取考试"""
        return self.db.query(Exam).filter(Exam.id == exam_id).first()
    
    def get_exams(
        self,
        skip: int = 0,
        limit: int = 20,
        keyword: str = None,
        exam_type: str = None,
        status: str = None
    ) -> Tuple[List[Exam], int]:
        """获取考试列表"""
        query = self.db.query(Exam)
        
        if keyword:
            query = query.filter(Exam.title.contains(keyword))
        
        if exam_type:
            query = query.filter(Exam.exam_type == exam_type)
        
        if status:
            query = query.filter(Exam.status == status)
        
        total = query.count()
        exams = query.order_by(Exam.id.desc()).offset(skip).limit(limit).all()
        
        return exams, total
    
    def get_available_exams(self, user_id: int) -> List[Exam]:
        """获取用户可参加的考试"""
        now = datetime.now()
        query = self.db.query(Exam).filter(
            Exam.status == ExamStatus.PUBLISHED,
            (Exam.start_time == None) | (Exam.start_time <= now),
            (Exam.end_time == None) | (Exam.end_time >= now)
        )
        return query.order_by(Exam.id.desc()).all()
    
    def create_exam(self, exam_data: ExamCreate, creator_id: int = None) -> Exam:
        """创建考试"""
        # 处理随机组卷配置
        random_config_json = None
        if exam_data.random_config:
            random_config_json = json.dumps(exam_data.random_config, ensure_ascii=False)
        
        exam = Exam(
            title=exam_data.title,
            description=exam_data.description,
            exam_type=exam_data.exam_type,
            total_score=exam_data.total_score,
            pass_score=exam_data.pass_score,
            duration=exam_data.duration,
            is_random=exam_data.is_random,
            random_config=random_config_json,
            random_question_count=exam_data.random_question_count,
            question_type_filter=exam_data.question_type_filter,
            start_time=exam_data.start_time,
            end_time=exam_data.end_time,
            allow_review=exam_data.allow_review,
            show_answer=exam_data.show_answer,
            max_attempts=exam_data.max_attempts,
            creator_id=creator_id,
        )
        
        self.db.add(exam)
        self.db.flush()
        
        # 保存考试与题库的关联
        if exam_data.bank_ids:
            for bank_id in set(exam_data.bank_ids):
                link = ExamQuestionBank(exam_id=exam.id, bank_id=bank_id)
                self.db.add(link)

        # 固定组卷：添加指定题目
        if not exam_data.is_random and exam_data.question_ids:
            for i, q_id in enumerate(exam_data.question_ids):
                question = self.question_service.get_question_by_id(q_id)
                if question:
                    eq = ExamQuestion(
                        exam_id=exam.id,
                        question_id=q_id,
                        sort_order=i,
                        score=question.score
                    )
                    self.db.add(eq)
            exam.question_count = len(exam_data.question_ids)

        self.db.commit()
        self.db.refresh(exam)
        
        return exam
    
    def update_exam(self, exam_id: int, exam_data: ExamUpdate) -> Optional[Exam]:
        """更新考试"""
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return None
        
        update_data = exam_data.model_dump(exclude_unset=True, exclude={"question_ids", "bank_ids"})
        
        # 处理随机组卷配置
        if "random_config" in update_data and update_data["random_config"]:
            update_data["random_config"] = json.dumps(update_data["random_config"], ensure_ascii=False)
        
        for field, value in update_data.items():
            setattr(exam, field, value)
        
        # 更新题目
        if exam_data.question_ids is not None:
            self.db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).delete()
            for i, q_id in enumerate(exam_data.question_ids):
                question = self.question_service.get_question_by_id(q_id)
                if question:
                    eq = ExamQuestion(
                        exam_id=exam_id,
                        question_id=q_id,
                        sort_order=i,
                        score=question.score
                    )
                    self.db.add(eq)
            exam.question_count = len(exam_data.question_ids)
        
        self.db.commit()
        self.db.refresh(exam)
        
        return exam
    
    def delete_exam(self, exam_id: int) -> bool:
        """删除考试及其所有关联数据"""
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return False
        
        # 删除考试答案（先删除子表）
        self.db.query(ExamAnswer).filter(
            ExamAnswer.record_id.in_(
                self.db.query(ExamRecord.id).filter(ExamRecord.exam_id == exam_id)
            )
        ).delete(synchronize_session=False)
        
        # 删除考试记录
        self.db.query(ExamRecord).filter(ExamRecord.exam_id == exam_id).delete(synchronize_session=False)
        
        # 删除考试题目关联
        self.db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).delete(synchronize_session=False)
        
        # 删除考试
        self.db.delete(exam)
        self.db.commit()
        
        return True
    
    def publish_exam(self, exam_id: int) -> Optional[Exam]:
        """发布考试"""
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return None
        
        exam.status = ExamStatus.PUBLISHED
        self.db.commit()
        self.db.refresh(exam)
        
        return exam
    
    # ==================== 组卷引擎 ====================
    
    def generate_exam_questions(self, exam: Exam) -> List[Question]:
        """
        生成考试题目
        支持固定组卷和随机组卷
        """
        # 优先使用统一随机抽题配置（基于 random_question_count / question_type_filter / 多题库）
        if exam.random_question_count and exam.random_question_count > 0:
            query = self.db.query(Question).filter(Question.is_active == 1)

            # 按题库过滤（多题库）
            if getattr(exam, "banks", None):
                bank_ids = [link.bank_id for link in exam.banks]
                if bank_ids:
                    query = query.filter(Question.bank_id.in_(bank_ids))

            # 按题型过滤
            if exam.question_type_filter == "single":
                query = query.filter(Question.question_type == QuestionType.SINGLE_CHOICE)
            elif exam.question_type_filter == "multiple":
                query = query.filter(Question.question_type == QuestionType.MULTIPLE_CHOICE)

            # 随机抽题（MySQL 使用 RAND）
            questions = (
                query
                .order_by(func.rand())
                .limit(exam.random_question_count)
                .all()
            )
            return questions

        if not exam.is_random:
            # 固定组卷：返回预设题目
            exam_questions = self.db.query(ExamQuestion).filter(
                ExamQuestion.exam_id == exam.id
            ).order_by(ExamQuestion.sort_order).all()
            
            questions = []
            for eq in exam_questions:
                question = self.question_service.get_question_by_id(eq.question_id)
                if question:
                    questions.append(question)
            return questions
        
        # 随机组卷
        if not exam.random_config:
            return []
        
        config = json.loads(exam.random_config)
        questions = []
        used_ids = []
        
        for item in config.get("questions", []):
            q_type = item.get("question_type")
            count = item.get("count", 0)
            knowledge_ids = item.get("knowledge_ids")
            difficulty = item.get("difficulty")
            
            random_questions = self.question_service.get_random_questions(
                count=count,
                question_type=q_type,
                difficulty=difficulty,
                knowledge_ids=knowledge_ids,
                exclude_ids=used_ids
            )
            
            for q in random_questions:
                questions.append(q)
                used_ids.append(q.id)
        
        return questions
    
    # ==================== 考试流程 ====================
    
    def start_exam(self, user_id: int, exam_id: int) -> Tuple[Optional[ExamRecord], str]:
        """
        开始考试
        返回: (考试记录, 错误信息)
        """
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            return None, "考试不存在"
        
        if exam.status != ExamStatus.PUBLISHED:
            return None, "考试未发布"
        
        # 检查时间限制
        now = datetime.now()
        if exam.start_time and now < exam.start_time:
            return None, "考试尚未开始"
        if exam.end_time and now > exam.end_time:
            return None, "考试已结束"
        
        # 检查尝试次数
        if exam.max_attempts > 0:
            attempt_count = self.db.query(ExamRecord).filter(
                ExamRecord.user_id == user_id,
                ExamRecord.exam_id == exam_id
            ).count()
            if attempt_count >= exam.max_attempts:
                return None, f"已达到最大尝试次数({exam.max_attempts}次)"
        
        # 检查是否有未完成的考试
        ongoing = self.db.query(ExamRecord).filter(
            ExamRecord.user_id == user_id,
            ExamRecord.exam_id == exam_id,
            ExamRecord.status == RecordStatus.IN_PROGRESS
        ).first()
        if ongoing:
            return ongoing, ""
        
        # 创建考试记录
        record = ExamRecord(
            user_id=user_id,
            exam_id=exam_id,
            status=RecordStatus.IN_PROGRESS,
            start_time=now
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        return record, ""
    
    def submit_exam(
        self, 
        record_id: int, 
        answers: List[Dict[str, Any]]
    ) -> Tuple[Optional[ExamRecord], str]:
        """
        提交考试
        返回: (考试记录, 错误信息)
        """
        record = self.db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
        if not record:
            return None, "考试记录不存在"
        
        if record.status != RecordStatus.IN_PROGRESS:
            return None, "考试已提交"
        
        exam = self.get_exam_by_id(record.exam_id)
        if not exam:
            return None, "考试不存在"
        
        # 获取考试题目
        questions = self.generate_exam_questions(exam)
        question_map = {q.id: q for q in questions}
        
        # 处理答案并判分
        total_score = 0
        correct_count = 0
        wrong_count = 0
        
        for ans in answers:
            question_id = ans.get("question_id")
            user_answer = ans.get("answer", "")
            
            question = question_map.get(question_id)
            if not question:
                continue
            
            # 判分
            is_correct, score = self.grade_answer(question, user_answer)
            
            # 保存答题记录
            exam_answer = ExamAnswer(
                record_id=record_id,
                question_id=question_id,
                user_answer=user_answer,
                is_correct=is_correct,
                score=score
            )
            self.db.add(exam_answer)
            
            total_score += score
            if is_correct == 1:
                correct_count += 1
                # 更新题目正确率
                question.correct_count += 1
            else:
                wrong_count += 1
                # 记录错题
                self.add_wrong_question(record.user_id, question_id, user_answer)
            
            # 更新题目使用次数
            question.use_count += 1
        
        # 计算未答题数
        unanswered_count = len(questions) - len(answers)
        
        # 更新考试记录
        now = datetime.now()
        duration = int((now - record.start_time).total_seconds())
        accuracy = (correct_count / len(questions) * 100) if questions else 0
        
        record.status = RecordStatus.GRADED
        record.score = total_score
        record.correct_count = correct_count
        record.wrong_count = wrong_count
        record.unanswered_count = unanswered_count
        record.accuracy = round(accuracy, 2)
        record.duration = duration
        record.submit_time = now
        record.is_passed = 1 if total_score >= exam.pass_score else 0
        
        # 更新学习记录
        self.update_study_record(record.user_id, len(questions), correct_count, 1)
        
        self.db.commit()
        self.db.refresh(record)
        
        return record, ""
    
    def grade_answer(self, question: Question, user_answer: str) -> Tuple[int, float]:
        """
        判分
        返回: (是否正确, 得分)
        is_correct: 0错误 1正确 2部分正确
        """
        if not user_answer:
            return 0, 0
        
        correct_answer = question.answer.strip()
        user_answer = user_answer.strip()
        
        if question.question_type in [QuestionType.SINGLE_CHOICE, QuestionType.TRUE_FALSE]:
            # 单选题、判断题：精确匹配
            if user_answer.upper() == correct_answer.upper():
                return 1, question.score
            return 0, 0
        
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            # 多选题：只保留字母，忽略逗号空格等符号
            correct_letters = set(re.sub(r'[^A-Za-z]', '', correct_answer).upper())
            user_letters = set(re.sub(r'[^A-Za-z]', '', user_answer).upper())
            
            if correct_letters == user_letters:
                return 1, question.score
            elif user_letters.issubset(correct_letters) and len(user_letters) > 0:
                return 2, question.score * 0.5
            return 0, 0
        
        elif question.question_type == QuestionType.FILL_BLANK:
            # 填空题：支持多个答案（用|分隔）和模糊匹配
            correct_answers = [a.strip().lower() for a in correct_answer.split("|")]
            user_answer_lower = user_answer.lower()
            
            # 精确匹配
            if user_answer_lower in correct_answers:
                return 1, question.score
            
            # 模糊匹配（去除空格和标点）
            def normalize(s):
                return re.sub(r'[\s\.,，。、；;：:！!？?]', '', s)
            
            normalized_user = normalize(user_answer_lower)
            for ans in correct_answers:
                if normalize(ans) == normalized_user:
                    return 1, question.score
            
            return 0, 0
        
        # 简答题需要人工判分
        return 0, 0
    
    # ==================== 错题管理 ====================
    
    def add_wrong_question(self, user_id: int, question_id: int, wrong_answer: str):
        """添加错题"""
        wrong = self.db.query(WrongQuestion).filter(
            WrongQuestion.user_id == user_id,
            WrongQuestion.question_id == question_id
        ).first()
        
        if wrong:
            wrong.wrong_count += 1
            wrong.last_wrong_answer = wrong_answer
            wrong.is_mastered = 0
        else:
            wrong = WrongQuestion(
                user_id=user_id,
                question_id=question_id,
                last_wrong_answer=wrong_answer
            )
            self.db.add(wrong)
    
    def get_wrong_questions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        is_mastered: int = None
    ) -> Tuple[List[WrongQuestion], int]:
        """获取错题列表"""
        query = self.db.query(WrongQuestion).filter(WrongQuestion.user_id == user_id)
        
        if is_mastered is not None:
            query = query.filter(WrongQuestion.is_mastered == is_mastered)
        
        total = query.count()
        wrongs = query.order_by(WrongQuestion.updated_at.desc()).offset(skip).limit(limit).all()
        
        return wrongs, total
    
    def mark_mastered(self, user_id: int, wrong_id: int, is_mastered: int) -> bool:
        """标记错题为已掌握"""
        wrong = self.db.query(WrongQuestion).filter(
            WrongQuestion.id == wrong_id,
            WrongQuestion.user_id == user_id
        ).first()
        
        if not wrong:
            return False
        
        wrong.is_mastered = is_mastered
        self.db.commit()
        
        return True
    
    # ==================== 考试记录 ====================
    
    def get_exam_records(
        self,
        user_id: int = None,
        exam_id: int = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[ExamRecord], int]:
        """获取考试记录"""
        query = self.db.query(ExamRecord)
        
        if user_id:
            query = query.filter(ExamRecord.user_id == user_id)
        
        if exam_id:
            query = query.filter(ExamRecord.exam_id == exam_id)
        
        total = query.count()
        records = query.order_by(ExamRecord.id.desc()).offset(skip).limit(limit).all()
        
        return records, total
    
    def get_exam_record_detail(self, record_id: int) -> Optional[ExamRecord]:
        """获取考试记录详情"""
        return self.db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
    
    # ==================== 学习统计 ====================
    
    def update_study_record(
        self, 
        user_id: int, 
        question_count: int, 
        correct_count: int,
        exam_count: int = 0
    ):
        """更新学习记录"""
        today = datetime.now().date()
        
        record = self.db.query(StudyRecord).filter(
            StudyRecord.user_id == user_id,
            func.date(StudyRecord.study_date) == today
        ).first()
        
        if record:
            record.question_count += question_count
            record.correct_count += correct_count
            record.exam_count += exam_count
        else:
            record = StudyRecord(
                user_id=user_id,
                study_date=datetime.now(),
                question_count=question_count,
                correct_count=correct_count,
                exam_count=exam_count
            )
            self.db.add(record)
    
    def get_study_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取学习统计"""
        # 学习天数
        study_days = self.db.query(func.count(func.distinct(func.date(StudyRecord.study_date)))).filter(
            StudyRecord.user_id == user_id
        ).scalar() or 0
        
        # 总学习时长
        total_duration = self.db.query(func.sum(StudyRecord.study_duration)).filter(
            StudyRecord.user_id == user_id
        ).scalar() or 0
        
        # 练习题数和正确数
        stats = self.db.query(
            func.sum(StudyRecord.question_count),
            func.sum(StudyRecord.correct_count),
            func.sum(StudyRecord.exam_count)
        ).filter(StudyRecord.user_id == user_id).first()
        
        total_questions = stats[0] or 0
        total_correct = stats[1] or 0
        total_exams = stats[2] or 0
        
        # 平均正确率
        avg_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # 错题数量
        wrong_count = self.db.query(WrongQuestion).filter(
            WrongQuestion.user_id == user_id,
            WrongQuestion.is_mastered == 0
        ).count()
        
        return {
            "total_study_days": study_days,
            "total_study_duration": total_duration,
            "total_questions": total_questions,
            "total_correct": total_correct,
            "total_exams": total_exams,
            "average_accuracy": round(avg_accuracy, 2),
            "wrong_question_count": wrong_count
        }
    
    def get_study_trend(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取学习趋势"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        records = self.db.query(StudyRecord).filter(
            StudyRecord.user_id == user_id,
            func.date(StudyRecord.study_date) >= start_date,
            func.date(StudyRecord.study_date) <= end_date
        ).all()
        
        # 构建日期映射
        record_map = {}
        for r in records:
            date_str = r.study_date.strftime("%Y-%m-%d")
            record_map[date_str] = r
        
        dates = []
        study_durations = []
        question_counts = []
        accuracies = []
        
        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            dates.append(date_str)
            
            if date_str in record_map:
                r = record_map[date_str]
                study_durations.append(r.study_duration)
                question_counts.append(r.question_count)
                acc = (r.correct_count / r.question_count * 100) if r.question_count > 0 else 0
                accuracies.append(round(acc, 2))
            else:
                study_durations.append(0)
                question_counts.append(0)
                accuracies.append(0)
            
            current += timedelta(days=1)
        
        return {
            "dates": dates,
            "study_durations": study_durations,
            "question_counts": question_counts,
            "accuracies": accuracies
        }
