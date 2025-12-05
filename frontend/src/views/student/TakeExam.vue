<template>
  <div class="take-exam" v-if="examStore.currentExam">
    <!-- 顶部信息栏 -->
    <div class="exam-header">
      <div class="header-left">
        <div class="back-btn" @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
        </div>
        <div class="exam-title">{{ examStore.currentExam.title }}</div>
      </div>
      <div class="header-center">
        <div class="exam-timer" :class="{ warning: remainingMinutes < 5 }" v-if="!isPracticeMode">
          <el-icon><Clock /></el-icon>
          <span>{{ formatTime(examStore.remainingTime) }}</span>
        </div>
        <div class="practice-stats" v-else>
          <span class="stat correct">
            <el-icon><CircleCheck /></el-icon>{{ correctCount }}
          </span>
          <span class="stat wrong">
            <el-icon><CircleClose /></el-icon>{{ wrongCount }}
          </span>
        </div>
      </div>
      <el-button type="danger" size="small" @click="handleSubmit">交卷</el-button>
    </div>
    
    <!-- 主内容区 -->
    <div class="exam-body">
      <!-- 左侧题目区 -->
      <div class="question-panel">
        <div class="question-card">
          <!-- 题目头部 -->
          <div class="question-header">
            <div class="question-meta">
              <span class="question-index">第 {{ examStore.currentIndex + 1 }} 题</span>
              <el-tag :type="questionTypeTag[currentQuestion?.question_type]" size="small" effect="plain">
                {{ questionTypeMap[currentQuestion?.question_type] }}
              </el-tag>
              <span class="question-score" v-if="!isPracticeMode">{{ currentQuestion?.score }}分</span>
            </div>
            <div class="question-hint" v-if="currentQuestion?.question_type === 'multiple_choice'">
              多选题，选完点击确认
            </div>
          </div>
          
          <!-- 题目内容 -->
          <div class="question-body">
            <div class="question-title">{{ currentQuestion?.title }}</div>
            
            <!-- 选择题选项 -->
            <div class="options-wrap" v-if="['single_choice', 'multiple_choice'].includes(currentQuestion?.question_type)">
              <div 
                v-for="(value, key) in currentQuestion?.options" 
                :key="key"
                class="option-item"
                :class="{ 
                  selected: isOptionSelected(key),
                  correct: showResult && isCorrectOption(key),
                  wrong: showResult && isOptionSelected(key) && !isCorrectOption(key),
                  disabled: showResult
                }"
                @click="handleOptionClick(key)"
              >
                <span class="option-key">{{ key }}</span>
                <span class="option-text">{{ value }}</span>
                <span class="option-status" v-if="showResult">
                  <el-icon v-if="isCorrectOption(key)" class="correct"><CircleCheck /></el-icon>
                  <el-icon v-else-if="isOptionSelected(key)" class="wrong"><CircleClose /></el-icon>
                </span>
              </div>
            </div>
            
            <!-- 判断题 -->
            <div class="options-wrap tf-options" v-else-if="currentQuestion?.question_type === 'true_false'">
              <div 
                class="option-item tf-item"
                :class="{ 
                  selected: currentAnswer === '对',
                  correct: showResult && currentQuestion?.answer === '对',
                  wrong: showResult && currentAnswer === '对' && currentQuestion?.answer !== '对',
                  disabled: showResult
                }"
                @click="handleTrueFalseClick('对')"
              >
                <span class="tf-icon correct-icon">✓</span>
                <span class="option-text">正确</span>
              </div>
              <div 
                class="option-item tf-item"
                :class="{ 
                  selected: currentAnswer === '错',
                  correct: showResult && currentQuestion?.answer === '错',
                  wrong: showResult && currentAnswer === '错' && currentQuestion?.answer !== '错',
                  disabled: showResult
                }"
                @click="handleTrueFalseClick('错')"
              >
                <span class="tf-icon wrong-icon">✗</span>
                <span class="option-text">错误</span>
              </div>
            </div>
            
            <!-- 填空题/简答题 -->
            <div class="text-answer" v-else>
              <el-input
                v-model="textAnswer"
                :type="currentQuestion?.question_type === 'short_answer' ? 'textarea' : 'text'"
                :rows="5"
                placeholder="请输入答案"
                @blur="saveTextAnswer"
              />
            </div>
          </div>
          
          <!-- 导航按钮 -->
          <div class="question-nav">
            <el-button 
              class="nav-btn prev"
              :disabled="examStore.currentIndex === 0"
              @click="goToPrev"
            >
              <el-icon><ArrowLeft /></el-icon>
              上一题
            </el-button>
            
            <!-- 多选确认按钮 -->
            <el-button 
              v-if="currentQuestion?.question_type === 'multiple_choice' && !showResult"
              class="nav-btn confirm"
              type="primary"
              @click="confirmMultipleChoice" 
              :disabled="!currentAnswer"
            >
              确认答案
            </el-button>
            <div v-else class="nav-placeholder"></div>
            
            <el-button 
              class="nav-btn next"
              type="primary"
              :disabled="examStore.currentIndex === examStore.totalQuestions - 1"
              @click="goToNext"
            >
              下一题
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          
          <!-- 答案解析 -->
          <div class="answer-result" v-if="showResult && isPracticeMode">
            <div class="result-banner" :class="isCurrentCorrect ? 'correct' : 'wrong'">
              <el-icon><component :is="isCurrentCorrect ? 'CircleCheck' : 'CircleClose'" /></el-icon>
              <span>{{ isCurrentCorrect ? '回答正确！' : '回答错误' }}</span>
            </div>
            <div class="result-detail">
              <div class="answer-row">
                <span class="label">正确答案：</span>
                <span class="value correct">{{ currentQuestion?.answer }}</span>
              </div>
              <div class="answer-row" v-if="!isCurrentCorrect">
                <span class="label">你的答案：</span>
                <span class="value wrong">{{ currentAnswer || '未作答' }}</span>
              </div>
              <div class="analysis-row" v-if="currentQuestion?.analysis">
                <span class="label">解析：</span>
                <p class="analysis-text">{{ currentQuestion.analysis }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 底部设置栏 -->
        <div class="settings-bar" v-if="isPracticeMode">
          <el-checkbox v-model="autoNext" size="small">答对自动下一题</el-checkbox>
        </div>
      </div>
      
      <!-- 右侧答题卡 (桌面端) -->
      <div class="answer-card-panel">
        <div class="card-header">
          <h4>答题卡</h4>
          <span class="progress">{{ examStore.answeredCount }}/{{ examStore.totalQuestions }}</span>
        </div>
        <div class="card-body">
          <div class="card-grid">
            <div 
              v-for="(q, index) in examStore.questions" 
              :key="q.id"
              class="card-num"
              :class="{ 
                current: index === examStore.currentIndex,
                answered: !isPracticeMode && examStore.isAnswered(q.id),
                correct: isPracticeMode && answeredResults[q.id] === true,
                wrong: isPracticeMode && answeredResults[q.id] === false
              }"
              @click="goToQuestion(index)"
            >
              {{ index + 1 }}
            </div>
          </div>
        </div>
        <div class="card-footer">
          <div class="legend">
            <span><i class="dot current"></i>当前</span>
            <span v-if="isPracticeMode"><i class="dot correct"></i>正确</span>
            <span v-if="isPracticeMode"><i class="dot wrong"></i>错误</span>
            <span v-if="!isPracticeMode"><i class="dot answered"></i>已答</span>
            <span><i class="dot"></i>未答</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 移动端底部答题卡按钮 -->
    <div class="mobile-card-btn" @click="showMobileCard = true">
      <el-icon><Grid /></el-icon>
      <span>{{ examStore.answeredCount }}/{{ examStore.totalQuestions }}</span>
    </div>
    
    <!-- 移动端答题卡弹出层 -->
    <el-drawer 
      v-model="showMobileCard" 
      direction="btt" 
      size="60%"
      :show-close="false"
      class="mobile-drawer"
    >
      <template #header>
        <div class="drawer-header">
          <span>答题卡</span>
          <span class="close-btn" @click="showMobileCard = false">完成</span>
        </div>
      </template>
      <div class="mobile-card-content">
        <div class="mobile-card-grid">
          <div 
            v-for="(q, index) in examStore.questions" 
            :key="q.id"
            class="mobile-card-item"
            :class="{ 
              current: index === examStore.currentIndex,
              answered: !isPracticeMode && examStore.isAnswered(q.id),
              correct: isPracticeMode && answeredResults[q.id] === true,
              wrong: isPracticeMode && answeredResults[q.id] === false
            }"
            @click="goToQuestionMobile(index)"
          >
            {{ index + 1 }}
          </div>
        </div>
        <div class="mobile-legend">
          <span><i class="dot current"></i>当前</span>
          <span v-if="isPracticeMode"><i class="dot correct"></i>正确</span>
          <span v-if="isPracticeMode"><i class="dot wrong"></i>错误</span>
          <span v-if="!isPracticeMode"><i class="dot answered"></i>已答</span>
          <span><i class="dot"></i>未答</span>
        </div>
      </div>
    </el-drawer>
  </div>
  
  <!-- 加载中 -->
  <div class="loading-container" v-else>
    <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    <p>正在加载考试...</p>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, Grid, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { useExamStore } from '@/stores/exam'
