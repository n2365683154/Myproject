<template>
  <div class="exam-edit">
    <h1 class="page-title">{{ isEdit ? '编辑考试' : '创建考试' }}</h1>
    
    <div class="card">
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
        style="max-width: 900px"
      >
        <el-form-item label="考试名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入考试名称" />
        </el-form-item>
        
        <el-form-item label="考试类型" prop="exam_type">
          <el-radio-group v-model="form.exam_type">
            <el-radio-button value="practice">顺序练习</el-radio-button>
            <el-radio-button value="mock">模拟考试</el-radio-button>
            <el-radio-button value="formal">正式考试</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="考试描述">
          <el-input 
            v-model="form.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入考试描述（选填）"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="总分" prop="total_score">
              <el-input-number v-model="form.total_score" :min="1" :max="1000" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="及格分" prop="pass_score">
              <el-input-number v-model="form.pass_score" :min="0" :max="form.total_score" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="时长(分钟)" prop="duration">
              <el-input-number v-model="form.duration" :min="0" :max="600" />
              <span class="tips">0 表示不限时</span>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 题库多选（用于随机抽题的题目范围） -->
        <el-form-item label="题库选择">
          <el-select
            v-model="form.bank_ids"
            multiple
            collapse-tags
            placeholder="请选择一个或多个题库"
            style="width: 400px;"
          >
            <el-option
              v-for="bank in bankList"
              :key="bank.id"
              :label="`${bank.name} (${bank.question_count}题)`"
              :value="bank.id"
            />
          </el-select>
          <span class="tips" style="margin-left: 8px;">随机抽题时将从这些题库中抽题</span>
        </el-form-item>
        
        <el-form-item label="组卷方式">
          <el-radio-group v-model="form.is_random">
            <el-radio :value="0">固定组卷</el-radio>
            <el-radio :value="1">随机组卷</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 固定组卷：选择题目 -->
        <el-form-item label="选择题目" v-if="form.is_random === 0">
          <div class="question-selector">
            <div class="selector-row">
              <el-select 
                v-model="selectedBankId" 
                placeholder="选择题库（可选）" 
                clearable
                @change="handleBankChange"
                style="width: 200px; margin-right: 10px;"
              >
                <el-option 
                  v-for="bank in bankList" 
                  :key="bank.id" 
                  :label="`${bank.name} (${bank.question_count}题)`" 
                  :value="bank.id" 
                />
              </el-select>
              <el-button type="primary" @click="showQuestionDialog">
                选择题目 (已选 {{ form.question_ids.length }} 题)
              </el-button>
            </div>
            
            <div class="selected-questions" v-if="selectedQuestions.length">
              <el-table :data="selectedQuestions" max-height="300">
                <el-table-column type="index" label="序号" width="60" />
                <el-table-column prop="title" label="题目" show-overflow-tooltip />
                <el-table-column label="题型" width="100">
                  <template #default="{ row }">
                    {{ questionTypeMap[row.question_type] }}
                  </template>
                </el-table-column>
                <el-table-column prop="score" label="分值" width="70" />
                <el-table-column label="操作" width="80">
                  <template #default="{ row, $index }">
                    <el-button type="danger" link @click="removeQuestion($index)">
                      移除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-form-item>
        
        <!-- 随机组卷配置 -->
        <el-form-item label="随机配置" v-if="form.is_random === 1">
          <div class="random-config">
            <div class="config-row">
              <span class="config-label">统一随机抽题：</span>
              <el-input-number
                v-model="form.random_question_count"
                :min="0"
                :max="500"
                :step="10"
                style="margin-right: 10px;"
              />
              <span class="tips">设置为 100 表示每次随机抽取 100 题，0 表示按下方配置分段抽题</span>
            </div>
            <div class="config-row" style="margin-top: 10px;">
              <span class="config-label">题型限制：</span>
              <el-select v-model="form.question_type_filter" placeholder="题型过滤" style="width: 200px;">
                <el-option label="全部题型" value="all" />
                <el-option label="仅单选题" value="single" />
                <el-option label="仅多选题" value="multiple" />
              </el-select>
            </div>
            <div 
              v-for="(config, index) in randomConfigs" 
              :key="index"
              class="config-row"
            >
              <el-select v-model="config.question_type" placeholder="题型">
                <el-option label="单选题" value="single_choice" />
                <el-option label="多选题" value="multiple_choice" />
                <el-option label="判断题" value="true_false" />
                <el-option label="填空题" value="fill_blank" />
              </el-select>
              <el-input-number v-model="config.count" :min="1" placeholder="数量" />
              <el-input-number v-model="config.score" :min="1" placeholder="每题分值" />
              <el-select v-model="config.difficulty" placeholder="难度" clearable>
                <el-option label="简单" value="easy" />
                <el-option label="中等" value="medium" />
                <el-option label="困难" value="hard" />
              </el-select>
              <el-button type="danger" :icon="Delete" circle @click="removeConfig(index)" />
            </div>
            <el-button type="primary" link @click="addConfig">
              <el-icon><Plus /></el-icon>
              添加配置
            </el-button>
          </div>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间">
              <el-date-picker
                v-model="form.start_time"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间">
              <el-date-picker
                v-model="form.end_time"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="其他设置">
          <el-checkbox v-model="form.allow_review" :true-value="1" :false-value="0">
            允许查看解析
          </el-checkbox>
          <el-checkbox v-model="form.show_answer" :true-value="1" :false-value="0">
            交卷后显示答案
          </el-checkbox>
        </el-form-item>
        
        <el-form-item label="最大尝试次数">
          <el-input-number v-model="form.max_attempts" :min="0" />
          <span class="tips">0表示不限制</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '创建考试' }}
          </el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 选择题目弹窗 -->
    <el-dialog v-model="questionDialogVisible" title="选择题目" width="900px">
      <div class="question-dialog">
        <div class="search-row">
          <el-input 
            v-model="questionSearch.keyword" 
            placeholder="搜索题目"
            clearable
            @keyup.enter="fetchQuestions"
          />
          <el-select v-model="questionSearch.question_type" placeholder="题型" clearable>
            <el-option label="单选题" value="single_choice" />
            <el-option label="多选题" value="multiple_choice" />
            <el-option label="判断题" value="true_false" />
            <el-option label="填空题" value="fill_blank" />
          </el-select>
          <el-button type="primary" @click="fetchQuestions">搜索</el-button>
        </div>
        
        <el-table 
          ref="questionTableRef"
          :data="questionList" 
          @selection-change="handleSelectionChange"
          max-height="400"
        >
          <el-table-column type="selection" width="50" />
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="title" label="题目" show-overflow-tooltip />
          <el-table-column label="题型" width="100">
            <template #default="{ row }">
              {{ questionTypeMap[row.question_type] }}
            </template>
          </el-table-column>
          <el-table-column prop="score" label="分值" width="70" />
        </el-table>
        
        <el-pagination
          v-model:current-page="questionPagination.page"
          :total="questionPagination.total"
          :page-size="20"
          layout="total, prev, pager, next"
          class="mt-20"
          @current-change="fetchQuestions"
        />
      </div>
      
      <template #footer>
        <el-button @click="questionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmQuestionSelection">
          确定 ({{ tempSelectedQuestions.length }} 题)
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { examApi } from '@/api/exam'
import { questionApi, importApi } from '@/api/question'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const submitting = ref(false)

