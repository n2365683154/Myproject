<template>
  <div class="exam-result" v-loading="loading">
    <div class="result-header" v-if="record">
      <div class="score-circle" :class="{ passed: record.is_passed }">
        <div class="score">{{ record.score }}</div>
        <div class="label">分</div>
      </div>
      
      <h2>{{ record.is_passed ? '恭喜通过！' : '继续努力！' }}</h2>
      
      <div class="result-stats">
        <div class="stat-item">
          <span class="value">{{ record.correct_count }}</span>
          <span class="label">正确</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ record.wrong_count }}</span>
          <span class="label">错误</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ record.unanswered_count }}</span>
          <span class="label">未答</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ record.accuracy }}%</span>
          <span class="label">正确率</span>
        </div>
        <div class="stat-item">
          <span class="value">{{ formatDuration(record.duration) }}</span>
          <span class="label">用时</span>
        </div>
      </div>
    </div>
    
    <div class="result-actions">
      <el-button @click="router.push('/history')">查看记录</el-button>
      <el-button type="primary" @click="router.push('/exam-center')">继续考试</el-button>
    </div>
    
    <!-- 答题详情 -->
    <div class="card answer-detail" v-if="record?.answers?.length">
      <h3>答题详情</h3>
      
      <div 
        v-for="(answer, index) in record.answers" 
        :key="answer.question_id"
        class="question-item"
        :class="{ correct: answer.is_correct === 1, wrong: answer.is_correct === 0 }"
      >
        <div class="question-header">
          <span class="question-num">第 {{ index + 1 }} 题</span>
          <el-tag 
            :type="answer.is_correct === 1 ? 'success' : (answer.is_correct === 2 ? 'warning' : 'danger')" 
            size="small"
          >
            {{ answer.is_correct === 1 ? '正确' : (answer.is_correct === 2 ? '部分正确' : '错误') }}
          </el-tag>
          <span class="score-info">得分：{{ answer.score }} / {{ answer.question?.score }}</span>
        </div>
        
        <div class="question-content">
          <div class="question-title">{{ answer.question?.title }}</div>
          
          <!-- 选项 -->
          <div class="options" v-if="answer.question?.options">
            <div 
              v-for="(value, key) in answer.question.options" 
              :key="key"
              class="option-item"
              :class="{
                'user-answer': isUserAnswer(answer.user_answer, key),
                'correct-answer': isCorrectAnswer(answer.question.answer, key),
                'wrong-answer': isUserAnswer(answer.user_answer, key) && !isCorrectAnswer(answer.question.answer, key)
              }"
            >
              <span class="option-key">{{ key }}</span>
              <span class="option-value">{{ value }}</span>
              <span class="option-icon" v-if="isCorrectAnswer(answer.question.answer, key) || (isUserAnswer(answer.user_answer, key) && !isCorrectAnswer(answer.question.answer, key))">
                <el-icon v-if="isCorrectAnswer(answer.question.answer, key)"><CircleCheck /></el-icon>
                <el-icon v-else><CircleClose /></el-icon>
              </span>
            </div>
          </div>
          
          <div class="answer-info">
            <p><strong>你的答案：</strong>{{ answer.user_answer || '未作答' }}</p>
            <p><strong>正确答案：</strong>{{ answer.question?.answer }}</p>
          </div>
          
          <div class="analysis" v-if="answer.question?.analysis">
            <strong>解析：</strong>{{ answer.question.analysis }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { examApi } from '@/api/exam'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const record = ref(null)

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '0秒'
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  if (m === 0) return `${s}秒`
  return `${m}分${s}秒`
}

// 检查是否是用户答案
const isUserAnswer = (userAnswer, key) => {
  if (!userAnswer) return false
  // 去除逗号后检查
  const answer = userAnswer.toUpperCase().replace(/,|，/g, '')
  return answer.includes(key.toUpperCase())
}

// 检查是否是正确答案
const isCorrectAnswer = (correctAnswer, key) => {
  if (!correctAnswer) return false
  // 去除逗号后检查
  const answer = correctAnswer.toUpperCase().replace(/,|，/g, '')
  return answer.includes(key.toUpperCase())
}