import { examApi } from '@/api/exam'

const router = useRouter()
const route = useRoute()
const examStore = useExamStore()

// 映射
const questionTypeMap = {
  single_choice: '单选题',
  multiple_choice: '多选题',
  true_false: '判断题',
  fill_blank: '填空题',
  short_answer: '简答题'
}

const questionTypeTag = {
  single_choice: 'primary',
  multiple_choice: 'success',
  true_false: 'warning',
  fill_blank: 'info',
  short_answer: 'danger'
}

// 状态
const showMobileCard = ref(false)
const autoNext = ref(true)
const textAnswer = ref('')
const answeredResults = reactive({}) // 记录每题对错 { questionId: true/false }
const showResultMap = reactive({}) // 记录哪些题已显示结果

// 是否练习模式
const isPracticeMode = computed(() => {
  return examStore.currentExam?.exam_type === 'practice'
})

// 当前题目
const currentQuestion = computed(() => examStore.currentQuestion)

// 当前答案
const currentAnswer = computed(() => {
  if (!currentQuestion.value) return ''
  return examStore.getAnswer(currentQuestion.value.id)
})

// 是否显示当前题结果
const showResult = computed(() => {
  if (!isPracticeMode.value) return false
  return showResultMap[currentQuestion.value?.id] || false
})

