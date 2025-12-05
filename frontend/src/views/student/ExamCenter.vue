<template>
  <div class="exam-center">
    <h1 class="page-title">考试中心</h1>
    
    <!-- 练习模式选择 -->
    <div class="practice-modes">
      <div 
        v-for="mode in practiceModes" 
        :key="mode.type"
        class="mode-card"
        :class="{ active: selectedMode === mode.type }"
        @click="selectMode(mode.type)"
      >
        <div class="mode-icon" :style="{ background: mode.bgColor }">
          <el-icon :size="28" :color="mode.color"><component :is="mode.icon" /></el-icon>
        </div>
        <span class="mode-name">{{ mode.name }}</span>
      </div>
    </div>
    
    <!-- 考试列表 -->
    <div class="section-title" v-if="filteredExams.length > 0">
      <h2>{{ currentModeName }}</h2>
      <span class="count">共 {{ filteredExams.length }} 个</span>
    </div>
    
    <div class="exam-grid" v-loading="loading">
      <div 
        v-for="exam in filteredExams" 
        :key="exam.id"
        class="exam-card"
      >
        <div class="exam-type">
          <el-tag :type="examTypeTag[exam.exam_type]" size="small">
            {{ examTypeMap[exam.exam_type] }}
          </el-tag>
        </div>
        
        <h3 class="exam-title">{{ exam.title }}</h3>
        
        <p class="exam-desc" v-if="exam.description">{{ exam.description }}</p>
        
        <div class="exam-info">
          <div class="info-item">
            <el-icon><Clock /></el-icon>
            <span>{{ exam.duration }}分钟</span>
          </div>
          <div class="info-item">
            <el-icon><Document /></el-icon>
            <span>{{ exam.question_count }}题</span>
          </div>
          <div class="info-item">
            <el-icon><Trophy /></el-icon>
            <span>{{ exam.total_score }}分</span>
          </div>
        </div>
        
        <div class="exam-footer">
          <span class="pass-score" v-if="exam.exam_type !== 'practice'">及格分：{{ exam.pass_score }}分</span>
          <span class="pass-score" v-else>练习模式</span>
          <el-button type="primary" @click="startExam(exam)">
            {{ exam.exam_type === 'practice' ? '开始练习' : '开始考试' }}
          </el-button>
        </div>
      </div>
    </div>
    
    <el-empty v-if="!loading && filteredExams.length === 0" :description="emptyText" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { List, Refresh, Reading, Aim, EditPen, Clock, Document, Trophy } from '@element-plus/icons-vue'
import { examApi } from '@/api/exam'

const router = useRouter()
const loading = ref(false)
const exams = ref([])
const selectedMode = ref('all')

// 练习模式配置
const practiceModes = [
  { type: 'all', name: '全部', icon: List, color: '#409eff', bgColor: '#ecf5ff' },
  { type: 'practice', name: '顺序练习', icon: Reading, color: '#67c23a', bgColor: '#f0f9eb' },
  { type: 'random', name: '随机练习', icon: Refresh, color: '#e6a23c', bgColor: '#fdf6ec' },
  { type: 'mock', name: '模拟考试', icon: EditPen, color: '#f56c6c', bgColor: '#fef0f0' },
  { type: 'formal', name: '正式考试', icon: Aim, color: '#909399', bgColor: '#f4f4f5' }
]

// 映射
const examTypeMap = {
  practice: '顺序练习',
  random: '随机练习',
  mock: '模拟考试',
  formal: '正式考试'
}

const examTypeTag = {
  practice: 'success',
  random: 'warning',
  mock: 'danger',
  formal: ''
}

// 当前模式名称
const currentModeName = computed(() => {
  const mode = practiceModes.find(m => m.type === selectedMode.value)
  return mode ? mode.name : '全部'
})

// 筛选后的考试列表
const filteredExams = computed(() => {
  if (selectedMode.value === 'all') {
    return exams.value
  }
  return exams.value.filter(exam => exam.exam_type === selectedMode.value)
})

// 空状态文本
const emptyText = computed(() => {
  if (selectedMode.value === 'all') {
    return '暂无可参加的考试'
  }
  return `暂无${currentModeName.value}`
})

// 选择模式
const selectMode = (mode) => {
  selectedMode.value = mode
}

// 获取可参加的考试
const fetchExams = async () => {
  loading.value = true
  try {
    const res = await examApi.getAvailableExams()
    exams.value = res.data
  } catch (error) {
    console.error('获取考试列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 开始考试
const startExam = async (exam) => {
  const isPractice = exam.exam_type === 'practice' || exam.exam_type === 'random'
  const title = isPractice ? '开始练习' : '开始考试'
  const message = isPractice 
    ? `确定要开始"${exam.title}"吗？\n共${exam.question_count}道题目`
    : `确定要开始"${exam.title}"吗？\n考试时长：${exam.duration}分钟\n总分：${exam.total_score}分`
  
  try {
    await ElMessageBox.confirm(message, title, {
      confirmButtonText: '开始',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    router.push(`/exam/${exam.id}`)
  } catch {
    // 取消
  }
}

onMounted(() => {
  fetchExams()
})
</script>

<style lang="scss" scoped>
.exam-center {
  // 练习模式选择
  .practice-modes {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-bottom: 30px;
    
    .mode-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      transition: all 0.3s;
      border: 2px solid transparent;
      
      &:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
      }
      
      &.active {
        border-color: var(--primary-color);
        box-shadow: 0 4px 15px rgba(64, 158, 255, 0.2);
      }
      
      .mode-icon {
        width: 56px;
        height: 56px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .mode-name {
        font-size: 14px;
        font-weight: 500;
        color: #333;
      }
    }
  }
  
  // 标题
  .section-title {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    
    h2 {
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }
    
    .count {
      font-size: 14px;
      color: #999;
    }
  }
  
  .exam-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }
  
  .exam-card {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .exam-type {
      margin-bottom: 12px;
    }
    
    .exam-title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin-bottom: 10px;
    }
    
    .exam-desc {
      font-size: 14px;
      color: #666;
      margin-bottom: 15px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .exam-info {
      display: flex;
      gap: 20px;
      margin-bottom: 20px;
      padding: 15px;
      background: #f9f9f9;
      border-radius: 8px;
      
      .info-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        color: #666;
        
        .el-icon {
          color: var(--primary-color);
        }
      }
    }
    
    .exam-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .pass-score {
        font-size: 13px;
        color: #999;
      }
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .exam-center {
    .practice-modes {
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      
      .mode-card {
        padding: 15px 10px;
        
        .mode-icon {
          width: 44px;
          height: 44px;
        }
        
        .mode-name {
          font-size: 12px;
        }
      }
    }
  }
}
</style>
