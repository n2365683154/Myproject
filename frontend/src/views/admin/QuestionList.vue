<template>
  <div class="question-list">
    <h1 class="page-title">题库管理</h1>
    
    <!-- 搜索栏 -->
    <div class="card search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input 
            v-model="searchForm.keyword" 
            placeholder="题目内容"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="searchForm.question_type" placeholder="全部" clearable>
            <el-option label="单选题" value="single_choice" />
            <el-option label="多选题" value="multiple_choice" />
            <el-option label="判断题" value="true_false" />
            <el-option label="填空题" value="fill_blank" />
            <el-option label="简答题" value="short_answer" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="searchForm.difficulty" placeholder="全部" clearable>
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <div class="actions">
        <el-button type="primary" @click="router.push('/admin/questions/create')">
          <el-icon><Plus /></el-icon>
          添加题目
        </el-button>
        <el-button @click="router.push('/admin/questions/import')">
          <el-icon><Upload /></el-icon>
          导入题库
        </el-button>
        <el-popconfirm
          title="确定删除所有题目吗？此操作不可恢复！"
          confirm-button-text="确定删除"
          cancel-button-text="取消"
          @confirm="handleDeleteAll"
        >
          <template #reference>
            <el-button type="danger" :loading="deletingAll">
              <el-icon><Delete /></el-icon>
              清空题库
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>
    
    <!-- 题目表格 -->
    <div class="card">
      <el-table :data="questions" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="题型" width="100">
          <template #default="{ row }">
            <el-tag :type="questionTypeTag[row.question_type]" size="small">
              {{ questionTypeMap[row.question_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="题目内容" min-width="300">
          <template #default="{ row }">
            <div class="question-title text-ellipsis">{{ row.title }}</div>
          </template>
        </el-table-column>
        <el-table-column label="难度" width="80">
          <template #default="{ row }">
            <el-tag :type="difficultyTag[row.difficulty]" size="small">
              {{ difficultyMap[row.difficulty] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分值" width="70" />
        <el-table-column label="正确率" width="100">
          <template #default="{ row }">
            {{ row.use_count > 0 ? Math.round(row.correct_count / row.use_count * 100) : 0 }}%
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDetail(row)">
              查看
            </el-button>
            <el-button type="primary" link @click="router.push(`/admin/questions/${row.id}/edit`)">
              编辑
            </el-button>
            <el-popconfirm 
              title="确定删除该题目吗？"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="mt-20"
        @size-change="fetchQuestions"
        @current-change="fetchQuestions"
      />
    </div>
    
    <!-- 题目详情弹窗 -->
    <el-dialog v-model="detailVisible" title="题目详情" width="700px">
      <div class="question-detail" v-if="currentQuestion">
        <div class="detail-item">
          <label>题型：</label>
          <el-tag :type="questionTypeTag[currentQuestion.question_type]">
            {{ questionTypeMap[currentQuestion.question_type] }}
          </el-tag>
          <el-tag :type="difficultyTag[currentQuestion.difficulty]" class="ml-10">
            {{ difficultyMap[currentQuestion.difficulty] }}
          </el-tag>
        </div>
        
        <div class="detail-item">
          <label>题目：</label>
          <div class="content">{{ currentQuestion.title }}</div>
        </div>
        
        <div class="detail-item" v-if="currentQuestion.options">
          <label>选项：</label>
          <div class="options">
            <div v-for="(value, key) in currentQuestion.options" :key="key" class="option-item">
              <span class="option-key">{{ key }}.</span>
              <span>{{ value }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-item">
          <label>答案：</label>
          <div class="answer">{{ currentQuestion.answer }}</div>
        </div>
        
        <div class="detail-item" v-if="currentQuestion.analysis">
          <label>解析：</label>
          <div class="content">{{ currentQuestion.analysis }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { questionApi } from '@/api/question'

const router = useRouter()
const loading = ref(false)
const deletingAll = ref(false)
const questions = ref([])
const detailVisible = ref(false)
const currentQuestion = ref(null)

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

const difficultyMap = {
  easy: '简单',
  medium: '中等',
  hard: '困难'
}

const difficultyTag = {
  easy: 'success',
  medium: 'warning',
  hard: 'danger'
}

// 搜索表单
const searchForm = reactive({
  keyword: '',
  question_type: '',
  difficulty: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 获取题目列表
const fetchQuestions = async () => {
  loading.value = true
  try {
    const res = await questionApi.getQuestions({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    })
    questions.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error('获取题目列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchQuestions()
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.question_type = ''
  searchForm.difficulty = ''
  handleSearch()
}

// 查看详情
const showDetail = (question) => {
  currentQuestion.value = question
  detailVisible.value = true
}

// 删除题目
const handleDelete = async (id) => {
  try {
    await questionApi.deleteQuestion(id)
    ElMessage.success('删除成功')
    fetchQuestions()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 删除所有题目
const handleDeleteAll = async () => {
  deletingAll.value = true
  try {
    await questionApi.deleteAllQuestions()
    ElMessage.success('已清空所有题目')
    fetchQuestions()
  } catch (error) {
    console.error('清空失败:', error)
  } finally {
    deletingAll.value = false
  }
}

onMounted(() => {
  fetchQuestions()
})
</script>

<style lang="scss" scoped>
.question-list {
  .search-bar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 10px;
    
    .el-form {
      flex: 1;
    }
    
    .actions {
      display: flex;
      gap: 10px;
    }
  }
  
  .question-title {
    max-width: 400px;
  }
  
  .ml-10 {
    margin-left: 10px;
  }
  
  .question-detail {
    .detail-item {
      margin-bottom: 20px;
      
      label {
        font-weight: 600;
        color: #333;
        display: block;
        margin-bottom: 8px;
      }
      
      .content {
        color: #666;
        line-height: 1.6;
      }
      
      .options {
        .option-item {
          padding: 8px 0;
          
          .option-key {
            font-weight: 600;
            margin-right: 8px;
          }
        }
      }
      
      .answer {
        color: var(--primary-color);
        font-weight: 600;
      }
    }
  }
}
</style>
