<template>
  <div class="role-list">
    <h1 class="page-title">角色管理</h1>
    
    <div class="card">
      <div class="toolbar">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          添加角色
        </el-button>
      </div>
      
      <el-table :data="roles" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色编码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="权限数" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.permissions?.length || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showEditDialog(row)">
              编辑
            </el-button>
            <el-button type="primary" link @click="showPermissionDialog(row)">
              配置权限
            </el-button>
            <el-popconfirm 
              title="确定删除该角色吗？"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 创建/编辑角色弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingRole ? '编辑角色' : '添加角色'"
      width="500px"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="80px"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input 
            v-model="form.code" 
            :disabled="!!editingRole"
            placeholder="请输入角色编码，如：admin"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active" v-if="editingRole">
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
    
    <!-- 配置权限弹窗 -->
    <el-dialog 
      v-model="permissionDialogVisible" 
      title="配置权限" 
      width="600px"
    >
      <div class="permission-groups">
        <div 
          v-for="(perms, module) in groupedPermissions" 
          :key="module"
          class="permission-group"
        >
          <div class="group-title">{{ moduleNames[module] || module }}</div>
          <el-checkbox-group v-model="selectedPermissions">
            <el-checkbox 
              v-for="perm in perms" 
              :key="perm.id" 
              :label="perm.id"
            >
              {{ perm.name }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSavePermissions">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api/user'

const loading = ref(false)
const submitting = ref(false)
const roles = ref([])
const permissions = ref([])

// 弹窗
const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const editingRole = ref(null)
const selectedPermissions = ref([])

// 表单
const formRef = ref()
const form = reactive({
  name: '',
  code: '',
  description: '',
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }]
}

// 模块名称映射
const moduleNames = {
  user: '用户管理',
  role: '角色管理',
  question: '题库管理',
  knowledge: '知识点管理',
  exam: '考试管理',
  stats: '统计分析',
  system: '系统设置'
}

// 按模块分组权限
const groupedPermissions = computed(() => {
  const groups = {}
  permissions.value.forEach(perm => {
    const module = perm.module || 'other'
    if (!groups[module]) {
      groups[module] = []
    }
    groups[module].push(perm)
  })
  return groups
})

// 获取角色列表
const fetchRoles = async () => {
  loading.value = true
  try {
    const res = await userApi.getRoles()
    roles.value = res.data
  } catch (error) {
    console.error('获取角色列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取权限列表
const fetchPermissions = async () => {
  try {
    const res = await userApi.getPermissions()
    permissions.value = res.data
  } catch (error) {
    console.error('获取权限列表失败:', error)
  }
}

// 显示创建弹窗
const showCreateDialog = () => {
  editingRole.value = null
  Object.assign(form, {
    name: '',
    code: '',
    description: '',
    is_active: true
  })
  dialogVisible.value = true
}

// 显示编辑弹窗
const showEditDialog = (role) => {
  editingRole.value = role
  Object.assign(form, {
    name: role.name,
    code: role.code,
    description: role.description || '',
    is_active: role.is_active
  })
  dialogVisible.value = true
}

// 显示权限配置弹窗
const showPermissionDialog = (role) => {
  editingRole.value = role
  selectedPermissions.value = role.permissions?.map(p => p.id) || []
  permissionDialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (editingRole.value) {
      await userApi.updateRole(editingRole.value.id, {
        name: form.name,
        description: form.description,
        is_active: form.is_active
      })
      ElMessage.success('更新成功')
    } else {
      await userApi.createRole(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchRoles()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

// 保存权限配置
const handleSavePermissions = async () => {
  submitting.value = true
  try {
    await userApi.updateRole(editingRole.value.id, {
      permission_ids: selectedPermissions.value
    })
    ElMessage.success('权限配置成功')
    permissionDialogVisible.value = false
    fetchRoles()
  } catch (error) {
    console.error('配置权限失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除角色
const handleDelete = async (id) => {
  try {
    await userApi.deleteRole(id)
    ElMessage.success('删除成功')
    fetchRoles()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  fetchRoles()
  fetchPermissions()
})
</script>

<style lang="scss" scoped>
.role-list {
  .toolbar {
    margin-bottom: 20px;
  }
  
  .permission-groups {
    max-height: 400px;
    overflow-y: auto;
    
    .permission-group {
      margin-bottom: 20px;
      
      .group-title {
        font-weight: 600;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
      }
      
      .el-checkbox {
        margin-right: 20px;
        margin-bottom: 10px;
      }
    }
  }
}
</style>