// 当前题是否正确
const isCurrentCorrect = computed(() => {
  if (!currentQuestion.value) return false
  return answeredResults[currentQuestion.value.id] === true
})

// 统计
const correctCount = computed(() => Object.values(answeredResults).filter(v => v === true).length)
const wrongCount = computed(() => Object.values(answeredResults).filter(v => v === false).length)
const accuracyRate = computed(() => {
  const total = correctCount.value + wrongCount.value
  if (total === 0) return 0
  return Math.round(correctCount.value / total * 100)
})

// 剩余分钟数
const remainingMinutes = computed(() => Math.floor(examStore.remainingTime / 60))

// 定时器
let timer = null

// 格式化时间
const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

// 检查选项是否选中
const isOptionSelected = (key) => {
  const answer = currentAnswer.value
  if (!answer) return false
  
  if (currentQuestion.value?.question_type === 'multiple_choice') {
    return answer.includes(key)
  }
  return answer === key
}

// 检查是否正确选项
const isCorrectOption = (key) => {
  if (!currentQuestion.value?.answer) return false
  return currentQuestion.value.answer.includes(key)
}

// 处理选项点击 (单选)
const handleOptionClick = (key) => {
  if (!currentQuestion.value) return
  if (showResult.value && isPracticeMode.value) return // 已显示结果，不能再选
  
  if (currentQuestion.value.question_type === 'single_choice') {
    examStore.setAnswer(currentQuestion.value.id, key)
    // 单选题自动提交
    if (isPracticeMode.value) {
      checkAnswer()
    } else {
      // 考试模式，直接跳转下一题
      if (examStore.currentIndex < examStore.totalQuestions - 1) {
        setTimeout(() => examStore.nextQuestion(), 300)
      }
    }
  } else if (currentQuestion.value.question_type === 'multiple_choice') {
    let answer = currentAnswer.value || ''
    if (answer.includes(key)) {
      answer = answer.replace(key, '')
    } else {
      answer = (answer + key).split('').sort().join('')
    }
    examStore.setAnswer(currentQuestion.value.id, answer)
  }
}

