/**
 * 楚然智考系统 - 考试管理API
 */
import request from './request'

export const examApi = {
  // 获取考试列表
  getExams(params) {
    return request.get('/exams', { params })
  },
  
  // 获取可参加的考试
  getAvailableExams() {
    return request.get('/exams/available')
  },
  
  // 获取考试详情
  getExam(id) {
    return request.get(`/exams/${id}`)
  },
  
  // 创建考试
  createExam(data) {
    return request.post('/exams', data)
  },
  
  // 更新考试
  updateExam(id, data) {
    return request.put(`/exams/${id}`, data)
  },
  
  // 删除考试
  deleteExam(id) {
    return request.delete(`/exams/${id}`)
  },
  
  // 发布考试
  publishExam(id) {
    return request.post(`/exams/${id}/publish`)
  },
  
  // 开始考试
  startExam(examId) {
    return request.post(`/exams/${examId}/start`)
  },
  
  // 提交考试
  submitExam(data) {
    return request.post('/exams/submit', data)
  },
  
  // 获取我的考试记录
  getMyRecords(params) {
    return request.get('/exams/records/my', { params })
  },
  
  // 获取考试记录详情
  getRecordDetail(id) {
    return request.get(`/exams/records/${id}`)
  },
  
  // 获取错题列表
  getWrongQuestions(params) {
    return request.get('/exams/wrong/list', { params })
  },
  
  // 更新错题状态
  updateWrongQuestion(id, data) {
    return request.put(`/exams/wrong/${id}`, data)
  }
}

export const statisticsApi = {
  // 获取学习统计
  getStudyStatistics() {
    return request.get('/statistics/study')
  },
  
  // 获取学习趋势
  getStudyTrend(days = 30) {
    return request.get('/statistics/study/trend', { params: { days } })
  },
  
  // 获取系统概览
  getSystemOverview() {
    return request.get('/statistics/overview')
  },
  
  // 获取考试统计
  getExamStatistics(examId) {
    return request.get(`/statistics/exam/${examId}`)
  }
}
