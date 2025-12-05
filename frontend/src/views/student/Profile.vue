<template>
  <div class="profile">
    <h1 class="page-title">个人中心</h1>
    
    <el-row :gutter="20">
      <el-col :xs="24" :lg="8">
        <div class="card user-card">
          <div class="avatar-section">
            <el-avatar :size="80" :src="userStore.userInfo?.avatar">
              {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <h3>{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}</h3>
            <p>{{ userStore.userInfo?.phone || userStore.userInfo?.email || '未绑定联系方式' }}</p>
          </div>
          
          <div class="info-list">
            <div class="info-item">
              <span class="label">用户名</span>
              <span class="value">{{ userStore.userInfo?.username }}</span>
            </div>
            <div class="info-item">
              <span class="label">角色</span>
              <span class="value">
                <el-tag v-for="role in userStore.roles" :key="role" size="small">
                  {{ role === 'admin' ? '管理员' : '学员' }}
                </el-tag>
              </span>
            </div>
            <div class="info-item">
              <span class="label">注册时间</span>
              <span class="value">{{ formatDate(userStore.userInfo?.created_at) }}</span>
            </div>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :lg="16">
        <el-tabs v-model="activeTab" class="profile-tabs">
          <el-tab-pane label="基本信息" name="info">
            <div class="card">
              <el-form 
                ref="infoFormRef" 
                :model="infoForm" 
                :rules="infoRules"
                label-width="80px"
              >
                <el-form-item label="真实姓名" prop="real_name">
                  <el-input v-model="infoForm.real_name" placeholder="请输入真实姓名" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="infoForm.phone" placeholder="请输入手机号" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="infoForm.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="性别" prop="gender">
                  <el-radio-group v-model="infoForm.gender">
                    <el-radio :value="0">保密</el-radio>
                    <el-radio :value="1">男</el-radio>
                    <el-radio :value="2">女</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="saving" @click="saveInfo">
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="修改密码" name="password">
            <div class="card">
              <el-form 
                ref="passwordFormRef" 
                :model="passwordForm" 
                :rules="passwordRules"
                label-width="100px"
              >
                <el-form-item label="当前密码" prop="old_password">
                  <el-input 
                    v-model="passwordForm.old_password" 
                    type="password"
                    placeholder="请输入当前密码"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="新密码" prop="new_password">
                  <el-input 
                    v-model="passwordForm.new_password" 
                    type="password"
                    placeholder="请输入新密码"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="确认新密码" prop="confirm_password">
                  <el-input 
                    v-model="passwordForm.confirm_password" 
                    type="password"
                    placeholder="请再次输入新密码"
                    show-password
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="saving" @click="changePassword">
                    修改密码
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { userApi } from '@/api/user'
import dayjs from 'dayjs'

const userStore = useUserStore()
const activeTab = ref('info')
const saving = ref(false)

// 格式化日期
const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD') : '-'
}

// 基本信息表单
const infoFormRef = ref()
const infoForm = reactive({
  real_name: '',
  phone: '',
  email: '',
  gender: 0
})

const infoRules = {
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

// 密码表单
const passwordFormRef = ref()
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 初始化表单
const initForm = () => {
  const user = userStore.userInfo
  if (user) {
    infoForm.real_name = user.real_name || ''
    infoForm.phone = user.phone || ''
    infoForm.email = user.email || ''
    infoForm.gender = user.gender || 0
  }
}

// 保存基本信息
const saveInfo = async () => {
  const valid = await infoFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    await userApi.updateProfile(infoForm)
    await userStore.getUserInfo()
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

// 修改密码
const changePassword = async () => {
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    await userApi.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码修改成功')
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (error) {
    console.error('修改密码失败:', error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  initForm()
})
</script>

<style lang="scss" scoped>
.profile {
  .user-card {
    text-align: center;
    
    .avatar-section {
      padding: 30px 0;
      border-bottom: 1px solid #f0f0f0;
      
      .el-avatar {
        margin-bottom: 15px;
      }
      
      h3 {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
      }
      
      p {
        font-size: 14px;
        color: #999;
      }
    }
    
    .info-list {
      padding: 20px 0;
      
      .info-item {
        display: flex;
        justify-content: space-between;
        padding: 12px 20px;
        
        .label {
          color: #999;
        }
        
        .value {
          color: #333;
        }
      }
    }
  }
  
  .profile-tabs {
    :deep(.el-tabs__header) {
      background: #fff;
      padding: 0 20px;
      border-radius: 8px 8px 0 0;
      margin-bottom: 0;
    }
    
    :deep(.el-tabs__content) {
      padding: 0;
    }
    
    .card {
      border-radius: 0 0 8px 8px;
    }
  }
}
</style>
