<template>
  <div class="study-statistics">
    <h1 class="page-title">学习统计</h1>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="8" :lg="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_study_days || 0 }}</div>
          <div class="stat-label">学习天数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_questions || 0 }}</div>
          <div class="stat-label">练习题数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_correct || 0 }}</div>
          <div class="stat-label">正确题数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.average_accuracy || 0 }}%</div>
          <div class="stat-label">平均正确率</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_exams || 0 }}</div>
          <div class="stat-label">参加考试</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :lg="4">
        <div class="stat-card">
          <div class="stat-value">{{ stats.wrong_question_count || 0 }}</div>
          <div class="stat-label">错题待复习</div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <div class="card">
          <h3>练习题数趋势</h3>
          <v-chart :option="questionChartOption" style="height: 300px" autoresize />
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="card">
          <h3>正确率趋势</h3>
          <v-chart :option="accuracyChartOption" style="height: 300px" autoresize />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { statisticsApi } from '@/api/exam'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

const stats = ref({})
const trend = ref({})

// 练习题数图表配置
const questionChartOption = computed(() => ({
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
    data: trend.value.dates || [],
    axisLabel: {
      formatter: (value) => value.slice(5)
    }
  },
  yAxis: {
    type: 'value',
    name: '题数'
  },
  series: [
    {
      name: '练习题数',
      type: 'bar',
      data: trend.value.question_counts || [],
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

// 正确率图表配置
const accuracyChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    formatter: '{b}<br/>{a}: {c}%'
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
    data: trend.value.dates || [],
    axisLabel: {
      formatter: (value) => value.slice(5)
    }
  },
  yAxis: {
    type: 'value',
    name: '正确率(%)',
    max: 100
  },
  series: [
    {
      name: '正确率',
      type: 'line',
      smooth: true,
      data: trend.value.accuracies || [],
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ]
        }
      },
      lineStyle: {
        color: '#67c23a'
      },
      itemStyle: {
        color: '#67c23a'
      }
    }
  ]
}))

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await statisticsApi.getStudyStatistics()
    stats.value = res.data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取趋势数据
const fetchTrend = async () => {
  try {
    const res = await statisticsApi.getStudyTrend(30)
    trend.value = res.data
  } catch (error) {
    console.error('获取趋势数据失败:', error)
  }
}

onMounted(() => {
  fetchStats()
  fetchTrend()
})
</script>

<style lang="scss" scoped>
.study-statistics {
  .stat-cards {
    margin-bottom: 20px;
    
    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      text-align: center;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
      margin-bottom: 20px;
      
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
    margin-bottom: 20px;
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 20px;
    }
  }
}
</style>
