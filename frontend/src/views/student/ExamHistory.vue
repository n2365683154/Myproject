<template>
  <div class="exam-history">
    <h1 class="page-title">考试记录</h1>
    
    <div class="card">
      <el-table :data="records" v-loading="loading" stripe>
        <el-table-column prop="exam_title" label="考试名称" min-width="200" />
        <el-table-column label="得分" width="100">
          <template #default="{ row }">
            <span :class="{ 'text-success': row.is_passed, 'text-danger': !row.is_passed }">
              {{ row.score }}分
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="correct_count" label="正确" width="80" />
        <el-table-column prop="wrong_count" label="错误" width="80" />
        <el-table-column label="正确率" width="100">
          <template #default="{ row }">
            {{ row.accuracy }}%
          </template>
        </el-table-column>
        <el-table-column label="用时" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_passed ? 'success' : 'danger'" size="small">
              {{ row.is_passed ? '通过' : '未通过' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submit_time" label="提交时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.submit_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="router.push(`/exam-result/${row.id}`)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        class="mt-20"
        @size-change="fetchRecords"
        @current-change="fetchRecords"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { examApi } from '@/api/exam'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const records = ref([])

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

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}分${s}秒`
}

// 获取考试记录
const fetchRecords = async () => {
  loading.value = true
  try {
    const res = await examApi.getMyRecords({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    })
    records.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error('获取考试记录失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecords()
})
</script>

<style lang="scss" scoped>
.exam-history {
  .text-success {
    color: #67c23a;
    font-weight: 600;
  }
  
  .text-danger {
    color: #f56c6c;
    font-weight: 600;
  }
}
</style>
