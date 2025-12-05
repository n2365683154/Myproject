<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-left">
        <div class="brand">
          <h1>楚然智考系统</h1>
          <p>专业的在线考试平台</p>
        </div>
        <div class="features">
          <div class="feature-item">
            <el-icon><Document /></el-icon>
            <span>海量题库，智能组卷</span>
          </div>
          <div class="feature-item">
            <el-icon><Timer /></el-icon>
            <span>在线考试，自动判分</span>
          </div>
          <div class="feature-item">
            <el-icon><DataLine /></el-icon>
            <span>错题回顾，学习统计</span>
          </div>
        </div>
      </div>
      
      <div class="login-right">
        <div class="login-form-container">
          <h2>欢迎登录</h2>
          
          <el-form 
            ref="loginFormRef" 
            :model="loginForm" 
            :rules="loginRules"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="username">
              <el-input 
                v-model="loginForm.username" 
                placeholder="用户名/手机号"
                prefix-icon="User"
                size="large"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="密码"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>
            
            <el-form-item prop="captcha_code">
              <div class="captcha-row">
                <el-input 
                  v-model="loginForm.captcha_code" 
                  placeholder="验证码"
                  prefix-icon="Key"
                  size="large"
                  @keyup.enter="handleLogin"
                />
                <img 
                  :src="captchaImage" 
                  class="captcha-img" 
                  @click="refreshCaptcha"
                  title="点击刷新"
                />
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                size="large" 
                :loading="loading"
                native-type="submit"
                class="login-btn"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="login-footer">
            <span>还没有账号？</span>
            <el-button type="primary" link @click="showRegister = true">
              立即注册
            </el-button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 注册弹窗 -->
    <el-dialog 
      v-model="showRegister" 
      title="用户注册" 
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="registerFormRef" 
        :model="registerForm" 
        :rules="registerRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号（选填）" />
        </el-form-item>
        
        <el-form-item label="验证码" prop="captcha_code">
          <div class="captcha-row">
            <el-input v-model="registerForm.captcha_code" placeholder="验证码" />
            <img 
              :src="captchaImage" 
              class="captcha-img" 
              @click="refreshCaptcha"
            />
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleRegister">
          注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const showRegister = ref(false)

// 验证码
const captchaKey = ref('')
const captchaImage = ref('')

// 登录表单
const loginFormRef = ref()
const loginForm = ref({
  username: '',
  password: '',
  captcha_code: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名或手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha_code: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

// 注册表单
const registerFormRef = ref()
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  phone: '',
  captcha_code: ''
})

// 确认密码验证
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.value.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  captcha_code: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

// 获取验证码
const refreshCaptcha = async () => {
  try {
    const res = await authApi.getCaptcha()
    captchaKey.value = res.data.captcha_key
    captchaImage.value = res.data.captcha_image
  } catch (error) {
    console.error('获取验证码失败:', error)
  }
}

// 登录
const handleLogin = async () => {
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await userStore.login({
      username: loginForm.value.username,
      password: loginForm.value.password,
      captcha_key: captchaKey.value,
      captcha_code: loginForm.value.captcha_code
    })
    ElMessage.success('登录成功')
    
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

// 注册
const handleRegister = async () => {
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await authApi.register({
      username: registerForm.value.username,
      password: registerForm.value.password,
      phone: registerForm.value.phone || undefined,
      captcha_key: captchaKey.value,
      captcha_code: registerForm.value.captcha_code
    })
    ElMessage.success('注册成功，请登录')
    showRegister.value = false
    refreshCaptcha()
    
    // 自动填充用户名
    loginForm.value.username = registerForm.value.username
  } catch (error) {
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

// 清除token但不跳转
const clearToken = () => {
  // 清除cookie
  document.cookie = 'token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'
  // 清除localStorage
  localStorage.removeItem('token')
}

onMounted(() => {
  // 进入登录页时清除旧的token，避免过期token导致问题
  clearToken()
  refreshCaptcha()
})
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 900px;
  max-width: 100%;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  overflow: hidden;
}

.login-left {
  width: 400px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 40px;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  
  .brand {
    margin-bottom: 60px;
    
    h1 {
      font-size: 32px;
      font-weight: 600;
      margin-bottom: 10px;
    }
    
    p {
      font-size: 16px;
      opacity: 0.9;
    }
  }
  
  .features {
    .feature-item {
      display: flex;
      align-items: center;
      margin-bottom: 20px;
      font-size: 15px;
      
      .el-icon {
        font-size: 24px;
        margin-right: 15px;
      }
    }
  }
}

.login-right {
  flex: 1;
  padding: 60px 50px;
  
  .login-form-container {
    max-width: 360px;
    margin: 0 auto;
    
    h2 {
      font-size: 24px;
      font-weight: 600;
      color: #333;
      margin-bottom: 30px;
      text-align: center;
    }
    
    .login-tabs {
      :deep(.el-tabs__header) {
        margin-bottom: 20px;
      }
    }
    
    .captcha-row,
    .sms-row {
      display: flex;
      gap: 10px;
      
      .el-input {
        flex: 1;
      }
      
      .captcha-img {
        height: 40px;
        cursor: pointer;
        border-radius: 4px;
      }
      
      .el-button {
        width: 120px;
      }
    }
    
    .login-btn {
      width: 100%;
    }
    
    .login-footer {
      text-align: center;
      margin-top: 20px;
      color: #666;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .login-left {
    width: 100%;
    padding: 40px 30px;
    
    .brand {
      margin-bottom: 30px;
      text-align: center;
      
      h1 {
        font-size: 24px;
      }
    }
    
    .features {
      display: none;
    }
  }
  
  .login-right {
    padding: 40px 30px;
  }
}
</style>
