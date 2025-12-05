<template>
  <div class="wrong-questions">
    <h1 class="page-title">错题本</h1>
    
    <div class="card filter-bar">
      <el-radio-group v-model="filter" @change="fetchWrongQuestions">
        <el-radio-button :value="null">全部</el-radio-button>
        <el-radio-button :value="0">未掌握</el-radio-button>
        <el-radio-button :value="1">已掌握</el-radio-button>
      </el-radio-group>
      
      <span class="total">共 {{ pagination.total }} 道错题</span>
    </div>
    
    <div class="question-list" v-loading="loading">
      <div 
        v-for="item in wrongQuestions" 
        :key="item.id"
        class="question-card"
        :class="{ mastered: item.is_mastered }"
      >
        <div class="question-header">
          <el-tag :type="questionTypeTag[item.question?.question_type]" size="small">
            {{ questionTypeMap[item.question?.question_type] }}
          </el-tag>
          <span class="wrong-count">错误 {{ item.wrong_count }} 次</span>
          <el-tag v-if="item.is_mastered" type="success" size="small">已掌握</el-tag>
        </div>
        
        <div class="question-title">{{ item.question?.title }}</div>
        
        <div class="options" v-if="item.question?.options">
          <div 
            v-for="(value, key) in item.question.options" 
            :key="key"
            class="option-item"
            :class="{
              'correct-answer': isCorrectAnswer(item.question.answer, key),
              'wrong-answer': isWrongAnswer(item.last_wrong_answer, item.question.answer, key)
            }"
          >
            <span class="option-key">{{ key }}</span>
            <span class="option-value">{{ value }}</span>
          </div>
        </div>
        
        <div class="answer-info">
          <p><strong>你的答案：</strong><span class="wrong">{{ item.last_wrong_answer || '未作答' }}</span></p>
          <p><strong>正确答案：</strong><span class="correct">{{ item.question?.answer }}</span></p>
        </div>
        
        <div class="analysis" v-if="item.question?.analysis">
          <strong>解析：</strong>{{ item.question.analysis }}
        </div>
        
        <div class="question-actions">
          <el-button 
            :type="item.is_mastered ? 'default' : 'success'"
            size="small"
            @click="toggleMastered(item)"
          >
            {{ item.is_mastered ? '取消掌握' : '标记已掌握' }}
          </el-button>
        </div>
      </div>
    </div>
    
    <el-empty v-if="!loading && wrongQuestions.length === 0" description="暂无错题" />
    
    <el-pagination
      v-if="pagination.total > pagination.pageSize"
      v-model:current-page="pagination.page"
      :total="pagination.total"
      :page-size="pagination.pageSize"
      layout="prev, pager, next"
      class="mt-20"
      @current-change="fetchWrongQuestions"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { examApi } from '@/api/exam'

const loading = ref(false)
const wrongQuestions = ref([])
const filter = ref(null)

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

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

// 检查是否是正确答案
const isCorrectAnswer = (correctAnswer, key) => {
  if (!correctAnswer) return false
  return correctAnswer.includes(key)
}

// 检查是否是错误答案
const isWrongAnswer = (wrongAnswer, correctAnswer, key) => {
  if (!wrongAnswer) return false
  return wrongAnswer.includes(key) && !correctAnswer.includes(key)
}

// 获取错题列表
const fetchWrongQuestions = async () => {
  loading.value = true
  try {
    const res = await examApi.getWrongQuestions({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      is_mastered: filter.value
    })
    wrongQuestions.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error('获取错题列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 切换掌握状态
const toggleMastered = async (item) => {
  try {
    await examApi.updateWrongQuestion(item.id, {
      is_mastered: item.is_mastered ? 0 : 1
    })
    item.is_mastered = item.is_mastered ? 0 : 1
    ElMessage.success(item.is_mastered ? '已标记为掌握' : '已取消掌握')
  } catch (error) {
    console.error('更新失败:', error)
  }
}

onMounted(() => {
  fetchWrongQuestions()
})
</script>

<style lang="scss" scoped>
.wrong-questions {
  .filter-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .total {
      color: #999;
      font-size: 14px;
    }
  }
  
  .question-list {
    .question-card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 16px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
      border-left: 4px solid #f56c6c;
      
      &.mastered {
        border-left-color: #67c23a;
        opacity: 0.8;
      }
      
      .question-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 15px;
        
        .wrong-count {
          font-size: 13px;
          color: #f56c6c;
        }
      }
      
      .question-title {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 15px;
      }
      
      .options {
        margin-bottom: 15px;
        
        .option-item {
          display: flex;
          align-items: center;
          padding: 10px 15px;
          margin-bottom: 8px;
          border-radius: 6px;
          background: #f9f9f9;
          
          &.correct-answer {
            background: #e1f3d8;
            
            .option-key {
              background: #67c23a;
              color: #fff;
            }
          }
          
          &.wrong-answer {
            background: #fde2e2;
            
            .option-key {
              background: #f56c6c;
              color: #fff;
            }
          }
          
          .option-key {
            width: 24px;
            height: 24px;
            min-width: 24px;
            max-width: 24px;
            border-radius: 50%;
            background: #e4e7ed;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
            margin-right: 12px;
            box-sizing: border-box;
          }
        }
      }
      
      .answer-info {
        font-size: 14px;
        margin-bottom: 12px;
        
        p {
          margin-bottom: 5px;
        }
        
        .wrong {
          color: #f56c6c;
        }
        
        .correct {
          color: #67c23a;
        }
      }
      
      .analysis {
        font-size: 14px;
        color: #666;
        padding: 12px 15px;
        background: #f5f7fa;
        border-radius: 6px;
        margin-bottom: 15px;
      }
      
      .question-actions {
        text-align: right;
      }
    }
  }
}
</style>
