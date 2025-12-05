<template>
  <div class="exam-list">
    <h1 class="page-title">考试管理</h1>
    
    <!-- 搜索栏 -->
    <div class="card search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input 
            v-model="searchForm.keyword" 
            placeholder="考试名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.exam_type" placeholder="全部" clearable>
            <el-option label="顺序练习" value="practice" />
            <el-option label="模拟考试" value="mock" />
            <el-option label="正式考试" value="formal" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已关闭" value="closed" />
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
      
      <el-button type="primary" @click="router.push('/admin/exams/create')">
        <el-icon><Plus /></el-icon>
        创建考试
      </el-button>
    </div>
    
    <!-- 考试表格 -->
    <div class="card">
      <el-table :data="exams" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="考试名称" min-width="200" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="examTypeTag[row.exam_type]" size="small">
              {{ examTypeMap[row.exam_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="question_count" label="题目数" width="80" />
        <el-table-column prop="total_score" label="总分" width="70" />
        <el-table-column prop="duration" label="时长(分)" width="90" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag[row.status]" size="small">
              {{ statusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="router.push(`/admin/exams/${row.id}/edit`)">
              编辑
            </el-button>
            <el-button 
              type="success" 
              link 
              @click="handlePublish(row)"
              v-if="row.status === 'draft'"
            >
              发布
            </el-button>
            <el-button 
              type="primary" 
              link 
              @click="router.push(`/admin/exams/${row.id}/statistics`)"
            >
              统计
            </el-button>
            <el-popconfirm 
              title="确定删除该考试吗？"
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
        @size-change="fetchExams"
        @current-change="fetchExams"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { examApi } from '@/api/exam'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const exams = ref([])

// 映射
const examTypeMap = {
  practice: '顺序练习',
  mock: '模拟考试',
  formal: '正式考试'
}

const examTypeTag = {
  practice: 'info',
  mock: 'warning',
  formal: 'danger'
}

const statusMap = {
  draft: '草稿',
  published: '已发布',
  closed: '已关闭'
}

const statusTag = {
  draft: 'info',
  published: 'success',
  closed: 'danger'
}

// 搜索表单
const searchForm = reactive({
  keyword: '',
  exam_type: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 格式化日期
const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

// 获取考试列表
const fetchExams = async () => {
  loading.value = true
  try {
    const res = await examApi.getExams({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    })
    exams.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error('获取考试列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchExams()
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.exam_type = ''
  searchForm.status = ''
  handleSearch()
}

// 发布考试
const handlePublish = async (exam) => {
  try {
    await examApi.publishExam(exam.id)
    ElMessage.success('发布成功')
    fetchExams()
  } catch (error) {
    console.error('发布失败:', error)
  }
}

// 删除考试
const handleDelete = async (id) => {
  try {
    await examApi.deleteExam(id)
    ElMessage.success('删除成功')
    fetchExams()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  fetchExams()
})
</script>

<style lang="scss" scoped>
.exam-list {
  .search-bar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    
    .el-form {
      flex: 1;
    }
  }
}
</style>
