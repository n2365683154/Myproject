<template>
  <div class="user-list">
    <h1 class="page-title">用户管理</h1>
    
    <!-- 搜索栏 -->
    <div class="card search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input 
            v-model="searchForm.keyword" 
            placeholder="用户名/姓名/手机号"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role_id" placeholder="全部" clearable>
            <el-option 
              v-for="role in roles" 
              :key="role.id" 
              :label="role.name" 
              :value="role.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        添加用户
      </el-button>
    </div>
    
    <!-- 用户表格 -->
    <div class="card">
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column label="角色" width="150">
          <template #default="{ row }">
            <el-tag 
              v-for="role in row.roles" 
              :key="role.id"
              size="small"
              class="mr-5"
            >
              {{ role.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showEditDialog(row)">
              编辑
            </el-button>
            <el-button type="primary" link @click="showRoleDialog(row)">
              分配角色
            </el-button>
            <el-popconfirm 
              title="确定删除该用户吗？"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="mt-20"
        @size-change="fetchUsers"
        @current-change="fetchUsers"
      />
    </div>
    
    <!-- 创建/编辑用户弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingUser ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="form.username" 
            :disabled="!!editingUser"
            placeholder="请输入用户名"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input 
            v-model="form.password" 
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio :label="0">未知</el-radio>
            <el-radio :label="1">男</el-radio>
            <el-radio :label="2">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态" prop="is_active" v-if="editingUser">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 分配角色弹窗 -->
    <el-dialog v-model="roleDialogVisible" title="分配角色" width="400px">
      <el-checkbox-group v-model="selectedRoles">
        <el-checkbox 
          v-for="role in roles" 
          :key="role.id" 
          :label="role.id"
        >
          {{ role.name }}
        </el-checkbox>
      </el-checkbox-group>
      
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleAssignRoles">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api/user'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const roles = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  role_id: null,
  is_active: null
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 弹窗
const dialogVisible = ref(false)
const roleDialogVisible = ref(false)
const editingUser = ref(null)
const selectedRoles = ref([])

// 表单
const formRef = ref()
const form = reactive({
  username: '',
  password: '',
  real_name: '',
  phone: '',
  email: '',
  gender: 0,
  is_active: true
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

// 格式化日期
const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await userApi.getUsers({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    })
    users.value = res.data.items
    pagination.total = res.data.total
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取角色列表
const fetchRoles = async () => {
  try {
    const res = await userApi.getRoles()
    roles.value = res.data
  } catch (error) {
    console.error('获取角色列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchUsers()
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.role_id = null
  searchForm.is_active = null
  handleSearch()
}

// 显示创建弹窗
const showCreateDialog = () => {
  editingUser.value = null
  Object.assign(form, {
    username: '',
    password: '',
    real_name: '',
    phone: '',
    email: '',
    gender: 0,
    is_active: true
  })
  dialogVisible.value = true
}

// 显示编辑弹窗
const showEditDialog = (user) => {
  editingUser.value = user
  Object.assign(form, {
    username: user.username,
    real_name: user.real_name || '',
    phone: user.phone || '',
    email: user.email || '',
    gender: user.gender || 0,
    is_active: user.is_active
  })
  dialogVisible.value = true
}

// 显示角色分配弹窗
const showRoleDialog = (user) => {
  editingUser.value = user
  selectedRoles.value = user.roles?.map(r => r.id) || []
  roleDialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (editingUser.value) {
      await userApi.updateUser(editingUser.value.id, {
        real_name: form.real_name,
        phone: form.phone || null,
        email: form.email || null,
        gender: form.gender,
        is_active: form.is_active
      })
      ElMessage.success('更新成功')
    } else {
      // 创建用户时，处理空字段
      const createData = {
        username: form.username,
        password: form.password,
        real_name: form.real_name || null,
        phone: form.phone || null,
        email: form.email || null,
        gender: form.gender
      }
      await userApi.createUser(createData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchUsers()
  } catch (error) {
    console.error('操作失败:', error)
    const msg = error.response?.data?.detail || '操作失败'
    ElMessage.error(msg)
  } finally {
    submitting.value = false
  }
}

// 分配角色
const handleAssignRoles = async () => {
  submitting.value = true
  try {
    await userApi.assignRoles(editingUser.value.id, selectedRoles.value)
    ElMessage.success('角色分配成功')
    roleDialogVisible.value = false
    fetchUsers()
  } catch (error) {
    console.error('分配角色失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除用户
const handleDelete = async (id) => {
  try {
    await userApi.deleteUser(id)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  fetchUsers()
  fetchRoles()
})
</script>

<style lang="scss" scoped>
.user-list {
  .search-bar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    
    .el-form {
      flex: 1;
    }
  }
  
  .mr-5 {
    margin-right: 5px;
  }
}
</style>
