/**
 * 楚然智考系统 - 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import router from '@/router'

// Cookie工具函数
const setCookie = (name, value, hours) => {
  const expires = new Date()
  expires.setTime(expires.getTime() + hours * 60 * 60 * 1000)
  document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/`
}

const getCookie = (name) => {
  const nameEQ = name + '='
  const ca = document.cookie.split(';')
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i].trim()
    if (c.indexOf(nameEQ) === 0) {
      return decodeURIComponent(c.substring(nameEQ.length))
    }
  }
  return ''
}

const deleteCookie = (name) => {
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`
}

export const useUserStore = defineStore('user', () => {
  // 状态 - 优先从cookie读取，兼容localStorage
  const token = ref(getCookie('token') || localStorage.getItem('token') || '')
  const userInfo = ref(null)
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const roles = computed(() => userInfo.value?.roles || [])
  const permissions = computed(() => userInfo.value?.permissions || [])
  const isAdmin = computed(() => roles.value.includes('admin') || userInfo.value?.is_superuser)
  
  // 检查权限
  const hasPermission = (permission) => {
    if (userInfo.value?.is_superuser) return true
    return permissions.value.includes(permission)
  }
  
  // 检查角色
  const hasRole = (role) => {
    if (userInfo.value?.is_superuser) return true
    return roles.value.includes(role)
  }
  
  // 设置Token（存储到cookie，有效期2小时）
  const setToken = (newToken) => {
    token.value = newToken
    setCookie('token', newToken, 2) // 2小时有效期
    localStorage.setItem('token', newToken) // 同时存localStorage作为备份
  }
  
  // 获取用户信息
  const getUserInfo = async () => {
    try {
      const res = await authApi.getUserInfo()
      userInfo.value = res.data
      return res.data
    } catch (error) {
      throw error
    }
  }
  
  // 登录（用户名/手机号 + 密码）
  const login = async (loginData) => {
    try {
      const res = await authApi.login(loginData)
      setToken(res.data.access_token)
      await getUserInfo()
      return res.data
    } catch (error) {
      throw error
    }
  }
  
  // 退出登录
  const logout = () => {
    token.value = ''
    userInfo.value = null
    deleteCookie('token') // 清除cookie
    localStorage.removeItem('token') // 清除localStorage
    router.push('/login')
  }
  
  return {
    token,
    userInfo,
    isLoggedIn,
    roles,
    permissions,
    isAdmin,
    hasPermission,
    hasRole,
    setToken,
    getUserInfo,
    login,
    logout
  }
})
