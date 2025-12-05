/**
 * 楚然智考系统 - 用户管理API
 */
import request from './request'

export const userApi = {
  // 获取用户列表
  getUsers(params) {
    return request.get('/users', { params })
  },
  
  // 获取用户详情
  getUser(id) {
    return request.get(`/users/${id}`)
  },
  
  // 创建用户
  createUser(data) {
    return request.post('/users', data)
  },
  
  // 更新用户
  updateUser(id, data) {
    return request.put(`/users/${id}`, data)
  },
  
  // 删除用户
  deleteUser(id) {
    return request.delete(`/users/${id}`)
  },
  
  // 分配角色
  assignRoles(id, roleIds) {
    return request.put(`/users/${id}/roles`, roleIds)
  },
  
  // 修改密码
  changePassword(data) {
    return request.put('/users/me/password', data)
  },
  
  // 更新个人信息
  updateProfile(data) {
    return request.put('/users/me/profile', data)
  },
  
  // 获取角色列表
  getRoles() {
    return request.get('/users/roles/list')
  },
  
  // 创建角色
  createRole(data) {
    return request.post('/users/roles', data)
  },
  
  // 更新角色
  updateRole(id, data) {
    return request.put(`/users/roles/${id}`, data)
  },
  
  // 删除角色
  deleteRole(id) {
    return request.delete(`/users/roles/${id}`)
  },
  
  // 获取权限列表
  getPermissions() {
    return request.get('/users/permissions/list')
  }
}
