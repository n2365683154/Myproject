<template>
  <div class="knowledge-tree">
    <h1 class="page-title">知识点管理</h1>
    
    <div class="card">
      <div class="toolbar">
        <el-button type="primary" @click="showCreateDialog(null)">
          <el-icon><Plus /></el-icon>
          添加根节点
        </el-button>
      </div>
      
      <el-tree
        ref="treeRef"
        :data="treeData"
        :props="{ label: 'name', children: 'children' }"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
        v-loading="loading"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span class="node-label">{{ data.name }}</span>
            <span class="node-actions">
              <el-button type="primary" link size="small" @click="showCreateDialog(data)">
                添加子节点
              </el-button>
              <el-button type="primary" link size="small" @click="showEditDialog(data)">
                编辑
              </el-button>
              <el-popconfirm 
                title="确定删除该知识点吗？"
                @confirm="handleDelete(data.id)"
              >
                <template #reference>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </span>
          </div>
        </template>
      </el-tree>
      
      <el-empty v-if="!loading && treeData.length === 0" description="暂无知识点" />
    </div>
    
    <!-- 创建/编辑弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingNode ? '编辑知识点' : '添加知识点'"
      width="500px"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入知识点名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入知识点编码（选填）" />
        </el-form-item>
        <el-form-item label="父级" v-if="!editingNode">
          <el-input :value="parentNode?.name || '根节点'" disabled />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入描述（选填）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { questionApi } from '@/api/question'

const loading = ref(false)
const submitting = ref(false)
const treeData = ref([])
const treeRef = ref()

// 弹窗
const dialogVisible = ref(false)
const editingNode = ref(null)
const parentNode = ref(null)

// 表单
const formRef = ref()
const form = reactive({
  name: '',
  code: '',
  parent_id: null,
  sort_order: 0,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入知识点名称', trigger: 'blur' }]
}

// 获取知识点树
const fetchTree = async () => {
  loading.value = true
  try {
    const res = await questionApi.getKnowledgeTree()
    treeData.value = res.data
  } catch (error) {
    console.error('获取知识点失败:', error)
  } finally {
    loading.value = false
  }
}

// 显示创建弹窗
const showCreateDialog = (parent) => {
  editingNode.value = null
  parentNode.value = parent
  Object.assign(form, {
    name: '',
    code: '',
    parent_id: parent?.id || null,
    sort_order: 0,
    description: ''
  })
  dialogVisible.value = true
}

// 显示编辑弹窗
const showEditDialog = (node) => {
  editingNode.value = node
  parentNode.value = null
  Object.assign(form, {
    name: node.name,
    code: node.code || '',
    parent_id: node.parent_id,
    sort_order: node.sort_order || 0,
    description: node.description || ''
  })
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (editingNode.value) {
      await questionApi.updateKnowledgePoint(editingNode.value.id, form)
      ElMessage.success('更新成功')
    } else {
      await questionApi.createKnowledgePoint(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchTree()
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除知识点
const handleDelete = async (id) => {
  try {
    await questionApi.deleteKnowledgePoint(id)
    ElMessage.success('删除成功')
    fetchTree()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  fetchTree()
})
</script>

<style lang="scss" scoped>
.knowledge-tree {
  .toolbar {
    margin-bottom: 20px;
  }
  
  .tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-right: 10px;
    
    .node-label {
      font-size: 14px;
    }
    
    .node-actions {
      opacity: 0;
      transition: opacity 0.2s;
    }
    
    &:hover .node-actions {
      opacity: 1;
    }
  }
}
</style>
