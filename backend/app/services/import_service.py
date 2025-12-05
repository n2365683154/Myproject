"""
楚然智考系统 - 题库导入服务
支持Excel、Word、PDF、图片OCR导入
"""
import re
import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.question import QuestionType, DifficultyLevel, QuestionBank, Question
from app.schemas.question import QuestionCreate, ImportResult


class ImportService:
    """题库导入服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== Excel导入 ====================
    
    def import_from_excel(self, file_path: str, creator_id: int = None) -> ImportResult:
        """
        从Excel文件导入题库
        Excel格式：题型 | 题干 | 选项 | 答案 | 解析 | 知识点 | 难度
        """
        import openpyxl
        
        try:
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            questions = []
            errors = []
            
            # 跳过表头
            for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    if not row[0] or not row[1]:  # 题型和题干必填
                        continue
                    
                    question_type = self._parse_question_type(str(row[0]))
                    title = str(row[1]).strip()
                    options = self._parse_options(str(row[2]) if row[2] else None)
                    answer = str(row[3]).strip() if row[3] else ""
                    analysis = str(row[4]).strip() if row[4] else None
                    knowledge_point = str(row[5]).strip() if row[5] else None
                    difficulty = self._parse_difficulty(str(row[6]) if row[6] else None)
                    
                    if not answer:
                        errors.append({
                            "row": row_num,
                            "error": "答案不能为空"
                        })
                        continue
                    
                    question = QuestionCreate(
                        question_type=question_type,
                        title=title,
                        options=options,
                        answer=answer,
                        analysis=analysis,
                        difficulty=difficulty,
                        knowledge_ids=[]
                    )
                    questions.append(question)
                    
                except Exception as e:
                    errors.append({
                        "row": row_num,
                        "error": str(e)
                    })
            
            # 批量创建题目
            from app.services.question_service import QuestionService
            question_service = QuestionService(self.db)
            created = question_service.create_questions_batch(questions, creator_id)
            
            return ImportResult(
                success=True,
                total=len(questions) + len(errors),
                success_count=len(created),
                fail_count=len(errors),
                errors=errors
            )
            
        except Exception as e:
            return ImportResult(
                success=False,
                total=0,
                success_count=0,
                fail_count=1,
                errors=[{"row": 0, "error": f"文件解析失败: {str(e)}"}]
            )
    
    # ==================== Word导入 ====================
    
    def import_from_word(self, file_path: str, bank_name: str, creator_id: int = None) -> ImportResult:
        """
        从Word文件导入题库
        支持多种格式：
        1. 题干中包含答案：1、xxx（A）xxx  A、选项1 B、选项2
        2. 单独答案行：答案：A
        3. 题型标题：一、单选题 / 二、多选题
        """
        from docx import Document
        
        try:
            doc = Document(file_path)
            
            # 合并所有段落文本
            raw_text = "\n".join([para.text for para in doc.paragraphs])
            
            # 预处理：格式化文本
            formatted_text = self._format_exam_text(raw_text)
            
            # 解析格式化后的文本
            questions, errors = self._parse_formatted_text(formatted_text)
            
            if not questions:
                return ImportResult(
                    success=False,
                    total=0,
                    success_count=0,
                    fail_count=1,
                    errors=[{"row": 0, "error": "未识别到有效题目，请检查文档格式"}]
                )
            
            # 创建题库
            bank = QuestionBank(
                name=bank_name,
                question_count=0,
                creator_id=creator_id,
                is_active=1
            )
            self.db.add(bank)
            self.db.flush()  # 获取 bank.id
            
            # 批量创建题目并关联到题库
            from app.services.question_service import QuestionService
            question_service = QuestionService(self.db)
            created = question_service.create_questions_batch(questions, creator_id, bank.id)
            
            # 更新题库的题目数量
            bank.question_count = len(created)
            self.db.commit()
            
            return ImportResult(
                success=True,
                total=len(questions) + len(errors),
                success_count=len(created),
                fail_count=len(errors),
                errors=errors,
                bank_id=bank.id
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.db.rollback()
            return ImportResult(
                success=False,
                total=0,
                success_count=0,
                fail_count=1,
                errors=[{"row": 0, "error": f"文件解析失败: {str(e)}"}]
            )
    
    # ==================== PDF导入 ====================
    
    def import_from_pdf(self, file_path: str, bank_name: str, creator_id: int = None) -> ImportResult:
        """
        从PDF文件导入题库
        自动识别题目格式并解析
        """
        try:
            # 提取PDF文本
            raw_text = self._extract_pdf_text(file_path)
            
            if not raw_text or len(raw_text.strip()) < 10:
                return ImportResult(
                    success=False,
                    total=0,
                    success_count=0,
                    fail_count=1,
                    errors=[{"row": 0, "error": "PDF文件内容为空或无法提取文本"}]
                )
            
            # 使用PDF专用解析方法（支持题目和答案分离的格式）
            questions, errors = self._parse_pdf_exam(raw_text)
            
            if not questions:
                return ImportResult(
                    success=False,
                    total=0,
                    success_count=0,
                    fail_count=1,
                    errors=[{"row": 0, "error": "未识别到有效题目，请检查PDF格式"}]
                )
            
            # 创建题库
            bank = QuestionBank(
                name=bank_name,
                question_count=0,
                creator_id=creator_id,
                is_active=1
            )
            self.db.add(bank)
            self.db.flush()
            
            # 批量创建题目并关联到题库
            from app.services.question_service import QuestionService
            question_service = QuestionService(self.db)
            created = question_service.create_questions_batch(questions, creator_id, bank.id)
            
            # 更新题库的题目数量
            bank.question_count = len(created)
            self.db.commit()
            
            return ImportResult(
                success=True,
                total=len(questions) + len(errors),
                success_count=len(created),
                fail_count=len(errors),
                errors=errors,
                bank_id=bank.id
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.db.rollback()
            return ImportResult(
                success=False,
                total=0,
                success_count=0,
                fail_count=1,
                errors=[{"row": 0, "error": f"PDF解析失败: {str(e)}"}]
            )
    
    def pdf_preview(self, file_path: str) -> Dict:
        """
        PDF预览 - 解析但不导入，返回识别结果供用户确认
        """
        try:
            # 提取PDF文本
            raw_text = self._extract_pdf_text(file_path)
            
            if not raw_text or len(raw_text.strip()) < 10:
                return {
                    "success": False,
                    "raw_text": "",
                    "questions": [],
                    "errors": ["PDF文件内容为空或无法提取文本"]
                }
            
            # 使用PDF专用解析方法（支持题目和答案分离的格式）
            questions, errors = self._parse_pdf_exam(raw_text)
            
            return {
                "success": True,
                "raw_text": raw_text[:5000],  # 限制返回的原始文本长度
                "questions": [q.model_dump() for q in questions],
                "errors": errors
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "raw_text": "",
                "questions": [],
                "errors": [str(e)]
            }
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """
        从PDF文件提取文本
        支持多种PDF格式，包括扫描件（通过OCR）
        """
        text_content = []
        
        try:
            # 首先尝试使用 pdfplumber（对表格和结构化文本效果好）
            import pdfplumber
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            if text_content:
                return '\n'.join(text_content)
        except ImportError:
            pass
        except Exception as e:
            print(f"pdfplumber解析失败: {e}")
        
        try:
            # 备用方案：使用 PyPDF2
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            if text_content:
                return '\n'.join(text_content)
        except ImportError:
            pass
        except Exception as e:
            print(f"PyPDF2解析失败: {e}")
        
        try:
            # 最后尝试 pymupdf (fitz)
            import fitz
            
            doc = fitz.open(file_path)
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text_content.append(page_text)
            doc.close()
            
            if text_content:
                return '\n'.join(text_content)
        except ImportError:
            pass
        except Exception as e:
            print(f"pymupdf解析失败: {e}")
        
        # 如果所有方法都失败
        if not text_content:
            raise Exception("无法提取PDF文本，请确保安装了 pdfplumber 或 PyPDF2 或 pymupdf")
        
        return '\n'.join(text_content)
    
    def _parse_pdf_exam(self, raw_text: str) -> Tuple[List[QuestionCreate], List[Dict]]:
        """
        解析PDF考试试卷 - 支持题目和答案分离的格式
        支持多部分试卷（第一部分、第二部分等），每部分有独立的题号和答案
        """
        questions = []
        errors = []
        
        # 1. 分割试卷为多个部分
        parts = self._split_exam_parts(raw_text)
        
        # 2. 解析每个部分
        global_index = 0
        for part_idx, part_text in enumerate(parts):
            part_questions, part_errors = self._parse_exam_part(part_text, global_index)
            questions.extend(part_questions)
            errors.extend(part_errors)
            global_index += len(part_questions)
        
        return questions, errors
    
    def _split_exam_parts(self, text: str) -> List[str]:
        """将试卷分割为多个部分"""
        # 查找"第X部分"标记
        part_pattern = r'第[一二三四五六七八九十]+部分'
        matches = list(re.finditer(part_pattern, text))
        
        if len(matches) <= 1:
            return [text]
        
        parts = []
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            parts.append(text[start:end])
        
        return parts
    
    def _parse_exam_part(self, part_text: str, global_offset: int) -> Tuple[List[QuestionCreate], List[Dict]]:
        """解析试卷的一个部分"""
        questions = []
        errors = []
        
        # 1. 提取该部分的答案
        answer_map = self._extract_part_answers(part_text)
        
        # 2. 查找题目区域（在"三、答案"之前）
        answer_section = re.search(r'三[、.．\s]*答案', part_text)
        question_text = part_text[:answer_section.start()] if answer_section else part_text
        
        # 3. 分割单选题和多选题区域
        single_section = ""
        multi_section = ""
        
        single_match = re.search(r'一[、.．\s]*单选题', question_text)
        multi_match = re.search(r'二[、.．\s]*多选题', question_text)
        
        if single_match:
            single_start = single_match.end()
            single_end = multi_match.start() if multi_match else len(question_text)
            single_section = question_text[single_start:single_end]
        
        if multi_match:
            multi_section = question_text[multi_match.end():]
        
        # 4. 解析单选题
        if single_section:
            single_qs, single_errs = self._parse_questions_section(
                single_section, QuestionType.SINGLE_CHOICE, answer_map, global_offset
            )
            questions.extend(single_qs)
            errors.extend(single_errs)
        
        # 5. 解析多选题
        if multi_section:
            multi_qs, multi_errs = self._parse_questions_section(
                multi_section, QuestionType.MULTIPLE_CHOICE, answer_map, global_offset + len(questions)
            )
            questions.extend(multi_qs)
            errors.extend(multi_errs)
        
        return questions, errors
    
    def _extract_part_answers(self, part_text: str) -> Dict[int, str]:
        """提取某部分的答案"""
        answer_map = {}
        
        # 查找答案区域
        answer_match = re.search(r'三[、.．\s]*答案(.+?)(?=第[一二三四五六七八九十]+部分|$)', part_text, re.DOTALL)
        if not answer_match:
            return answer_map
        
        answer_section = answer_match.group(1)
        
        # 提取单选答案: 1.C  2.D  或 1.C 2.D
        single_pattern = r'(\d+)\s*[\.．]\s*([A-E])\b'
        for m in re.finditer(single_pattern, answer_section):
            num = int(m.group(1))
            answer_map[num] = m.group(2)
        
        # 提取多选答案: 215.D,E 或 215.A,B,C,D
        multi_pattern = r'(\d+)\s*[\.．]\s*([A-E](?:\s*,\s*[A-E])+)'
        for m in re.finditer(multi_pattern, answer_section):
            num = int(m.group(1))
            answers = re.findall(r'[A-E]', m.group(2))
            answer_map[num] = ','.join(answers)
        
        return answer_map
    
    def _parse_questions_section(self, section_text: str, q_type: QuestionType, 
                                  answer_map: Dict[int, str], global_offset: int) -> Tuple[List[QuestionCreate], List[Dict]]:
        """解析题目区域"""
        questions = []
        errors = []
        
        # 识别题目起始位置 - 匹配 "1、" 或 "1." 开头的题目
        # 需要确保是题目编号而非选项或其他数字
        lines = section_text.split('\n')
        current_question = None
        current_num = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是新题目的开始
            q_match = re.match(r'^(\d{1,3})[、．.]\s*(.+)', line)
            if q_match:
                # 保存上一题
                if current_question and current_num:
                    q = self._build_question(current_question, q_type, current_num, answer_map)
                    if q:
                        questions.append(q)
                    else:
                        errors.append({"row": global_offset + current_num, "error": "解析失败"})
                
                current_num = int(q_match.group(1))
                current_question = q_match.group(2)
            elif current_question is not None:
                # 继续当前题目
                current_question += ' ' + line
        
        # 保存最后一题
        if current_question and current_num:
            q = self._build_question(current_question, q_type, current_num, answer_map)
            if q:
                questions.append(q)
            else:
                errors.append({"row": global_offset + current_num, "error": "解析失败"})
        
        return questions, errors
    
    def _build_question(self, content: str, q_type: QuestionType, q_num: int, 
                        answer_map: Dict[int, str]) -> QuestionCreate:
        """构建题目对象"""
        # 获取答案
        answer = answer_map.get(q_num, "")
        if not answer:
            return None
        
        # 如果答案有多个字母，确保是多选题
        if len(re.findall(r'[A-E]', answer)) > 1:
            q_type = QuestionType.MULTIPLE_CHOICE
        
        # 提取选项
        option_pattern = r'([A-E])[、.．:：]\s*'
        option_matches = list(re.finditer(option_pattern, content))
        
        options = {}
        for i, match in enumerate(option_matches):
            letter = match.group(1)
            start = match.end()
            
            if i + 1 < len(option_matches):
                end = option_matches[i + 1].start()
            else:
                end = len(content)
            
            opt_text = content[start:end].strip()
            opt_text = re.sub(r'\s+', ' ', opt_text).strip()
            if opt_text:
                options[letter] = opt_text
        
        # 提取题干
        if option_matches:
            title = content[:option_matches[0].start()].strip()
        else:
            title = content.strip()
        
        # 清理题干
        title = re.sub(r'[（(]\s*[)）]', '（  ）', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        if not title:
            return None
        
        try:
            return QuestionCreate(
                question_type=q_type,
                title=title,
                options=options if options else None,
                answer=answer,
                analysis="",
                difficulty=DifficultyLevel.MEDIUM,
                knowledge_ids=[]
            )
        except Exception:
            return None
    
    def _extract_answer_section(self, text: str) -> Dict[int, str]:
        """
        提取答案区域，返回 {题号: 答案} 的字典
        支持格式：
        - 1.A  2.D  3.C
        - 1、A  2、D  3、C
        - 单选题 1.A 2.B ...  多选题 69.A,B,C ...
        """
        answer_map = {}
        
        # 查找答案区域
        answer_section = ""
        patterns = [
            r'[一二三四五六七八九十]+[、.．\s]*答案(.+?)(?=[一二三四五六七八九十]+[、.．]|$)',
            r'答案[：:]\s*(.+?)(?=解析|$)',
            r'参考答案[：:]*\s*(.+?)(?=$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                answer_section = match.group(1)
                break
        
        if not answer_section:
            # 尝试从文档末尾查找答案表格格式
            # 如：1.A  2.D  3.C  (连续排列)
            last_part = text[-3000:] if len(text) > 3000 else text
            if re.search(r'\d+\s*[\.、]\s*[A-E]', last_part):
                answer_section = last_part
        
        if answer_section:
            # 提取单选/判断答案: 1.A 或 1、A
            single_pattern = r'(\d+)\s*[\.、．]\s*([A-E])\b'
            for match in re.finditer(single_pattern, answer_section):
                num = int(match.group(1))
                ans = match.group(2)
                if num not in answer_map:
                    answer_map[num] = ans
            
            # 提取多选答案: 69.A,B,C 或 69、A、B、C 或 69.A,B,C,D,E
            multi_pattern = r'(\d+)\s*[\.、．]\s*([A-E](?:\s*[,，、]\s*[A-E])+)'
            for match in re.finditer(multi_pattern, answer_section):
                num = int(match.group(1))
                ans_text = match.group(2)
                answers = re.findall(r'[A-E]', ans_text)
                answer_map[num] = ','.join(answers)
            
            # 提取判断题答案: 1.对 或 1.√
            tf_pattern = r'(\d+)\s*[\.、．]\s*(对|错|√|×|正确|错误)'
            for match in re.finditer(tf_pattern, answer_section):
                num = int(match.group(1))
                ans = match.group(2)
                if ans in ['对', '√', '正确']:
                    answer_map[num] = '对'
                else:
                    answer_map[num] = '错'
        
        return answer_map
    
    def _parse_pdf_question(self, content: str, q_type: QuestionType, q_num: int, answer_map: Dict[int, str]) -> Dict:
        """
        解析PDF中的单个题目
        优先使用答案表中的答案，其次尝试从题干中提取
        """
        result = {"title": "", "options": {}, "answer": "", "analysis": ""}
        
        # 1. 从答案表获取答案
        if q_num in answer_map:
            result["answer"] = answer_map[q_num]
        
        # 2. 提取选项
        option_pattern = r'([A-E])[、.．:：]\s*'
        option_matches = list(re.finditer(option_pattern, content))
        
        options = {}
        for i, match in enumerate(option_matches):
            letter = match.group(1)
            start = match.end()
            
            if i + 1 < len(option_matches):
                end = option_matches[i + 1].start()
            else:
                end = len(content)
            
            opt_text = content[start:end].strip()
            # 清理选项文本
            opt_text = re.sub(r'\s+', ' ', opt_text)
            # 移除末尾的题号（防止下一题混入）
            opt_text = re.sub(r'\d+[、．.]\s*$', '', opt_text).strip()
            if opt_text:
                options[letter] = opt_text
        
        result["options"] = options if options else None
        
        # 3. 提取题干
        if option_matches:
            title = content[:option_matches[0].start()].strip()
        else:
            title = content.strip()
        
        # 清理题干 - 移除答案括号（如果有）
        title = re.sub(r'[（(]\s*[A-E](?:[,，、\s]*[A-E])*\s*[)）]', '（  ）', title)
        title = re.sub(r'\s+', ' ', title).strip()
        result["title"] = title
        
        # 4. 如果没有从答案表获取到答案，尝试从题干提取
        if not result["answer"]:
            # 尝试从括号提取
            answer_in_title = re.search(r'[（(]\s*([A-E](?:[,，、\s]*[A-E])*)\s*[)）]', content)
            if answer_in_title:
                answers = re.findall(r'[A-E]', answer_in_title.group(1))
                result["answer"] = ','.join(answers)
            else:
                # 尝试 "答案：A" 格式
                ans_match = re.search(r'答案[：:]\s*([A-E,，、\s]+)', content)
                if ans_match:
                    answers = re.findall(r'[A-E]', ans_match.group(1))
                    result["answer"] = ','.join(answers)
        
        # 5. 判断题特殊处理
        if q_type == QuestionType.TRUE_FALSE and not result["answer"]:
            tf_match = re.search(r'答案[：:]\s*(对|错|正确|错误|√|×)', content)
            if tf_match:
                ans = tf_match.group(1)
                result["answer"] = '对' if ans in ['对', '正确', '√'] else '错'
        
        # 验证
        if not result["title"]:
            return None
        if not result["answer"]:
            return None
        
        return result
    
    # ==================== 题库管理 ====================
    
    def get_banks(self, skip: int = 0, limit: int = 100):
        """获取题库列表"""
        query = self.db.query(QuestionBank).filter(QuestionBank.is_active == 1)
        total = query.count()
        items = query.order_by(QuestionBank.created_at.desc()).offset(skip).limit(limit).all()
        return {"total": total, "items": items}
    
    def get_bank(self, bank_id: int):
        """获取单个题库"""
        return self.db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
    
    def delete_bank(self, bank_id: int) -> bool:
        """删除题库及其所有题目"""
        bank = self.db.query(QuestionBank).filter(QuestionBank.id == bank_id).first()
        if not bank:
            return False
        
        # 删除题库（由于设置了 cascade，会自动删除关联的题目）
        self.db.delete(bank)
        self.db.commit()
        return True
    
    def _format_exam_text(self, text: str) -> str:
        """
        预处理文本，将其格式化为标准格式
        每个题目占一行，格式：题号|题型|题干|选项A|选项B|选项C|选项D|选项E|答案
        """
        lines = text.split('\n')
        formatted_lines = []
        current_type = "single"  # 默认单选
        
        # 合并所有内容为一个长字符串，方便处理
        full_text = ' '.join([line.strip() for line in lines if line.strip()])
        
        # 移除多余空格
        full_text = re.sub(r'\s+', ' ', full_text)
        
        # 识别题型标记位置
        type_markers = []
        for m in re.finditer(r'[一二三四五六七八九十]+[、.．]\s*(单选题?|多选题?|判断题?|填空题?|简答题?)', full_text):
            type_markers.append((m.start(), m.group(1)))
        
        # 识别所有题目的起始位置 (数字 + 顿号/点)
        # 题号必须前面是空格、换行或文本开头，避免匹配选项中的数字如 "0.693/s"
        question_markers = []
        for m in re.finditer(r'(?:^|(?<=\s))(\d{1,3})[、．]\s*', full_text):
            num = int(m.group(1))
            if 1 <= num <= 500:
                question_markers.append((m.start(), m.end(), num))
        
        # 按位置排序
        question_markers.sort(key=lambda x: x[0])
        
        # 过滤：只保留递增的题号序列（允许跳跃但不能倒退太多）
        filtered_markers = []
        expected_num = 1
        for start, end, num in question_markers:
            # 如果题号合理（在预期范围内，或者是新的题型开始从1重新计数）
            if num >= expected_num or (num == 1 and expected_num > 1):
                filtered_markers.append((start, end, num))
                expected_num = num + 1
        
        question_markers = filtered_markers
        
        # 提取每道题的内容
        for idx, (start, content_start, q_num) in enumerate(question_markers):
            # 确定该题的结束位置
            if idx + 1 < len(question_markers):
                end = question_markers[idx + 1][0]
            else:
                end = len(full_text)
            
            # 提取题目内容
            content = full_text[content_start:end].strip()
            
            # 确定题型（根据最近的题型标记）
            q_type = "single"
            for marker_pos, marker_type in type_markers:
                if marker_pos < start:
                    if '多选' in marker_type:
                        q_type = "multiple"
                    elif '判断' in marker_type:
                        q_type = "truefalse"
                    elif '填空' in marker_type:
                        q_type = "fill"
                    elif '简答' in marker_type:
                        q_type = "short"
                    else:
                        q_type = "single"
            
            # 格式化为标准行
            formatted_lines.append(f"{q_num}|||{q_type}|||{content}")
        
        return '\n'.join(formatted_lines)
    
    def _parse_formatted_text(self, formatted_text: str) -> Tuple[List[QuestionCreate], List[Dict]]:
        """解析格式化后的文本"""
        questions = []
        errors = []
        
        lines = formatted_text.split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            parts = line.split('|||')
            if len(parts) != 3:
                continue
            
            q_num = parts[0].strip()
            q_type_str = parts[1].strip()
            content = parts[2].strip()
            
            # 解析题目内容
            parsed, parse_error = self._parse_question_content(content)
            
            if not parsed:
                row_num = int(q_num) if q_num.isdigit() else 0
                errors.append({"row": row_num, "error": parse_error or "无法解析题目内容", "content": content[:100]})
                continue
            
            # 确定题型
            if q_type_str == "multiple" or len(re.findall(r'[A-E]', parsed.get("answer", ""))) > 1:
                q_type = QuestionType.MULTIPLE_CHOICE
            elif q_type_str == "truefalse":
                q_type = QuestionType.TRUE_FALSE
            elif q_type_str == "fill":
                q_type = QuestionType.FILL_BLANK
            elif q_type_str == "short":
                q_type = QuestionType.SHORT_ANSWER
            else:
                q_type = QuestionType.SINGLE_CHOICE
            
            try:
                questions.append(QuestionCreate(
                    question_type=q_type,
                    title=parsed["title"],
                    options=parsed.get("options"),
                    answer=parsed["answer"],
                    analysis=parsed.get("analysis"),
                    difficulty=DifficultyLevel.MEDIUM,
                    knowledge_ids=[]
                ))
            except Exception as e:
                errors.append({"row": int(q_num) if q_num.isdigit() else 0, "error": str(e)})
        
        return questions, errors
    
    def _parse_question_content(self, content: str) -> Tuple[Dict, str]:
        """
        解析单个题目内容，提取题干、选项、答案
        返回: (解析结果, 错误信息) - 如果解析失败，结果为None
        """
        result = {"title": "", "options": {}, "answer": "", "analysis": ""}
        
        # 1. 提取答案 - 从括号中提取 (支持中英文括号)
        answer_match = re.search(r'[（(]\s*([A-E](?:[,，、\s]*[A-E])*)\s*[)）]', content)
        if answer_match:
            answers = re.findall(r'[A-E]', answer_match.group(1))
            result["answer"] = ','.join(answers)
        
        # 2. 提取选项 - 找到所有 A、B、C、D、E 选项
        option_pattern = r'(?<![A-Za-z])([A-E])[、.．:：]\s*'
        option_matches = list(re.finditer(option_pattern, content))
        
        options = {}
        for i, match in enumerate(option_matches):
            letter = match.group(1)
            start = match.end()
            
            # 确定选项内容的结束位置
            if i + 1 < len(option_matches):
                end = option_matches[i + 1].start()
            else:
                end = len(content)
            
            opt_text = content[start:end].strip()
            opt_text = re.sub(r'\s+', ' ', opt_text).strip()
            if opt_text:
                options[letter] = opt_text
        
        result["options"] = options if options else None
        
        # 3. 提取题干 - 选项之前的内容
        if option_matches:
            title = content[:option_matches[0].start()].strip()
        else:
            title = content.strip()
        
        # 清理题干 - 移除答案括号部分
        title = re.sub(r'[（(]\s*[A-E](?:[,，、\s]*[A-E])*\s*[)）]', '____', title)
        title = re.sub(r'\s+', ' ', title).strip()
        result["title"] = title
        
        # 4. 如果没有从括号提取到答案，尝试其他格式
        if not result["answer"]:
            # 尝试 "答案：A" 格式
            ans_match = re.search(r'答案[：:]\s*([A-E,，、\s]+)', content)
            if ans_match:
                answers = re.findall(r'[A-E]', ans_match.group(1))
                result["answer"] = ','.join(answers)
        
        # 5. 尝试判断题格式 (答案为"对/错"或"正确/错误"或"√/×")
        if not result["answer"]:
            tf_match = re.search(r'答案[：:]\s*(对|错|正确|错误|√|×|是|否)', content)
            if tf_match:
                ans = tf_match.group(1)
                if ans in ['对', '正确', '√', '是']:
                    result["answer"] = "对"
                else:
                    result["answer"] = "错"
        
        # 6. 尝试从题干末尾的括号提取（可能答案在最后）
        if not result["answer"]:
            # 检查内容末尾是否有答案格式
            end_ans = re.search(r'[（(]\s*([A-E])\s*[)）]\s*$', content)
            if end_ans:
                result["answer"] = end_ans.group(1)
        
        # 验证必要字段并返回详细错误
        if not result["title"]:
            return None, "题干为空"
        
        if not result["answer"]:
            return None, f"未找到答案（题干：{result['title'][:50]}...）"
        
        return result, None
    
    def _parse_exam_text(self, text: str) -> Tuple[List[QuestionCreate], List[Dict]]:
        """
        解析考试文本，支持多种格式
        格式1: 1. 题干（A）选项内容  A、xxx B、xxx
        格式2: 1. 题干  A、xxx B、xxx  答案：A
        """
        questions = []
        errors = []
        
        # 当前题型（默认单选）
        current_type = QuestionType.SINGLE_CHOICE
        
        # 按行分割
        lines = text.split('\n')
        
        i = 0
        question_num = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # 识别题型标题 (支持多种格式: 一、单选题 / 【单选题】 / 第一部分 等)
            type_match = re.match(r'^([一二三四五六七八九十]+[、.．]|【|第.+部分)', line)
            if type_match or '单选' in line or '多选' in line or '判断' in line or '填空' in line or '简答' in line:
                if '单选' in line:
                    current_type = QuestionType.SINGLE_CHOICE
                    i += 1
                    continue
                elif '多选' in line:
                    current_type = QuestionType.MULTIPLE_CHOICE
                    i += 1
                    continue
                elif '判断' in line:
                    current_type = QuestionType.TRUE_FALSE
                    i += 1
                    continue
                elif '填空' in line:
                    current_type = QuestionType.FILL_BLANK
                    i += 1
                    continue
                elif '简答' in line:
                    current_type = QuestionType.SHORT_ANSWER
                    i += 1
                    continue
                # 如果只是部分标题但没有题型信息，也跳过
                if type_match and not re.match(r'^\d+[、.．]', line):
                    i += 1
                    continue
            
            # 识别题目（数字开头）
            question_match = re.match(r'^(\d+)[\.、．\s]+(.+)', line)
            if question_match:
                question_num += 1
                title_text = question_match.group(2).strip()
                
                # 收集后续行直到下一题或题型标题
                content_lines = [title_text]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    # 如果是新题目或题型标题，停止
                    if re.match(r'^(\d+)[\.、．\s]+', next_line):
                        break
                    if re.match(r'^[一二三四五六七八九十]+[、.．]', next_line):
                        break
                    if next_line:
                        content_lines.append(next_line)
                    j += 1
                
                # 合并内容
                full_content = ' '.join(content_lines)
                
                # 解析题目
                parsed = self._parse_single_question(full_content, current_type)
                
                if parsed:
                    try:
                        # 判断是否多选（答案有多个字母）
                        answer = parsed.get("answer", "")
                        if len(re.findall(r'[A-E]', answer)) > 1:
                            q_type = QuestionType.MULTIPLE_CHOICE
                        else:
                            q_type = parsed.get("type", current_type)
                        
                        questions.append(QuestionCreate(
                            question_type=q_type,
                            title=parsed["title"],
                            options=parsed.get("options"),
                            answer=answer,
                            analysis=parsed.get("analysis"),
                            difficulty=DifficultyLevel.MEDIUM,
                            knowledge_ids=[]
                        ))
                    except Exception as e:
                        errors.append({
                            "row": question_num,
                            "error": f"解析错误: {str(e)}"
                        })
                else:
                    errors.append({
                        "row": question_num,
                        "error": f"无法解析题目"
                    })
                
                i = j
                continue
            
            i += 1
        
        return questions, errors
    
    def _parse_single_question(self, content: str, default_type: QuestionType) -> Dict:
        """解析单个题目"""
        result = {
            "type": default_type,
            "title": "",
            "options": {},
            "answer": "",
            "analysis": ""
        }
        
        # 尝试从题干中提取答案（格式：xxx（A）xxx 或 xxx（A,B,C）xxx 或 xxx（A、B、C）xxx）
        answer_in_title = re.search(r'[（(]\s*([A-E](?:[,，、\s]*[A-E])*)\s*[)）]', content)
        if answer_in_title:
            answer_text = answer_in_title.group(1)
            answers = re.findall(r'[A-E]', answer_text)
            result["answer"] = ','.join(answers) if len(answers) > 1 else (answers[0] if answers else "")
        
        # 提取选项 - 改进的正则表达式
        # 格式: A、xxx B、xxx 或 A. xxx B. xxx (选项可能包含特殊字符、空格等)
        options = {}
        
        # 先找到所有选项的位置
        option_positions = []
        for m in re.finditer(r'([A-E])[、.．:：]\s*', content):
            option_positions.append((m.group(1), m.start(), m.end()))
        
        # 根据位置提取每个选项的内容
        for idx, (letter, start, text_start) in enumerate(option_positions):
            if idx + 1 < len(option_positions):
                # 下一个选项的开始位置
                next_start = option_positions[idx + 1][1]
                opt_text = content[text_start:next_start].strip()
            else:
                # 最后一个选项，取到内容末尾
                opt_text = content[text_start:].strip()
            
            # 清理选项文本（去除末尾可能的换行和多余空格）
            opt_text = re.sub(r'\s+', ' ', opt_text).strip()
            if opt_text:
                options[letter] = opt_text
        
        result["options"] = options if options else None
        
        # 提取题干（去除选项部分）
        title = content
        if option_positions:
            first_option_start = option_positions[0][1]
            title = content[:first_option_start].strip()
        
        # 清理题干
        title = re.sub(r'\s+', ' ', title).strip()
        result["title"] = title
        
        # 如果没有从题干提取到答案，尝试查找"答案："格式
        if not result["answer"]:
            answer_match = re.search(r'答案[：:]\s*([A-E,，、\s]+)', content)
            if answer_match:
                answers = re.findall(r'[A-E]', answer_match.group(1))
                result["answer"] = ','.join(answers) if len(answers) > 1 else (answers[0] if answers else "")
        
        # 提取解析
        analysis_match = re.search(r'解析[：:]\s*(.+?)(?=\d+[\.、]|$)', content, re.DOTALL)
        if analysis_match:
            result["analysis"] = analysis_match.group(1).strip()
        
        # 验证必要字段
        if not result["title"] or not result["answer"]:
            return None
        
        return result
    
    # ==================== OCR识别导入 ====================
    
    def import_from_image(self, file_path: str, creator_id: int = None) -> ImportResult:
        """
        从图片OCR识别导入题库
        使用PaddleOCR进行文字识别
        """
        try:
            # 图片预处理
            from PIL import Image
            import numpy as np
            
            img = Image.open(file_path)
            
            # 转换为灰度图
            if img.mode != 'L':
                img = img.convert('L')
            
            # 调整大小（如果太大）
            max_size = 2000
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            img_array = np.array(img)
            
            # OCR识别
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            result = ocr.ocr(img_array, cls=True)
            
            # 提取文本
            texts = []
            for line in result:
                if line:
                    for item in line:
                        if item and len(item) >= 2:
                            texts.append(item[1][0])
            
            raw_text = "\n".join(texts)
            
            # 解析题目
            questions, errors = self._parse_ocr_text(raw_text)
            
            if not questions:
                return ImportResult(
                    success=False,
                    total=0,
                    success_count=0,
                    fail_count=1,
                    errors=[{"row": 0, "error": "未识别到有效题目"}]
                )
            
            # 批量创建
            from app.services.question_service import QuestionService
            question_service = QuestionService(self.db)
            created = question_service.create_questions_batch(questions, creator_id)
            
            return ImportResult(
                success=True,
                total=len(questions) + len(errors),
                success_count=len(created),
                fail_count=len(errors),
                errors=errors
            )
            
        except ImportError:
            return ImportResult(
                success=False,
                total=0,
                success_count=0,
                fail_count=1,
                errors=[{"row": 0, "error": "PaddleOCR未安装，请先安装: pip install paddleocr"}]
            )
        except Exception as e:
            return ImportResult(
                success=False,
                total=0,
                success_count=0,
                fail_count=1,
                errors=[{"row": 0, "error": f"OCR识别失败: {str(e)}"}]
            )
    
    def ocr_preview(self, file_path: str) -> Dict[str, Any]:
        """
        OCR预览（不入库）
        返回识别结果供用户确认
        """
        try:
            from PIL import Image
            import numpy as np
            from paddleocr import PaddleOCR
            
            img = Image.open(file_path)
            if img.mode != 'L':
                img = img.convert('L')
            
            img_array = np.array(img)
            
            ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            result = ocr.ocr(img_array, cls=True)
            
            texts = []
            for line in result:
                if line:
                    for item in line:
                        if item and len(item) >= 2:
                            texts.append(item[1][0])
            
            raw_text = "\n".join(texts)
            questions, errors = self._parse_ocr_text(raw_text)
            
            return {
                "success": True,
                "raw_text": raw_text,
                "questions": [q.model_dump() for q in questions],
                "errors": errors
            }
            
        except Exception as e:
            return {
                "success": False,
                "raw_text": "",
                "questions": [],
                "errors": [str(e)]
            }
    
    def _parse_ocr_text(self, text: str) -> Tuple[List[QuestionCreate], List[Dict]]:
        """解析OCR识别的文本"""
        questions = []
        errors = []
        
        # 按题号分割
        pattern = r'(\d+)[\.、．\s]'
        parts = re.split(pattern, text)
        
        current_num = None
        current_content = []
        
        for part in parts:
            if re.match(r'^\d+$', part.strip()):
                # 保存上一题
                if current_num and current_content:
                    q = self._parse_single_question(current_num, "".join(current_content))
                    if q:
                        questions.append(q)
                    else:
                        errors.append({
                            "row": current_num,
                            "error": "题目格式无法识别"
                        })
                
                current_num = int(part.strip())
                current_content = []
            else:
                current_content.append(part)
        
        # 保存最后一题
        if current_num and current_content:
            q = self._parse_single_question(current_num, "".join(current_content))
            if q:
                questions.append(q)
        
        return questions, errors
    
    def _parse_single_question(self, num: int, content: str) -> QuestionCreate:
        """解析单个题目"""
        content = content.strip()
        if not content:
            return None
        
        # 识别题型
        question_type = QuestionType.SINGLE_CHOICE
        if "判断" in content[:10] or content.startswith("(") or content.startswith("（"):
            question_type = QuestionType.TRUE_FALSE
        elif "____" in content or "___" in content or "（）" in content or "()" in content:
            question_type = QuestionType.FILL_BLANK
        
        # 提取选项
        options = {}
        option_pattern = r'([A-D])[\.、．\s]([^A-D]+?)(?=[A-D][\.、．\s]|答案|$)'
        option_matches = re.findall(option_pattern, content, re.DOTALL)
        for opt_key, opt_value in option_matches:
            options[opt_key] = opt_value.strip()
        
        # 提取答案
        answer = ""
        answer_match = re.search(r'答案[：:]\s*([A-D]+|[对错√×]|.+?)(?=解析|$)', content)
        if answer_match:
            answer = answer_match.group(1).strip()
        
        # 提取题干
        title = content
        if options:
            # 移除选项部分
            first_option = re.search(r'[A-D][\.、．\s]', content)
            if first_option:
                title = content[:first_option.start()].strip()
        
        # 移除答案部分
        answer_pos = re.search(r'答案[：:]', title)
        if answer_pos:
            title = title[:answer_pos.start()].strip()
        
        if not title or not answer:
            return None
        
        return QuestionCreate(
            question_type=question_type,
            title=title,
            options=options if options else None,
            answer=answer,
            difficulty=DifficultyLevel.MEDIUM,
            knowledge_ids=[]
        )
    
    # ==================== 辅助方法 ====================
    
    def _parse_question_type(self, type_str: str) -> QuestionType:
        """解析题型字符串"""
        type_str = type_str.strip().lower()
        
        if "单选" in type_str or "single" in type_str:
            return QuestionType.SINGLE_CHOICE
        elif "多选" in type_str or "multiple" in type_str:
            return QuestionType.MULTIPLE_CHOICE
        elif "判断" in type_str or "true" in type_str or "false" in type_str:
            return QuestionType.TRUE_FALSE
        elif "填空" in type_str or "fill" in type_str:
            return QuestionType.FILL_BLANK
        elif "简答" in type_str or "short" in type_str:
            return QuestionType.SHORT_ANSWER
        else:
            return QuestionType.SINGLE_CHOICE
    
    def _parse_options(self, options_str: str) -> Dict[str, str]:
        """解析选项字符串"""
        if not options_str:
            return None
        
        options = {}
        
        # 尝试JSON格式
        try:
            return json.loads(options_str)
        except:
            pass
        
        # 尝试 A.xxx B.xxx 格式
        pattern = r'([A-Z])[\.、．]\s*([^A-Z]+)'
        matches = re.findall(pattern, options_str)
        for key, value in matches:
            options[key] = value.strip()
        
        return options if options else None
    
    def _parse_difficulty(self, difficulty_str: str) -> DifficultyLevel:
        """解析难度字符串"""
        if not difficulty_str:
            return DifficultyLevel.MEDIUM
        
        difficulty_str = difficulty_str.strip().lower()
        
        if "简单" in difficulty_str or "easy" in difficulty_str:
            return DifficultyLevel.EASY
        elif "困难" in difficulty_str or "hard" in difficulty_str:
            return DifficultyLevel.HARD
        else:
            return DifficultyLevel.MEDIUM
