<template>
  <div class="exam-statistics">
    <h1 class="page-title">考试统计 - {{ examStats?.exam_title }}</h1>
    
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-value">{{ examStats?.total_participants || 0 }}</div>
          <div class="stat-label">参与人数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-value">{{ examStats?.average_score || 0 }}</div>
          <div class="stat-label">平均分</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-value">{{ examStats?.pass_rate || 0 }}%</div>
          <div class="stat-label">及格率</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-value">{{ formatDuration(examStats?.average_duration) }}</div>
          <div class="stat-label">平均用时</div>
        </div>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <div class="card">
          <h3>分数分布</h3>
          <v-chart :option="scoreChartOption" style="height: 300px" autoresize />
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="card">
          <h3>分数详情</h3>
          <div class="score-detail">
            <div class="detail-item">
              <span class="label">最高分</span>
              <span class="value">{{ examStats?.highest_score || 0 }}</span>
            </div>
            <div class="detail-item">
              <span class="label">最低分</span>
              <span class="value">{{ examStats?.lowest_score || 0 }}</span>
            </div>
            <div class="detail-item">
              <span class="label">平均分</span>
              <span class="value">{{ examStats?.average_score || 0 }}</span>
            </div>
            <div class="detail-item">
              <span class="label">及格人数</span>
              <span class="value">
                {{ Math.round((examStats?.pass_rate || 0) * (examStats?.total_participants || 0) / 100) }}
              </span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <div class="card mt-20">
      <el-button @click="router.back()">返回</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { statisticsApi } from '@/api/exam'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const router = useRouter()
const route = useRoute()
const examStats = ref(null)

// 分数分布图配置
const scoreChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: examStats.value?.score_distribution?.map(d => d.range) || []
  },
  yAxis: {
    type: 'value',
    name: '人数'
  },
  series: [
    {
      name: '人数',
      type: 'bar',
      data: examStats.value?.score_distribution?.map(d => d.count) || [],
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#79bbff' }
          ]
        }
      }
    }
  ]
}))

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '0分钟'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (minutes === 0) return `${secs}秒`
  if (secs === 0) return `${minutes}分钟`
  return `${minutes}分${secs}秒`
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await statisticsApi.getExamStatistics(route.params.id)
    examStats.value = res.data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style lang="scss" scoped>
.exam-statistics {
  .stat-cards {
    margin-bottom: 20px;
    
    .stat-card {
      background: #fff;
      border-radius: 8px;
      padding: 25px;
      text-align: center;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
      
      .stat-value {
        font-size: 32px;
        font-weight: 600;
        color: var(--primary-color);
      }
      
      .stat-label {
        font-size: 14px;
        color: #999;
        margin-top: 8px;
      }
    }
  }
  
  .card {
    h3 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 20px;
    }
  }
  
  .score-detail {
    .detail-item {
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
        color: #333;
      }
    }
  }
}
</style>
