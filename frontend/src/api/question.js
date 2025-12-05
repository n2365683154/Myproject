/**
 * 楚然智考系统 - 题库管理API
 */
import request from './request'

export const questionApi = {
  // 获取题目列表
  getQuestions(params) {
    return request.get('/questions', { params })
  },
  
  // 获取题目详情
  getQuestion(id) {
    return request.get(`/questions/${id}`)
  },
  
  // 创建题目
  createQuestion(data) {
    return request.post('/questions', data)
  },
  
  // 批量创建题目
  createQuestionsBatch(data) {
    return request.post('/questions/batch', data)
  },
  
  // 更新题目
  updateQuestion(id, data) {
    return request.put(`/questions/${id}`, data)
  },
  
  // 删除题目
  deleteQuestion(id) {
    return request.delete(`/questions/${id}`)
  },
  
  // 删除所有题目
  deleteAllQuestions() {
    return request.delete('/questions/all')
  },
  
  // 获取题库统计
  getStatistics() {
    return request.get('/questions/statistics')
  },
  
  // 获取知识点树
  getKnowledgeTree() {
    return request.get('/questions/knowledge/tree')
  },
  
  // 获取知识点列表
  getKnowledgePoints(params) {
    return request.get('/questions/knowledge/list', { params })
  },
  
  // 创建知识点
  createKnowledgePoint(data) {
    return request.post('/questions/knowledge', data)
  },
  
  // 更新知识点
  updateKnowledgePoint(id, data) {
    return request.put(`/questions/knowledge/${id}`, data)
  },
  
  // 删除知识点
  deleteKnowledgePoint(id) {
    return request.delete(`/questions/knowledge/${id}`)
  }
}

export const importApi = {
  // Excel导入
  importExcel(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/imports/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // Word导入
  importWord(file, bankName) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('bank_name', bankName)
    return request.post('/imports/word', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // OCR导入
  importOcr(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/imports/ocr', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // OCR预览
  ocrPreview(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/imports/ocr/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // PDF导入
  importPdf(file, bankName) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('bank_name', bankName)
    return request.post('/imports/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // PDF预览
  pdfPreview(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/imports/pdf/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // 下载模板
  downloadTemplate() {
    return request.get('/imports/template/excel', {
      responseType: 'blob'
    })
  },
  
  // 获取题库列表
  getBanks(params) {
    return request.get('/imports/banks', { params })
  },
  
  // 获取题库详情
  getBank(id) {
    return request.get(`/imports/banks/${id}`)
  },
  
  // 删除题库
  deleteBank(id) {
    return request.delete(`/imports/banks/${id}`)
  }
}