// 处理判断题点击
const handleTrueFalseClick = (value) => {
  if (!currentQuestion.value) return
  if (showResult.value && isPracticeMode.value) return
  
  examStore.setAnswer(currentQuestion.value.id, value)
  // 判断题自动提交
  if (isPracticeMode.value) {
    checkAnswer()
  } else {
    // 考试模式，直接跳转下一题
    if (examStore.currentIndex < examStore.totalQuestions - 1) {
      setTimeout(() => examStore.nextQuestion(), 300)
    }
  }
}

// 确认多选题答案
const confirmMultipleChoice = () => {
  if (isPracticeMode.value) {
    checkAnswer()
  } else {
    // 非练习模式，直接跳转下一题
    if (examStore.currentIndex < examStore.totalQuestions - 1) {
      setTimeout(() => examStore.nextQuestion(), 300)
    }
  }
}

// 检查答案并显示结果
const checkAnswer = () => {
  if (!currentQuestion.value) return
  
  const qId = currentQuestion.value.id
  const userAnswer = currentAnswer.value
  const correctAnswer = currentQuestion.value.answer
  
  // 判断是否正确
  let isCorrect = false
  if (currentQuestion.value.question_type === 'multiple_choice') {
    // 多选题：去除逗号后比较字符集合
    const userSet = new Set(userAnswer.toUpperCase().replace(/,|，/g, '').split(''))
    const correctSet = new Set(correctAnswer.toUpperCase().replace(/,|，/g, '').split(''))
    isCorrect = userSet.size === correctSet.size && [...userSet].every(c => correctSet.has(c))
  } else {
    isCorrect = userAnswer === correctAnswer
  }
  answeredResults[qId] = isCorrect
  showResultMap[qId] = true
  
  // 如果答对且开启自动下一题
  if (isCorrect && autoNext.value) {
    setTimeout(() => {
      if (examStore.currentIndex < examStore.totalQuestions - 1) {
        examStore.nextQuestion()
      }
    }, 800)
  }
}

// 保存文本答案
const saveTextAnswer = () => {
  if (!currentQuestion.value) return
  examStore.setAnswer(currentQuestion.value.id, textAnswer.value)
}

// 上一题
const goToPrev = () => {
  examStore.prevQuestion()
}

// 下一题
const goToNext = () => {
  examStore.nextQuestion()
}

// 跳转到指定题目
const goToQuestion = (index) => {
  examStore.goToQuestion(index)
}

// 移动端跳转题目
const goToQuestionMobile = (index) => {
  examStore.goToQuestion(index)
  showMobileCard.value = false
}

// 返回
const handleBack = async () => {
  try {
    await ElMessageBox.confirm('确定要退出吗？当前答题进度将会丢失。', '提示', {
      confirmButtonText: '确定退出',
      cancelButtonText: '继续答题',
      type: 'warning'
    })
    examStore.clearExam()
    router.back()
  } catch {}
}

// 监听题目变化，更新文本答案
watch(currentQuestion, (q) => {
  if (q && ['fill_blank', 'short_answer'].includes(q.question_type)) {
    textAnswer.value = examStore.getAnswer(q.id) || ''
  }
}, { immediate: true })

