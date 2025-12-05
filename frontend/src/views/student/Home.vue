<template>
  <div class="student-home">
    <div class="welcome-section">
      <h1>欢迎回来，{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}</h1>
      <p>今天也要加油学习哦！</p>
    </div>
    
    <!-- 学习概览 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="6">
        <div class="stat-card" @click="router.push('/statistics')">
          <el-icon class="stat-icon"><Calendar /></el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_study_days || 0 }}</div>
            <div class="stat-label">学习天数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card" @click="router.push('/history')">
          <el-icon class="stat-icon"><Document /></el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_questions || 0 }}</div>
            <div class="stat-label">练习题数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card" @click="router.push('/history')">
          <el-icon class="stat-icon"><Trophy /></el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_exams || 0 }}</div>
            <div class="stat-label">参加考试</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card" @click="router.push('/wrong-questions')">
          <el-icon class="stat-icon"><Warning /></el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ stats.wrong_question_count || 0 }}</div>
            <div class="stat-label">错题待复习</div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <!-- 可参加的考试 -->
      <el-col :xs="24" :lg="14">
        <div class="card">
          <div class="card-header">
            <h3>可参加的考试</h3>
            <el-button type="primary" link @click="router.push('/exam-center')">
              查看全部
            </el-button>
          </div>
          
          <div class="exam-list" v-if="availableExams.length">
            <div 
              v-for="exam in availableExams.slice(0, 5)" 
              :key="exam.id"
              class="exam-item"
              @click="router.push(`/exam/${exam.id}`)"
            >
              <div class="exam-info">
                <h4>{{ exam.title }}</h4>
                <div class="exam-meta">
                  <span><el-icon><Clock /></el-icon> {{ exam.duration }}分钟</span>
                  <span><el-icon><Document /></el-icon> {{ exam.question_count }}题</span>
                  <span><el-icon><Trophy /></el-icon> {{ exam.total_score }}分</span>
                </div>
              </div>
              <el-button type="primary" size="small">开始考试</el-button>
            </div>
          </div>
          <el-empty v-else description="暂无可参加的考试" />
        </div>
      </el-col>
      
      <!-- 最近考试记录 -->
      <el-col :xs="24" :lg="10">
        <div class="card">
          <div class="card-header">
            <h3>最近考试</h3>
            <el-button type="primary" link @click="router.push('/history')">
              查看全部
            </el-button>
          </div>
          
          <div class="record-list" v-if="recentRecords.length">
            <div 
              v-for="record in recentRecords" 
              :key="record.id"
              class="record-item"
              @click="router.push(`/exam-result/${record.id}`)"
            >
              <div class="record-info">
                <h4>{{ record.exam_title }}</h4>
                <div class="record-meta">
                  {{ formatDate(record.submit_time) }}
                </div>
              </div>
              <div class="record-score" :class="{ passed: record.is_passed }">
                {{ record.score }}分
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无考试记录" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { examApi, statisticsApi } from '@/api/exam'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const stats = ref({})
const availableExams = ref([])
const recentRecords = ref([])

// 格式化日期
const formatDate = (date) => {
  return date ? dayjs(date).format('MM-DD HH:mm') : '-'
}

// 获取学习统计
const fetchStats = async () => {
  try {
    const res = await statisticsApi.getStudyStatistics()
    stats.value = res.data
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

// 获取可参加的考试
const fetchAvailableExams = async () => {
  try {
    const res = await examApi.getAvailableExams()
    availableExams.value = res.data
  } catch (error) {
    console.error('获取考试列表失败:', error)
  }
}

// 获取最近考试记录
const fetchRecentRecords = async () => {
  try {
    const res = await examApi.getMyRecords({ limit: 5 })
    recentRecords.value = res.data.items
  } catch (error) {
    console.error('获取考试记录失败:', error)
  }
}

onMounted(() => {
  fetchStats()
  fetchAvailableExams()
  fetchRecentRecords()
})
</script>

<style lang="scss" scoped>
.student-home {
  .welcome-section {
    margin-bottom: 30px;
    
    h1 {
      font-size: 28px;
      font-weight: 600;
      color: #333;
      margin-bottom: 8px;
    }
    
    p {
      color: #666;
    }
  }
  
  .stat-cards {
    margin-bottom: 20px;
    
    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      align-items: center;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
      
      &:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
      }
      
      .stat-icon {
        font-size: 40px;
        color: var(--primary-color);
        margin-right: 15px;
      }
      
      .stat-info {
        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #333;
        }
        
        .stat-label {
          font-size: 13px;
          color: #999;
          margin-top: 4px;
        }
      }
    }
  }
  
  .card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      h3 {
        font-size: 16px;
        font-weight: 600;
        color: #333;
      }
    }
    
    .exam-list {
      .exam-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        border-radius: 8px;
        background: #f9f9f9;
        margin-bottom: 10px;
        cursor: pointer;
        transition: background 0.2s;
        
        &:hover {
          background: #f0f0f0;
        }
        
        .exam-info {
          h4 {
            font-size: 15px;
            font-weight: 500;
            margin-bottom: 8px;
          }
          
          .exam-meta {
            display: flex;
            gap: 15px;
            font-size: 13px;
            color: #999;
            
            span {
              display: flex;
              align-items: center;
              gap: 4px;
            }
          }
        }
      }
    }
    
    .record-list {
      .record-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        cursor: pointer;
        
        &:last-child {
          border-bottom: none;
        }
        
        .record-info {
          h4 {
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 4px;
          }
          
          .record-meta {
            font-size: 12px;
            color: #999;
          }
        }
        
        .record-score {
          font-size: 18px;
          font-weight: 600;
          color: #f56c6c;
          
          &.passed {
            color: #67c23a;
          }
        }
      }
    }
  }
}
</style>