// 映射
const questionTypeMap = {
  single_choice: '单选题',
  multiple_choice: '多选题',
  true_false: '判断题',
  fill_blank: '填空题',
  short_answer: '简答题'
}

// 表单
const formRef = ref()
const form = reactive({
  title: '',
  description: '',
  exam_type: 'mock',
  total_score: 100,
  pass_score: 60,
  duration: 120,
  is_random: 0,
  random_question_count: 0,
  question_type_filter: 'all',
  question_ids: [],
  bank_ids: [],
  start_time: null,
  end_time: null,
  allow_review: 1,
  show_answer: 1,
  max_attempts: 0
})

const rules = {
  title: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  exam_type: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
  total_score: [{ required: true, message: '请输入总分', trigger: 'blur' }],
  duration: [{ required: true, message: '请输入考试时长', trigger: 'blur' }]
}

// 已选题目
const selectedQuestions = ref([])

// 题库列表
const bankList = ref([])
const selectedBankId = ref(null)

// 随机组卷配置
const randomConfigs = ref([
  { question_type: 'single_choice', count: 10, score: 2, difficulty: '' }
])

// 题目选择弹窗
const questionDialogVisible = ref(false)
const questionTableRef = ref()
const questionList = ref([])
const tempSelectedQuestions = ref([])
const questionSearch = reactive({
  keyword: '',
  question_type: ''
})
const questionPagination = reactive({
  page: 1,
  total: 0
})

// 添加随机配置
const addConfig = () => {
  randomConfigs.value.push({
    question_type: 'single_choice',
    count: 5,
    score: 2,
    difficulty: ''
  })
}

// 移除随机配置
const removeConfig = (index) => {
  randomConfigs.value.splice(index, 1)
}