// 交卷
const handleSubmit = async () => {
  const unanswered = examStore.unansweredCount
  
  let message = '确定要交卷吗？'
  if (unanswered > 0) {
    message = `还有 ${unanswered} 道题未作答，确定要交卷吗？`
  }
  
  try {
    await ElMessageBox.confirm(message, '交卷确认', {
      confirmButtonText: '确定交卷',
      cancelButtonText: '继续答题',
      type: 'warning'
    })
    
    examStore.isSubmitting = true
    
    const submitData = examStore.getSubmitData()
    const res = await examApi.submitExam(submitData)
    
    ElMessage.success('交卷成功')
    examStore.clearExam()
    
    router.replace(`/exam-result/${res.data.id}`)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('交卷失败:', error)
    }
    examStore.isSubmitting = false
  }
}

// 自动交卷
const autoSubmit = () => {
  if (examStore.remainingTime <= 0 && !examStore.isSubmitting) {
    ElMessage.warning('考试时间到，自动交卷')
    handleSubmit()
  }
}

// 开始考试
const startExam = async () => {
  try {
    const res = await examApi.startExam(route.params.id)
    examStore.initExam(res.data)
    
    // 非练习模式启动定时器
    if (!isPracticeMode.value) {
      timer = setInterval(() => {
        if (examStore.remainingTime <= 0) {
          autoSubmit()
        }
      }, 1000)
    }
  } catch (error) {
    console.error('开始考试失败:', error)
    ElMessage.error('开始考试失败')
    router.back()
  }
}

// 防止刷新丢失
const handleBeforeUnload = (e) => {
  if (examStore.currentExam) {
    e.preventDefault()
    e.returnValue = ''
  }
}

