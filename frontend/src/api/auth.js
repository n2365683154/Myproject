/**
 * 楚然智考系统 - 认证相关API
 */
import request from './request'

export const authApi = {
  // 获取图形验证码
  getCaptcha() {
    return request.get('/auth/captcha')
  },
  
  // 发送短信验证码
  sendSmsCode(data) {
    return request.post('/auth/sms/send', data)
  },
  
  // 密码登录
  login(data) {
    return request.post('/auth/login', data)
  },
  
  // 手机验证码登录
  loginByPhone(data) {
    return request.post('/auth/login/phone', data)
  },
  
  // 注册
  register(data) {
    return request.post('/auth/register', data)
  },
  
  // 重置密码
  resetPassword(data) {
    return request.post('/auth/password/reset', data)
  },
  
  // 获取当前用户信息
  getUserInfo() {
    return request.get('/auth/me')
  }
}
