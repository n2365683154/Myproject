/**
 * 楚然智考系统 - Axios请求封装
 */
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

// 创建axios实例
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    
    // 添加Token
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const { response } = error
    
    if (response) {
      const { status, data } = response
      
      switch (status) {
        case 400:
          ElMessage.error(data.detail || '请求参数错误')
          break
        case 401:
          // 如果已经在登录页面，不弹出提示
          if (window.location.pathname === '/login') {
            break
          }
          ElMessageBox.confirm(
            '登录已过期，请重新登录',
            '提示',
            {
              confirmButtonText: '重新登录',
              cancelButtonText: '取消',
              type: 'warning'
            }
          ).then(() => {
            const userStore = useUserStore()
            userStore.logout()
          }).catch(() => {})
          break
        case 403:
          ElMessage.error(data.detail || '没有操作权限')
          break
        case 404:
          ElMessage.error(data.detail || '请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败，请检查网络')
    }
    
    return Promise.reject(error)
  }
)

export default request