onMounted(() => {
  startExam()
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
</script>

<style lang="scss" scoped>
.take-exam {
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #f0f4f8 0%, #e8ecf1 100%);
  overflow: hidden;
  
  // 顶部导航
  .exam-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 54px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    z-index: 1000;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .back-btn {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: rgba(255,255,255,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        cursor: pointer;
        transition: all 0.2s;
        
        &:hover {
          background: rgba(255,255,255,0.25);
        }
      }
      
      .exam-title {
        font-size: 16px;
        font-weight: 600;
        color: #fff;
        max-width: 150px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
    
    .header-center {
      .exam-timer {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 18px;
        font-weight: 700;
        color: #fff;
        
        &.warning {
          animation: pulse 1s infinite;
        }
      }
      
      .practice-stats {
        display: flex;
        gap: 16px;
        
        .stat {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 15px;
          font-weight: 600;
          color: #fff;
          
          &.correct { color: #a5f3a6; }
          &.wrong { color: #fca5a5; }
        }
      }
    }
    
    > .el-button {
      background: rgba(255,255,255,0.9);
      color: #764ba2;
      border: none;
      font-weight: 600;
    }
  }
  
  // 主体区域
  .exam-body {
    position: absolute;
    top: 54px;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: stretch;
    padding: 8px 20px;
    gap: 16px;
    max-width: 1400px;
    margin: 0 auto;
    box-sizing: border-box;
    overflow: hidden;
  }
  
  // 左侧题目区
  .question-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    height: 100%;
    
    .question-card {
      background: #fff;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.06);
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      height: 100%;
      
      .question-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        padding-bottom: 12px;
        border-bottom: 1px solid #f0f0f0;
        
        .question-meta {
          display: flex;
          align-items: center;
          gap: 10px;
          
          .question-index {
            font-size: 16px;
            font-weight: 700;
            color: #667eea;
          }
          
          .question-score {
            font-size: 13px;
            color: #999;
          }
        }
        
        .question-hint {
          font-size: 12px;
          color: #e6a23c;
          background: #fdf6ec;
          padding: 4px 10px;
          border-radius: 12px;
        }
      }
      
      .question-body {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 8px;
        
        &::-webkit-scrollbar {
          width: 6px;
        }
        &::-webkit-scrollbar-thumb {
          background: #d0d5dd;
          border-radius: 3px;
        }
        &::-webkit-scrollbar-track {
          background: transparent;
        }
        
        .question-title {
          font-size: 16px;
          line-height: 1.7;
          color: #333;
          margin-bottom: 16px;
        }
        
        .options-wrap {
          .option-item {
            display: flex;
            align-items: flex-start;
            padding: 12px 16px;
            margin-bottom: 10px;
            border: 2px solid #eef0f5;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.25s ease;
            background: #fafbfc;
            
            &:hover:not(.disabled) {
              border-color: #667eea;
              background: #f8f9ff;
              transform: translateX(4px);
            }
            
            &.selected:not(.correct):not(.wrong) {
              border-color: #667eea;
              background: linear-gradient(135deg, #f0f3ff 0%, #e8ecff 100%);
              
              .option-key {
                width: 32px !important;
                height: 32px !important;
                min-width: 32px !important;
                max-width: 32px !important;
                border-radius: 50% !important;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: #fff;
              }
            }
            
            &.correct {
              border-color: #52c41a;
              background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
              
              .option-key {
                width: 32px !important;
                height: 32px !important;
                min-width: 32px !important;
                max-width: 32px !important;
                border-radius: 50% !important;
                background: linear-gradient(135deg, #52c41a, #73d13d);
                color: #fff;
              }
            }
            
            &.wrong {
              border-color: #ff4d4f;
              background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
              
              .option-key {
                width: 32px !important;
                height: 32px !important;
                min-width: 32px !important;
                max-width: 32px !important;
                border-radius: 50% !important;
                background: linear-gradient(135deg, #ff4d4f, #ff7875);
                color: #fff;
              }
            }
            
            &.disabled {
              cursor: default;
            }
            
            .option-key {
              width: 32px !important;
              height: 32px !important;
              min-width: 32px !important;
              max-width: 32px !important;
              border-radius: 50% !important;
              background: linear-gradient(135deg, #e8ecf1 0%, #dde2e8 100%);
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 14px;
              font-weight: 600;
              margin-right: 14px;
              flex-shrink: 0;
              transition: all 0.25s;
              color: #666;
              box-sizing: border-box;
            }
            
            .option-text {
              flex: 1;
              line-height: 1.7;
              color: #333;
              padding-top: 4px;
            }
            
            .option-status {
              margin-left: 10px;
              font-size: 20px;
              
              .correct { color: #52c41a; }
              .wrong { color: #ff4d4f; }
            }
          }
          
          &.tf-options {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            
            .tf-item {
              justify-content: center;
              padding: 24px 20px;
              
              .tf-icon {
                width: 44px;
                height: 44px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                margin-right: 12px;
                background: #f5f5f5;
                
                &.correct-icon { color: #52c41a; }
                &.wrong-icon { color: #ff4d4f; }
              }
              
              .option-text {
                font-size: 16px;
                font-weight: 600;
              }
            }
          }
        }
      }
      
      // 导航按钮
      .question-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: auto;
        padding-top: 16px;
        border-top: 1px dashed #e8e8e8;
        flex-shrink: 0;
        
        .nav-btn {
          min-width: 100px;
          height: 40px;
          border-radius: 20px;
          font-size: 14px;
          
          &.prev {
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            color: #666;
            
            &:hover:not(:disabled) {
              background: #ebebeb;
              border-color: #d0d0d0;
            }
          }
          
          &.confirm {
            min-width: 120px;
            height: 42px;
            font-size: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
            
            &:hover:not(:disabled) {
              opacity: 0.9;
            }
          }
          
          &.next {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            
            &:hover:not(:disabled) {
              opacity: 0.9;
            }
          }
        }
        
        .nav-placeholder {
          width: 120px;
        }
      }
      
      .answer-result {
        margin-top: 20px;
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #f0f0f0;
        
        .result-banner {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 14px;
          font-size: 16px;
          font-weight: 600;
          
          &.correct {
            background: linear-gradient(135deg, #d9f7be 0%, #b7eb8f 100%);
            color: #389e0d;
          }
          
          &.wrong {
            background: linear-gradient(135deg, #ffccc7 0%, #ffa39e 100%);
            color: #cf1322;
          }
          
          .el-icon {
            font-size: 20px;
          }
        }
        
        .result-detail {
          padding: 16px 20px;
          background: #fafafa;
          
          .answer-row {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            font-size: 14px;
            
            .label {
              color: #666;
              margin-right: 8px;
            }
            
            .value {
              font-weight: 600;
              
              &.correct { color: #52c41a; }
              &.wrong { color: #ff4d4f; }
            }
          }
          
          .analysis-row {
            .label {
              color: #666;
              font-size: 14px;
            }
            
            .analysis-text {
              margin-top: 8px;
              font-size: 14px;
              color: #666;
              line-height: 1.7;
            }
          }
        }
      }
    }
    
    // 底部设置栏
    .settings-bar {
      background: #fff;
      border-radius: 12px;
      padding: 12px 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 12px rgba(0,0,0,0.04);
      
      .el-checkbox {
        font-size: 13px;
      }
    }
  }
  
  // 右侧答题卡 (桌面端)
  .answer-card-panel {
    width: 480px;
    flex-shrink: 0;
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 14px;
      border-bottom: 1px solid #f0f0f0;
      flex-shrink: 0;
      
      h4 {
        font-size: 18px;
        font-weight: 600;
        color: #333;
      }
      
      .progress {
        font-size: 15px;
        color: #667eea;
        font-weight: 600;
        background: linear-gradient(135deg, #f0f3ff 0%, #e8ecff 100%);
        padding: 6px 14px;
        border-radius: 20px;
      }
    }
    
    .card-body {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      
      &::-webkit-scrollbar {
        width: 6px;
      }
      &::-webkit-scrollbar-thumb {
        background: #e0e0e0;
        border-radius: 3px;
      }
      &::-webkit-scrollbar-track {
        background: transparent;
      }
      
      .card-grid {
        display: grid;
        grid-template-columns: repeat(8, 44px);
        gap: 10px;
        justify-content: start;
        
        .card-num {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          background: #f5f7fa;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          color: #666;
          
          &:hover {
            background: #e8ecf1;
            transform: scale(1.08);
          }
          
          &.current {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
          }
          
          &.answered {
            background: linear-gradient(135deg, #909399, #a6a9ad);
            color: #fff;
          }
          
          &.correct {
            background: linear-gradient(135deg, #52c41a, #73d13d);
            color: #fff;
          }
          
          &.wrong {
            background: linear-gradient(135deg, #ff4d4f, #ff7875);
            color: #fff;
          }
        }
      }
    }
    
    .card-footer {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
      
      .legend {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        
        span {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: #666;
          
          .dot {
            width: 14px;
            height: 14px;
            border-radius: 4px;
            background: #f5f7fa;
            
            &.current { background: linear-gradient(135deg, #667eea, #764ba2); }
            &.correct { background: #52c41a; }
            &.wrong { background: #ff4d4f; }
            &.answered { background: #909399; }
          }
        }
      }
    }
  }
  
  // 移动端答题卡按钮
  .mobile-card-btn {
    display: none;
    position: fixed;
    right: 16px;
    bottom: 100px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
    cursor: pointer;
    z-index: 100;
    
    .el-icon {
      font-size: 20px;
    }
    
    span {
      font-size: 11px;
      font-weight: 600;
    }
  }
}

// 移动端答题卡内容
.mobile-card-content {
  padding: 20px;
  
  .mobile-card-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    
    .mobile-card-item {
      aspect-ratio: 1;
      border-radius: 10px;
      background: #f5f7fa;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      color: #999;
      
      &.current {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #fff;
      }
      
      &.answered {
        background: #909399;
        color: #fff;
      }
      
      &.correct {
        background: #52c41a;
        color: #fff;
      }
      
      &.wrong {
        background: #ff4d4f;
        color: #fff;
      }
    }
  }
  
  .mobile-legend {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 20px;
    
    span {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: #999;
      
      .dot {
        width: 12px;
        height: 12px;
        border-radius: 4px;
        background: #f5f7fa;
        
        &.current { background: linear-gradient(135deg, #667eea, #764ba2); }
        &.correct { background: #52c41a; }
        &.wrong { background: #ff4d4f; }
        &.answered { background: #909399; }
      }
    }
  }
}

// 移动端抽屉样式
:deep(.mobile-drawer) {
  .el-drawer__header {
    padding: 16px 20px;
    margin-bottom: 0;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .drawer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    font-size: 16px;
    font-weight: 600;
    
    .close-btn {
      color: #667eea;
      cursor: pointer;
    }
  }
}

.loading-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  
  p {
    margin-top: 15px;
    color: #999;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

// 响应式 - 平板
@media (max-width: 1024px) {
  .take-exam {
    .answer-card-panel {
      width: 280px;
      padding: 20px;
      
      .card-body .card-grid {
        grid-template-columns: repeat(6, 1fr);
        gap: 8px;
        
        .card-num {
          width: 32px;
          height: 32px;
          font-size: 13px;
        }
      }
    }
  }
}

// 响应式 - 手机
@media (max-width: 768px) {
  .take-exam {
    .exam-header {
      .header-left .exam-title {
        max-width: 100px;
        font-size: 14px;
      }
      
      .header-center {
        .exam-timer {
          font-size: 16px;
        }
        
        .practice-stats {
          gap: 12px;
          
          .stat {
            font-size: 14px;
          }
        }
      }
    }
    
    .exam-body {
      padding: 62px 12px 80px;
    }
    
    .question-panel {
      .question-card {
        padding: 18px;
        border-radius: 16px;
        
        .question-header {
          flex-direction: column;
          align-items: flex-start;
          gap: 8px;
          margin-bottom: 16px;
          padding-bottom: 12px;
        }
        
        .question-body {
          .question-title {
            font-size: 15px;
            margin-bottom: 20px;
          }
          
          .options-wrap {
            .option-item {
              padding: 12px 14px;
              margin-bottom: 10px;
              border-radius: 12px;
              
              .option-key {
                width: 28px !important;
                height: 28px !important;
                min-width: 28px !important;
                max-width: 28px !important;
                border-radius: 50% !important;
                font-size: 13px;
                margin-right: 12px;
              }
              
              .option-text {
                font-size: 14px;
              }
            }
            
            &.tf-options {
              gap: 12px;
              
              .tf-item {
                padding: 18px 16px;
                
                .tf-icon {
                  width: 36px;
                  height: 36px;
                  font-size: 20px;
                }
                
                .option-text {
                  font-size: 15px;
                }
              }
            }
          }
        }
        
        .question-nav {
          margin-top: 14px;
          padding-top: 14px;
          
          .nav-btn {
            min-width: 75px;
            height: 36px;
            font-size: 13px;
            
            &.confirm {
              min-width: 95px;
              height: 38px;
            }
          }
          
          .nav-placeholder {
            width: 95px;
          }
        }
      }
      
      .settings-bar {
        padding: 10px 16px;
      }
    }
    
    .answer-card-panel {
      display: none;
    }
    
    .mobile-card-btn {
      display: flex;
      bottom: 20px;
    }
  }
}

// 超小屏幕
@media (max-width: 375px) {
  .take-exam {
    .exam-header {
      padding: 0 12px;
      
      .header-left {
        gap: 8px;
        
        .back-btn {
          width: 32px;
          height: 32px;
        }
        
        .exam-title {
          max-width: 80px;
        }
      }
    }
    
    .question-panel {
      .question-card {
        padding: 14px;
        
        .question-nav {
          .nav-btn {
            min-width: 70px;
            font-size: 12px;
            
            &.confirm {
              min-width: 90px;
            }
          }
          
          .nav-placeholder {
            width: 90px;
          }
        }
      }
    }
  }
}
</style>
