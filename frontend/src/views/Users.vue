<template>
  <div>
    <div class="page-header">
      <h2>用户管理</h2>
    </div>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filters">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="用户名/姓名" clearable @keyup.enter="fetchUsers" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filters.role" placeholder="全部" clearable>
            <el-option v-for="role in roles" :key="role.value" :label="role.label" :value="role.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchUsers">查询</el-button>
          <el-button type="success" @click="handleAdd">新增用户</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="users" stripe>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'danger'">
              {{ row.status ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button 
              link 
              type="danger" 
              @click="handleDelete(row)"
              :disabled="row.username === 'admin'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchUsers"
          @current-change="fetchUsers"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option v-for="role in roles" :key="role.value" :label="role.label" :value="role.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch v-model="form.status" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const users = ref([])
const roles = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

const filters = reactive({
  search: '',
  role: ''
})

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

const form = reactive({
  id: null,
  username: '',
  real_name: '',
  password: '',
  role: 'operator',
  status: true
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑用户' : '新增用户')

const fetchUsers = async () => {
  try {
    const res = await api.get('/users', {
      params: {
        page: pagination.page,
        per_page: pagination.per_page,
        ...filters
      }
    })
    users.value = res.users
    pagination.total = res.total
  } catch (error) {
    console.error(error)
  }
}

const fetchRoles = async () => {
  try {
    const res = await api.get('/users/roles')
    roles.value = res
  } catch (error) {
    console.error(error)
  }
}

const getRoleType = (role) => {
  switch (role) {
    case 'admin': return 'danger'
    case 'operator': return 'primary'
    default: return 'info'
  }
}

const getRoleLabel = (role) => {
  const roleObj = roles.value.find(r => r.value === role)
  return roleObj ? roleObj.label : role
}

const resetForm = () => {
  Object.assign(form, {
    id: null,
    username: '',
    real_name: '',
    password: '',
    role: 'operator',
    status: true
  })
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, {
    id: row.id,
    username: row.username,
    real_name: row.real_name,
    role: row.role,
    status: row.status
  })
  isEdit.value = true
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/users/${row.id}`)
      ElMessage.success('删除成功')
      fetchUsers()
    } catch (error) {
      console.error(error)
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await api.put(`/users/${form.id}`, form)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users', form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchUsers()
      } catch (error) {
        console.error(error)
      }
    }
  })
}

onMounted(() => {
  fetchUsers()
  fetchRoles()
})
</script>
