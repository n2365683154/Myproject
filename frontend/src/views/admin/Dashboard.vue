<template>
  <div class="dashboard">
    <h1 class="page-title">控制台</h1>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="6">
        <div class="stat-card users">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.users?.total || 0 }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <div class="stat-card questions">
          <div class="stat-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.questions?.total || 0 }}</div>
            <div class="stat-label">题目总数</div>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <div class="stat-card exams">
          <div class="stat-icon">
            <el-icon><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.exams?.published || 0 }}</div>
            <div class="stat-label">已发布考试</div>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <div class="stat-card records">
          <div class="stat-icon">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.records?.today || 0 }}</div>
            <div class="stat-label">今日考试</div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="16">
        <div class="card">
          <h3>考试趋势（近7天）</h3>
          <v-chart :option="trendChartOption" style="height: 300px" autoresize />
        </div>
      </el-col>
      
      <el-col :xs="24" :lg="8">
        <div class="card">
          <h3>今日活跃</h3>
          <div class="today-stats">
            <div class="today-item">
              <span class="label">新增用户</span>
              <span class="value">{{ stats.users?.new_today || 0 }}</span>
            </div>
            <div class="today-item">
              <span class="label">活跃用户</span>
              <span class="value">{{ stats.today_active_users || 0 }}</span>
            </div>
            <div class="today-item">
              <span class="label">考试记录</span>
              <span class="value">{{ stats.records?.today || 0 }}</span>
            </div>
            <div class="today-item">
              <span class="label">总考试记录</span>
              <span class="value">{{ stats.records?.total || 0 }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 快捷操作 -->
    <div class="card quick-actions">
      <h3>快捷操作</h3>
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6">
          <div class="action-item" @click="router.push('/admin/questions/create')">
            <el-icon><Plus /></el-icon>
            <span>添加题目</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="action-item" @click="router.push('/admin/questions/import')">
            <el-icon><Upload /></el-icon>
            <span>导入题库</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="action-item" @click="router.push('/admin/exams/create')">
            <el-icon><Tickets /></el-icon>
            <span>创建考试</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="action-item" @click="router.push('/admin/users')">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { statisticsApi } from '@/api/exam'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const router = useRouter()
const stats = ref({})

// 趋势图配置
const trendChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: stats.value.record_trend?.dates || []
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '考试记录',
      type: 'line',
      smooth: true,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ]
        }
      },
      lineStyle: {
        color: '#409eff'
      },
      itemStyle: {
        color: '#409eff'
      },
      data: stats.value.record_trend?.counts || []
    }
  ]
}))

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await statisticsApi.getSystemOverview()
    stats.value = res.data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-cards {
    margin-bottom: 20px;
    
    .stat-card {
      background: #fff;
      border-radius: 8px;
      padding: 20px;
      display: flex;
      align-items: center;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
      
      .stat-icon {
        width: 60px;
        height: 60px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        
        .el-icon {
          font-size: 28px;
          color: #fff;
        }
      }
      
      .stat-info {
        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #333;
        }
        
        .stat-label {
          font-size: 14px;
          color: #999;
          margin-top: 5px;
        }
      }
      
      &.users .stat-icon {
        background: linear-gradient(135deg, #667eea, #764ba2);
      }
      
      &.questions .stat-icon {
        background: linear-gradient(135deg, #f093fb, #f5576c);
      }
      
      &.exams .stat-icon {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
      }
      
      &.records .stat-icon {
        background: linear-gradient(135deg, #43e97b, #38f9d7);
      }
    }
  }
  
  .chart-row {
    margin-bottom: 20px;
    
    .card {
      height: 100%;
      
      h3 {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 20px;
        color: #333;
      }
    }
    
    .today-stats {
      .today-item {
        display: flex;
        justify-content: space-between;
        padding: 15px 0;
        border-bottom: 1px solid #f0f0f0;
        
        &:last-child {
          border-bottom: none;
        }
        
        .label {
          color: #666;
        }
        
        .value {
          font-size: 18px;
          font-weight: 600;
          color: var(--primary-color);
        }
      }
    }
  }
  
  .quick-actions {
    h3 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 20px;
      color: #333;
    }
    
    .action-item {
      background: #f5f7fa;
      border-radius: 8px;
      padding: 30px 20px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        background: var(--primary-color);
        color: #fff;
        transform: translateY(-3px);
      }
      
      .el-icon {
        font-size: 32px;
        margin-bottom: 10px;
      }
      
      span {
        display: block;
        font-size: 14px;
      }
    }
  }
}
</style>