// 获取考试记录详情
const fetchRecord = async () => {
  loading.value = true
  try {
    const res = await examApi.getRecordDetail(route.params.id)
    record.value = res.data
  } catch (error) {
    console.error('获取考试记录失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecord()
})
</script>

<style lang="scss" scoped>
.exam-result {
  max-width: 900px;
  margin: 0 auto;
  
  .result-header {
    background: #fff;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    margin-bottom: 20px;
    
    .score-circle {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f56c6c, #f78989);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin: 0 auto 20px;
      
      &.passed {
        background: linear-gradient(135deg, #67c23a, #85ce61);
      }
      
      .score {
        font-size: 36px;
        font-weight: 700;
        color: #fff;
      }
      
      .label {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.9);
      }
    }
    
    h2 {
      font-size: 24px;
      margin-bottom: 30px;
    }
    
    .result-stats {
      display: flex;
      justify-content: center;
      gap: 40px;
      
      .stat-item {
        text-align: center;
        
        .value {
          display: block;
          font-size: 24px;
          font-weight: 600;
          color: #333;
        }
        
        .label {
          font-size: 13px;
          color: #999;
          margin-top: 5px;
        }
      }
    }
  }
  
  .result-actions {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .answer-detail {
    h3 {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 20px;
    }
    
    .question-item {
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 15px;
      border-left: 4px solid #e4e7ed;
      background: #fafafa;
      
      &.correct {
        border-left-color: #67c23a;
        background: #f0f9eb;
      }
      
      &.wrong {
        border-left-color: #f56c6c;
        background: #fef0f0;
      }
      
      .question-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;
        
        .question-num {
          font-weight: 600;
        }
        
        .score-info {
          margin-left: auto;
          font-size: 13px;
          color: #666;
        }
      }
      
      .question-content {
        .question-title {
          font-size: 15px;
          line-height: 1.6;
          margin-bottom: 15px;
        }
        
        .options {
          margin-bottom: 15px;
          
          .option-item {
            display: flex;
            align-items: flex-start;
            padding: 12px 16px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: #fff;
            border: 2px solid transparent;
            transition: all 0.2s;
            
            &.correct-answer {
              background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
              border-color: #67c23a;
              
              .option-key {
                background: linear-gradient(135deg, #67c23a, #85ce61);
                color: #fff;
              }
            }
            
            &.wrong-answer {
              background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%);
              border-color: #f56c6c;
              
              .option-key {
                background: linear-gradient(135deg, #f56c6c, #f78989);
                color: #fff;
              }
            }
            
            &.user-answer:not(.correct-answer):not(.wrong-answer) {
              border-color: #409eff;
              
              .option-key {
                background: linear-gradient(135deg, #409eff, #66b1ff);
                color: #fff;
              }
            }
            
            .option-key {
              width: 28px;
              height: 28px;
              min-width: 28px;
              max-width: 28px;
              border-radius: 50%;
              background: linear-gradient(135deg, #e4e7ed, #ebeef5);
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 13px;
              font-weight: 600;
              margin-right: 14px;
              flex-shrink: 0;
              transition: all 0.2s;
              box-sizing: border-box;
            }
            
            .option-value {
              flex: 1;
              line-height: 1.6;
              padding-top: 3px;
            }
            
            .option-icon {
              margin-left: 12px;
              flex-shrink: 0;
              
              .el-icon {
                font-size: 20px;
              }
            }
            
            &.correct-answer .option-icon {
              color: #67c23a;
            }
            
            &.wrong-answer .option-icon {
              color: #f56c6c;
            }
          }
        }
        
        .answer-info {
          font-size: 14px;
          color: #666;
          margin-bottom: 10px;
          
          p {
            margin-bottom: 5px;
          }
        }
        
        .analysis {
          font-size: 14px;
          color: #666;
          padding: 10px 15px;
          background: #fff;
          border-radius: 6px;
        }
      }
    }
  }
}
</style>