// 显示题目选择弹窗
const showQuestionDialog = () => {
  tempSelectedQuestions.value = [...selectedQuestions.value]
  questionDialogVisible.value = true
  fetchQuestions()
}

// 获取题目列表
const fetchQuestions = async () => {
  try {
    const res = await questionApi.getQuestions({
      skip: (questionPagination.page - 1) * 20,
      limit: 20,
      ...questionSearch,
      is_active: 1
    })
    questionList.value = res.data.items
    questionPagination.total = res.data.total
  } catch (error) {
    console.error('获取题目失败:', error)
  }
}

// 选择变化
const handleSelectionChange = (selection) => {
  tempSelectedQuestions.value = selection
}

// 确认选择
const confirmQuestionSelection = () => {
  selectedQuestions.value = [...tempSelectedQuestions.value]
  form.question_ids = selectedQuestions.value.map(q => q.id)
  questionDialogVisible.value = false
}

// 移除已选题目
const removeQuestion = (index) => {
  selectedQuestions.value.splice(index, 1)
  form.question_ids = selectedQuestions.value.map(q => q.id)
}

// 获取题库列表
const fetchBanks = async () => {
  try {
    const res = await importApi.getBanks({ skip: 0, limit: 100 })
    bankList.value = res.data.items || []
  } catch (error) {
    console.error('获取题库列表失败:', error)
  }
}

// 选择题库变化
const handleBankChange = async (bankId) => {
  if (!bankId) return
  
  try {
    // 分页获取该题库的所有题目
    let allQuestions = []
    let skip = 0
    const limit = 100
    
    while (true) {
      const res = await questionApi.getQuestions({
        bank_id: bankId,
        skip: skip,
        limit: limit
      })
      
      const questions = res.data?.items || []
      allQuestions = allQuestions.concat(questions)
      
      if (questions.length < limit) break
      skip += limit
    }
    
    console.log('获取到题目数:', allQuestions.length)
    
    if (allQuestions.length === 0) {
      ElMessage.warning('该题库暂无题目')
      return
    }
    
    // 合并已选题目（去重）
    const existingIds = new Set(form.question_ids)
    const newQuestions = allQuestions.filter(q => !existingIds.has(q.id))
    
    // 使用 push 保持响应式
    newQuestions.forEach(q => {
      selectedQuestions.value.push(q)
      form.question_ids.push(q.id)
    })
    
    ElMessage.success(`已添加 ${newQuestions.length} 道题目，共 ${form.question_ids.length} 题`)
  } catch (error) {
    console.error('获取题库题目失败:', error)
    ElMessage.error('获取题库题目失败')
  }
}

// 获取考试详情
const fetchExam = async () => {
  if (!isEdit.value) return
  
  try {
    const res = await examApi.getExam(route.params.id)
    const data = res.data
    
    Object.assign(form, {
      title: data.title,
      description: data.description || '',
      exam_type: data.exam_type,
      total_score: data.total_score,
      pass_score: data.pass_score,
      duration: data.duration,
      is_random: data.is_random,
      random_question_count: data.random_question_count || 0,
      question_type_filter: data.question_type_filter || 'all',
      start_time: data.start_time,
      end_time: data.end_time,
      allow_review: data.allow_review,
      show_answer: data.show_answer,
      max_attempts: data.max_attempts
    })
    
    // 加载已选题目
    if (data.questions?.length) {
      selectedQuestions.value = data.questions
      form.question_ids = data.questions.map(q => q.id)
    }
  } catch (error) {
    console.error('获取考试详情失败:', error)
  }
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  // 构建提交数据
  const data = { ...form }
  
  // 随机组卷配置
  if (form.is_random === 1) {
    data.random_config = { questions: randomConfigs.value }
  }
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await examApi.updateExam(route.params.id, data)
      ElMessage.success('修改成功')
    } else {
      await examApi.createExam(data)
      ElMessage.success('创建成功')
    }
    router.push('/admin/exams')
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchExam()
  fetchBanks()
})
</script>

<style lang="scss" scoped>
.exam-edit {
  .question-selector {
    width: 100%;
    
    .selected-questions {
      margin-top: 15px;
    }
  }
  
  .random-config {
    width: 100%;
    
    .config-row {
      display: flex;
      gap: 10px;
      margin-bottom: 10px;
      
      .el-select {
        width: 120px;
      }
      
      .el-input-number {
        width: 100px;
      }
    }
  }
  
  .tips {
    margin-left: 10px;
    color: #999;
    font-size: 12px;
  }
  
  .question-dialog {
    .search-row {
      display: flex;
      gap: 10px;
      margin-bottom: 15px;
      
      .el-input {
        width: 200px;
      }
    }
  }
}
</style>
