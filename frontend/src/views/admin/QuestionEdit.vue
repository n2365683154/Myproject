<template>
  <div class="question-edit">
    <h1 class="page-title">{{ isEdit ? '编辑题目' : '添加题目' }}</h1>
    
    <div class="card">
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
        style="max-width: 800px"
      >
        <el-form-item label="题目类型" prop="question_type">
          <el-radio-group v-model="form.question_type">
            <el-radio-button value="single_choice">单选题</el-radio-button>
            <el-radio-button value="multiple_choice">多选题</el-radio-button>
            <el-radio-button value="true_false">判断题</el-radio-button>
            <el-radio-button value="fill_blank">填空题</el-radio-button>
            <el-radio-button value="short_answer">简答题</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="题目内容" prop="title">
          <el-input 
            v-model="form.title" 
            type="textarea" 
            :rows="4"
            placeholder="请输入题目内容"
          />
        </el-form-item>
        
        <!-- 选择题选项 -->
        <el-form-item 
          label="选项" 
          v-if="['single_choice', 'multiple_choice'].includes(form.question_type)"
        >
          <div class="options-editor">
            <div 
              v-for="(value, key) in form.options" 
              :key="key" 
              class="option-row"
            >
              <span class="option-label">{{ key }}</span>
              <el-input v-model="form.options[key]" placeholder="请输入选项内容" />
              <el-button 
                type="danger" 
                :icon="Delete" 
                circle 
                @click="removeOption(key)"
                v-if="Object.keys(form.options).length > 2"
              />
            </div>
            <el-button 
              type="primary" 
              link 
              @click="addOption"
              v-if="Object.keys(form.options).length < 8"
            >
              <el-icon><Plus /></el-icon>
              添加选项
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="正确答案" prop="answer">
          <!-- 单选题 -->
          <el-radio-group 
            v-model="form.answer" 
            v-if="form.question_type === 'single_choice'"
          >
            <el-radio 
              v-for="key in Object.keys(form.options)" 
              :key="key" 
              :value="key"
            >
              {{ key }}
            </el-radio>
          </el-radio-group>
          
          <!-- 多选题 -->
          <el-checkbox-group 
            v-model="multipleAnswer" 
            v-else-if="form.question_type === 'multiple_choice'"
          >
            <el-checkbox 
              v-for="key in Object.keys(form.options)" 
              :key="key" 
              :label="key"
            >
              {{ key }}
            </el-checkbox>
          </el-checkbox-group>
          
          <!-- 判断题 -->
          <el-radio-group 
            v-model="form.answer" 
            v-else-if="form.question_type === 'true_false'"
          >
            <el-radio value="对">对</el-radio>
            <el-radio value="错">错</el-radio>
          </el-radio-group>
          
          <!-- 填空题/简答题 -->
          <el-input 
            v-else
            v-model="form.answer" 
            :type="form.question_type === 'short_answer' ? 'textarea' : 'text'"
            :rows="3"
            placeholder="请输入正确答案，多个答案用|分隔"
          />
        </el-form-item>
        
        <el-form-item label="答案解析" prop="analysis">
          <el-input 
            v-model="form.analysis" 
            type="textarea" 
            :rows="3"
            placeholder="请输入答案解析（选填）"
          />
        </el-form-item>
        
        <el-form-item label="难度等级" prop="difficulty">
          <el-radio-group v-model="form.difficulty">
            <el-radio-button value="easy">简单</el-radio-button>
            <el-radio-button value="medium">中等</el-radio-button>
            <el-radio-button value="hard">困难</el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="题目分值" prop="score">
          <el-input-number v-model="form.score" :min="1" :max="100" />
        </el-form-item>
        
        <el-form-item label="知识点">
          <el-tree-select
            v-model="form.knowledge_ids"
            :data="knowledgeTree"
            multiple
            :render-after-expand="false"
            placeholder="请选择知识点"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '添加题目' }}
          </el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { questionApi } from '@/api/question'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const submitting = ref(false)
const knowledgeTree = ref([])

// 多选答案
const multipleAnswer = ref([])

// 表单
const formRef = ref()
const form = reactive({
  question_type: 'single_choice',
  title: '',
  options: { A: '', B: '', C: '', D: '' },
  answer: '',
  analysis: '',
  difficulty: 'medium',
  score: 1,
  knowledge_ids: []
})

const rules = {
  question_type: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入正确答案', trigger: 'blur' }],
  difficulty: [{ required: true, message: '请选择难度等级', trigger: 'change' }]
}

// 监听多选答案变化
watch(multipleAnswer, (val) => {
  form.answer = val.sort().join('')
})

// 添加选项
const addOption = () => {
  const keys = Object.keys(form.options)
  const lastKey = keys[keys.length - 1]
  const nextKey = String.fromCharCode(lastKey.charCodeAt(0) + 1)
  form.options[nextKey] = ''
}

// 删除选项
const removeOption = (key) => {
  delete form.options[key]
}

// 获取知识点树
const fetchKnowledgeTree = async () => {
  try {
    const res = await questionApi.getKnowledgeTree()
    knowledgeTree.value = transformTree(res.data)
  } catch (error) {
    console.error('获取知识点失败:', error)
  }
}

// 转换树结构
const transformTree = (data) => {
  return data.map(item => ({
    value: item.id,
    label: item.name,
    children: item.children?.length ? transformTree(item.children) : undefined
  }))
}

// 获取题目详情
const fetchQuestion = async () => {
  if (!isEdit.value) return
  
  try {
    const res = await questionApi.getQuestion(route.params.id)
    const data = res.data
    
    Object.assign(form, {
      question_type: data.question_type,
      title: data.title,
      options: data.options || { A: '', B: '', C: '', D: '' },
      answer: data.answer,
      analysis: data.analysis || '',
      difficulty: data.difficulty,
      score: data.score,
      knowledge_ids: data.knowledge_points?.map(k => k.id) || []
    })
    
    // 处理多选答案
    if (data.question_type === 'multiple_choice') {
      multipleAnswer.value = data.answer.split('')
    }
  } catch (error) {
    console.error('获取题目详情失败:', error)
    ElMessage.error('获取题目详情失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  // 处理选项
  let options = null
  if (['single_choice', 'multiple_choice'].includes(form.question_type)) {
    options = form.options
  }
  
  const data = {
    ...form,
    options
  }
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await questionApi.updateQuestion(route.params.id, data)
      ElMessage.success('修改成功')
    } else {
      await questionApi.createQuestion(data)
      ElMessage.success('添加成功')
    }
    router.push('/admin/questions')
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchKnowledgeTree()
  fetchQuestion()
})
</script>

<style lang="scss" scoped>
.question-edit {
  .options-editor {
    width: 100%;
    
    .option-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
      
      .option-label {
        width: 30px;
        font-weight: 600;
      }
      
      .el-input {
        flex: 1;
      }
    }
  }
}
</style>
