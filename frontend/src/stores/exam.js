/**
 * 楚然智考系统 - 考试状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useExamStore = defineStore('exam', () => {
  // 当前考试状态
  const currentExam = ref(null)
  const currentRecord = ref(null)
  const questions = ref([])
  const answers = ref({}) // { questionId: answer }
  const currentIndex = ref(0)
  const startTime = ref(null)
  const endTime = ref(null)
  const isSubmitting = ref(false)
  
  // 计算属性
  const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
  const totalQuestions = computed(() => questions.value.length)
  const answeredCount = computed(() => Object.keys(answers.value).length)
  const unansweredCount = computed(() => totalQuestions.value - answeredCount.value)
  
  // 剩余时间（秒）
  const remainingTime = computed(() => {
    if (!endTime.value) return 0
    const now = Date.now()
    const end = new Date(endTime.value).getTime()
    return Math.max(0, Math.floor((end - now) / 1000))
  })
  
  // 进度百分比
  const progress = computed(() => {
    if (totalQuestions.value === 0) return 0
    return Math.round((answeredCount.value / totalQuestions.value) * 100)
  })
  
  // 初始化考试
  const initExam = (examData) => {
    currentExam.value = examData.exam
    currentRecord.value = { id: examData.record_id }
    questions.value = examData.questions || []
    answers.value = {}
    currentIndex.value = 0
    startTime.value = examData.start_time
    endTime.value = examData.end_time
    isSubmitting.value = false
  }
  
  // 设置答案
  const setAnswer = (questionId, answer) => {
    answers.value[questionId] = answer
  }
  
  // 获取答案
  const getAnswer = (questionId) => {
    return answers.value[questionId] || ''
  }
  
  // 跳转到指定题目
  const goToQuestion = (index) => {
    if (index >= 0 && index < totalQuestions.value) {
      currentIndex.value = index
    }
  }
  
  // 上一题
  const prevQuestion = () => {
    if (currentIndex.value > 0) {
      currentIndex.value--
    }
  }
  
  // 下一题
  const nextQuestion = () => {
    if (currentIndex.value < totalQuestions.value - 1) {
      currentIndex.value++
    }
  }
  
  // 获取提交数据
  const getSubmitData = () => {
    return {
      record_id: currentRecord.value?.id,
      answers: Object.entries(answers.value).map(([questionId, answer]) => ({
        question_id: parseInt(questionId),
        answer: answer
      }))
    }
  }
  
  // 清除考试状态
  const clearExam = () => {
    currentExam.value = null
    currentRecord.value = null
    questions.value = []
    answers.value = {}
    currentIndex.value = 0
    startTime.value = null
    endTime.value = null
    isSubmitting.value = false
  }
  
  // 检查题目是否已答
  const isAnswered = (questionId) => {
    return !!answers.value[questionId]
  }
  
  return {
    currentExam,
    currentRecord,
    questions,
    answers,
    currentIndex,
    startTime,
    endTime,
    isSubmitting,
    currentQuestion,
    totalQuestions,
    answeredCount,
    unansweredCount,
    remainingTime,
    progress,
    initExam,
    setAnswer,
    getAnswer,
    goToQuestion,
    prevQuestion,
    nextQuestion,
    getSubmitData,
    clearExam,
    isAnswered
  }
})
