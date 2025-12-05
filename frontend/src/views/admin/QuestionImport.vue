<template>
  <div class="question-import">
    <h1 class="page-title">导入题库</h1>
    
    <el-tabs v-model="activeTab" class="import-tabs">
      <!-- Excel导入 -->
      <el-tab-pane label="Excel导入" name="excel">
        <div class="card">
          <div class="import-tips">
            <h4>导入说明：</h4>
            <ul>
              <li>支持 .xlsx 格式文件</li>
              <li>第一行为表头，从第二行开始为数据</li>
              <li>列顺序：题型 | 题干 | 选项 | 答案 | 解析 | 知识点 | 难度</li>
              <li>题型：单选题/多选题/判断题/填空题/简答题</li>
              <li>选项格式：A.选项A B.选项B C.选项C D.选项D</li>
            </ul>
            <el-button type="primary" link @click="downloadTemplate">
              <el-icon><Download /></el-icon>
              下载模板
            </el-button>
          </div>
          
          <el-upload
            ref="excelUploadRef"
            class="upload-area"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            :on-change="handleExcelChange"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">只能上传 xlsx/xls 文件，且不超过10MB</div>
            </template>
          </el-upload>
          
          <div class="upload-actions">
            <el-button 
              type="primary" 
              :loading="importing" 
              :disabled="!excelFile"
              @click="handleExcelImport"
            >
              开始导入
            </el-button>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- Word导入 -->
      <el-tab-pane label="Word导入" name="word">
        <div class="card">
          <div class="import-tips">
            <h4>导入说明：</h4>
            <ul>
              <li>支持 .docx 格式文件</li>
              <li>使用【选择题】、【多选题】、【判断题】、【填空题】标题区分题型</li>
              <li>题目格式：1. 题干内容</li>
              <li>选项格式：A. 选项内容</li>
              <li>答案格式：答案：A 或 题干中包含（A）</li>
            </ul>
          </div>
          
          <el-form :model="wordForm" label-width="100px" class="import-form">
            <el-form-item label="题库名称" required>
              <el-input 
                v-model="wordForm.bankName" 
                placeholder="请输入题库名称，如：辐射安全考核试题"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-form>
          
          <el-upload
            ref="wordUploadRef"
            class="upload-area"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".docx,.doc"
            :on-change="handleWordChange"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">只能上传 docx/doc 文件，且不超过10MB</div>
            </template>
          </el-upload>
          
          <div class="upload-actions">
            <el-button 
              type="primary" 
              :loading="importing" 
              :disabled="!wordFile || !wordForm.bankName"
              @click="handleWordImport"
            >
              开始导入
            </el-button>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- PDF导入 -->
      <el-tab-pane label="PDF导入" name="pdf">
        <div class="card">
          <div class="import-tips">
            <h4>导入说明：</h4>
            <ul>
              <li>支持 .pdf 格式文件（标准文本PDF效果最佳）</li>
              <li>自动识别题目格式，支持多种常见试卷格式</li>
              <li>使用一、单选题 / 二、多选题 等标题区分题型</li>
              <li>题目格式：1. 题干内容 或 1、题干内容</li>
              <li>选项格式：A. 选项内容 或 A、选项内容</li>
              <li>答案格式：题干中包含（A）或 答案：A</li>
              <li>建议先预览识别结果，确认无误后再导入</li>
            </ul>
          </div>
          
          <el-form :model="pdfForm" label-width="100px" class="import-form">
            <el-form-item label="题库名称" required>
              <el-input 
                v-model="pdfForm.bankName" 
                placeholder="请输入题库名称，如：2024年安全考试题库"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-form>
          
          <el-upload
            ref="pdfUploadRef"
            class="upload-area"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".pdf"
            :on-change="handlePdfChange"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将PDF文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">只能上传 pdf 文件，且不超过10MB</div>
            </template>
          </el-upload>
          
          <div class="upload-actions">
            <el-button 
              :loading="importing" 
              :disabled="!pdfFile"
              @click="handlePdfPreview"
            >
              识别预览
            </el-button>
            <el-button 
              type="primary" 
              :loading="importing" 
              :disabled="!pdfFile || !pdfForm.bankName"
              @click="handlePdfImport"
            >
              直接导入
            </el-button>
          </div>
          
          <!-- PDF预览结果 -->
          <div class="pdf-preview" v-if="pdfResult">
            <h4>识别结果（共 {{ pdfResult.questions?.length || 0 }} 道题）</h4>
            
            <div class="raw-text" v-if="pdfResult.raw_text">
              <el-collapse>
                <el-collapse-item title="原始识别文本（点击展开）">
                  <pre>{{ pdfResult.raw_text }}</pre>
                </el-collapse-item>
              </el-collapse>
            </div>
            
            <div class="question-list" v-if="pdfResult.questions?.length">
              <div 
                v-for="(q, index) in pdfResult.questions" 
                :key="index"
                class="question-item"
              >
                <div class="question-header">
                  <span class="question-num">第 {{ index + 1 }} 题</span>
                  <el-tag size="small">{{ questionTypeMap[q.question_type] }}</el-tag>
                </div>
                <div class="question-content">
                  <p><strong>题目：</strong>{{ q.title }}</p>
                  <p v-if="q.options"><strong>选项：</strong>
                    <span v-for="(v, k) in q.options" :key="k" class="option-span">{{ k }}.{{ v }} </span>
                  </p>
                  <p><strong>答案：</strong><span class="answer-text">{{ q.answer }}</span></p>
                </div>
              </div>
            </div>
            
            <div class="error-list" v-if="pdfResult.errors?.length">
              <h4 style="color: #f56c6c;">解析错误（{{ pdfResult.errors.length }} 条）</h4>
              <el-table :data="pdfResult.errors" max-height="200" size="small">
                <el-table-column prop="row" label="题号" width="70" />
                <el-table-column prop="error" label="错误原因" />
              </el-table>
            </div>
            
            <div class="preview-actions" v-if="pdfResult.questions?.length">
              <el-button 
                type="primary" 
                :loading="importing"
                :disabled="!pdfForm.bankName"
                @click="handlePdfConfirmImport"
              >
                确认导入 {{ pdfResult.questions.length }} 道题
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- 题库管理 -->
      <el-tab-pane label="题库管理" name="banks">
        <div class="card">
          <div class="bank-header">
            <h4>已导入的题库</h4>
            <el-button type="primary" size="small" @click="loadBanks">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
          
          <el-table :data="banks" v-loading="banksLoading" stripe>
            <el-table-column prop="name" label="题库名称" min-width="200" />
            <el-table-column prop="question_count" label="题目数量" width="100" align="center" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ row }">
                <el-popconfirm
                  title="确定删除该题库及所有题目吗？此操作不可恢复！"
                  confirm-button-text="确定删除"
                  cancel-button-text="取消"
                  @confirm="handleDeleteBank(row.id)"
                >
                  <template #reference>
                    <el-button type="danger" size="small" :loading="deletingBankId === row.id">
                      删除
                    </el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="empty-tip" v-if="!banksLoading && banks.length === 0">
            <el-empty description="暂无题库，请先导入题目" />
          </div>
        </div>
      </el-tab-pane>
      
      <!-- OCR导入 -->
      <el-tab-pane label="图片OCR导入" name="ocr">
        <div class="card">
          <div class="import-tips">
            <h4>导入说明：</h4>
            <ul>
              <li>支持 .jpg, .jpeg, .png 格式图片</li>
              <li>建议使用清晰的打印体文字图片</li>
              <li>系统会自动识别题目、选项和答案</li>
              <li>识别后可预览和修正，确认无误后再导入</li>
            </ul>
          </div>
          
          <el-upload
            ref="ocrUploadRef"
            class="upload-area"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".jpg,.jpeg,.png"
            :on-change="handleOcrChange"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将图片拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">只能上传 jpg/png 图片，且不超过10MB</div>
            </template>
          </el-upload>
          
          <div class="upload-actions">
            <el-button 
              type="primary" 
              :loading="importing" 
              :disabled="!ocrFile"
              @click="handleOcrPreview"
            >
              识别预览
            </el-button>
          </div>
          
          <!-- OCR预览结果 -->
          <div class="ocr-preview" v-if="ocrResult">
            <h4>识别结果（共 {{ ocrResult.questions?.length || 0 }} 道题）</h4>
            
            <div class="raw-text" v-if="ocrResult.raw_text">
              <el-collapse>
                <el-collapse-item title="原始识别文本">
                  <pre>{{ ocrResult.raw_text }}</pre>
                </el-collapse-item>
              </el-collapse>
            </div>
            
            <div class="question-list" v-if="ocrResult.questions?.length">
              <div 
                v-for="(q, index) in ocrResult.questions" 
                :key="index"
                class="question-item"
              >
                <div class="question-header">
                  <span class="question-num">第 {{ index + 1 }} 题</span>
                  <el-tag size="small">{{ questionTypeMap[q.question_type] }}</el-tag>
                </div>
                <div class="question-content">
                  <p><strong>题目：</strong>{{ q.title }}</p>
                  <p v-if="q.options"><strong>选项：</strong>
                    <span v-for="(v, k) in q.options" :key="k">{{ k }}.{{ v }} </span>
                  </p>
                  <p><strong>答案：</strong>{{ q.answer }}</p>
                </div>
              </div>
            </div>
            
            <div class="preview-actions">
              <el-button 
                type="primary" 
                :loading="importing"
                @click="handleOcrImport"
              >
                确认导入
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 导入结果弹窗 -->
    <el-dialog v-model="resultVisible" title="导入结果" width="500px">
      <div class="import-result" v-if="importResult">
        <el-result 
          :icon="importResult.success ? 'success' : 'warning'"
          :title="importResult.success ? '导入完成' : '部分导入失败'"
        >
          <template #sub-title>
            <p>总计：{{ importResult.total }} 题</p>
            <p>成功：{{ importResult.success_count }} 题</p>
            <p>失败：{{ importResult.fail_count }} 题</p>
          </template>
        </el-result>
        
        <div class="error-list" v-if="importResult.errors?.length">
          <h4>错误详情：</h4>
          <el-table :data="importResult.errors" max-height="300">
            <el-table-column prop="row" label="行号" width="70" />
            <el-table-column prop="error" label="错误原因" min-width="200" />
            <el-table-column prop="content" label="题目内容预览" min-width="200">
              <template #default="{ row }">
                <span class="content-preview">{{ row.content || '-' }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <template #footer>
        <el-button type="primary" @click="resultVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { importApi, questionApi } from '@/api/question'
import dayjs from 'dayjs'

const activeTab = ref('excel')
const importing = ref(false)
const resultVisible = ref(false)
const importResult = ref(null)

// 文件
const excelFile = ref(null)
const wordFile = ref(null)
const ocrFile = ref(null)
const ocrResult = ref(null)
const pdfFile = ref(null)
const pdfResult = ref(null)

// Word导入表单
const wordForm = reactive({
  bankName: ''
})

// PDF导入表单
const pdfForm = reactive({
  bankName: ''
})

// 题库管理
const banks = ref([])
const banksLoading = ref(false)
const deletingBankId = ref(null)

// 映射
const questionTypeMap = {
  single_choice: '单选题',
  multiple_choice: '多选题',
  true_false: '判断题',
  fill_blank: '填空题',
  short_answer: '简答题'
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 加载题库列表
const loadBanks = async () => {
  banksLoading.value = true
  try {
    const res = await importApi.getBanks()
    banks.value = res.data.items || []
  } catch (error) {
    console.error('加载题库失败:', error)
  } finally {
    banksLoading.value = false
  }
}

// 删除题库
const handleDeleteBank = async (bankId) => {
  deletingBankId.value = bankId
  try {
    await importApi.deleteBank(bankId)
    ElMessage.success('删除成功')
    loadBanks()
  } catch (error) {
    console.error('删除失败:', error)
  } finally {
    deletingBankId.value = null
  }
}

// 切换到题库管理时加载数据
watch(activeTab, (val) => {
  if (val === 'banks') {
    loadBanks()
  }
})

// 下载模板
const downloadTemplate = async () => {
  try {
    const res = await importApi.downloadTemplate()
    const blob = new Blob([res.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '题库导入模板.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载模板失败')
  }
}

// Excel文件变化
const handleExcelChange = (file) => {
  excelFile.value = file.raw
}

// Word文件变化
const handleWordChange = (file) => {
  wordFile.value = file.raw
}

// OCR文件变化
const handleOcrChange = (file) => {
  ocrFile.value = file.raw
  ocrResult.value = null
}

// Excel导入
const handleExcelImport = async () => {
  if (!excelFile.value) return
  
  importing.value = true
  try {
    const res = await importApi.importExcel(excelFile.value)
    importResult.value = res.data
    resultVisible.value = true
    excelFile.value = null
  } catch (error) {
    console.error('导入失败:', error)
  } finally {
    importing.value = false
  }
}

// Word导入
const handleWordImport = async () => {
  if (!wordFile.value || !wordForm.bankName) {
    ElMessage.warning('请填写题库名称并选择文件')
    return
  }
  
  importing.value = true
  try {
    const res = await importApi.importWord(wordFile.value, wordForm.bankName)
    importResult.value = res.data
    resultVisible.value = true
    wordFile.value = null
    wordForm.bankName = ''
  } catch (error) {
    console.error('导入失败:', error)
  } finally {
    importing.value = false
  }
}

// OCR预览
const handleOcrPreview = async () => {
  if (!ocrFile.value) return
  
  importing.value = true
  try {
    const res = await importApi.ocrPreview(ocrFile.value)
    ocrResult.value = res.data
    
    if (!res.data.success) {
      ElMessage.warning('识别失败，请检查图片质量')
    }
  } catch (error) {
    console.error('识别失败:', error)
  } finally {
    importing.value = false
  }
}

// OCR导入
const handleOcrImport = async () => {
  if (!ocrResult.value?.questions?.length) {
    ElMessage.warning('没有可导入的题目')
    return
  }
  
  importing.value = true
  try {
    await questionApi.createQuestionsBatch(ocrResult.value.questions)
    ElMessage.success(`成功导入 ${ocrResult.value.questions.length} 道题目`)
    ocrFile.value = null
    ocrResult.value = null
  } catch (error) {
    console.error('导入失败:', error)
  } finally {
    importing.value = false
  }
}

// ============ PDF导入 ============

// PDF文件变化
const handlePdfChange = (file) => {
  pdfFile.value = file.raw
  pdfResult.value = null
}

// PDF预览
const handlePdfPreview = async () => {
  if (!pdfFile.value) return
  
  importing.value = true
  try {
    const res = await importApi.pdfPreview(pdfFile.value)
    pdfResult.value = res.data
    
    if (!res.data.success) {
      ElMessage.warning('识别失败，请检查PDF文件')
    } else if (res.data.questions?.length === 0) {
      ElMessage.warning('未识别到题目，请检查PDF格式')
    } else {
      ElMessage.success(`成功识别 ${res.data.questions.length} 道题目`)
    }
  } catch (error) {
    console.error('识别失败:', error)
    ElMessage.error('PDF识别失败，请检查文件格式')
  } finally {
    importing.value = false
  }
}

// PDF直接导入
const handlePdfImport = async () => {
  if (!pdfFile.value || !pdfForm.bankName) {
    ElMessage.warning('请填写题库名称并选择文件')
    return
  }
  
  importing.value = true
  try {
    const res = await importApi.importPdf(pdfFile.value, pdfForm.bankName)
    importResult.value = res.data
    resultVisible.value = true
    pdfFile.value = null
    pdfForm.bankName = ''
    pdfResult.value = null
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('PDF导入失败')
  } finally {
    importing.value = false
  }
}

// PDF确认导入（预览后）
const handlePdfConfirmImport = async () => {
  if (!pdfResult.value?.questions?.length) {
    ElMessage.warning('没有可导入的题目')
    return
  }
  
  if (!pdfForm.bankName) {
    ElMessage.warning('请填写题库名称')
    return
  }
  
  // 使用直接导入接口
  await handlePdfImport()
}
</script>

<style lang="scss" scoped>
.question-import {
  .import-tabs {
    :deep(.el-tabs__content) {
      padding: 0;
    }
  }
  
  .import-tips {
    background: #f5f7fa;
    padding: 15px 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    
    h4 {
      margin-bottom: 10px;
      color: #333;
    }
    
    ul {
      color: #666;
      padding-left: 20px;
      
      li {
        line-height: 1.8;
        list-style: disc;
      }
    }
  }
  
  .upload-area {
    margin-bottom: 20px;
    
    :deep(.el-upload-dragger) {
      width: 100%;
    }
  }
  
  .upload-actions {
    text-align: center;
  }
  
  .ocr-preview, .pdf-preview {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    
    h4 {
      margin-bottom: 15px;
    }
    
    .raw-text {
      margin-bottom: 20px;
      
      pre {
        background: #f5f5f5;
        padding: 10px;
        border-radius: 4px;
        max-height: 200px;
        overflow-y: auto;
        font-size: 12px;
        white-space: pre-wrap;
        word-break: break-all;
      }
    }
    
    .question-list {
      max-height: 500px;
      overflow-y: auto;
      
      .question-item {
        background: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        
        .question-header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 10px;
          
          .question-num {
            font-weight: 600;
          }
        }
        
        .question-content {
          font-size: 14px;
          color: #666;
          
          p {
            margin-bottom: 5px;
          }
          
          .option-span {
            display: inline-block;
            margin-right: 15px;
            padding: 2px 6px;
            background: #e8f4ff;
            border-radius: 4px;
            margin-bottom: 4px;
          }
          
          .answer-text {
            color: #52c41a;
            font-weight: 600;
          }
        }
      }
    }
    
    .error-list {
      margin-top: 20px;
      padding: 15px;
      background: #fff2f0;
      border-radius: 8px;
    }
    
    .preview-actions {
      margin-top: 20px;
      text-align: center;
    }
  }
  
  .import-result {
    .error-list {
      margin-top: 20px;
      
      h4 {
        margin-bottom: 10px;
        color: #f56c6c;
      }
      
      .content-preview {
        display: block;
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 12px;
        color: #999;
      }
    }
  }
  
  .import-form {
    margin-bottom: 20px;
    max-width: 500px;
  }
  
  .bank-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h4 {
      margin: 0;
      font-size: 16px;
    }
  }
  
  .empty-tip {
    padding: 40px 0;
  }
}
</style>
