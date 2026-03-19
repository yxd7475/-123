<template>
  <div class="items-page">
    <div class="page-header">
      <h2>物品管理</h2>
      <p class="page-desc">管理所有物品信息，支持批量导入</p>
    </div>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filters">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="编码/名称/规格" clearable @keyup.enter="fetchItems" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.category" placeholder="全部" clearable>
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="启用" value="true" />
            <el-option label="禁用" value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchItems">查询</el-button>
          <el-button type="success" @click="handleAdd" v-if="authStore.hasAnyRole(['admin', 'operator'])">新增物品</el-button>
          <el-button type="warning" @click="importDialogVisible = true" v-if="authStore.hasAnyRole(['admin', 'operator'])">
            <el-icon><Upload /></el-icon>
            一键导入
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="items" stripe>
        <el-table-column label="图片" width="80">
          <template #default="{ row }">
            <el-image 
              v-if="row.image" 
              :src="getImageUrl(row.image)" 
              :preview-src-list="[getImageUrl(row.image)]"
              :initial-index="0"
              fit="cover"
              class="table-image"
              lazy
              :preview-teleported="true"
              :scroll-container="false"
            >
              <template #placeholder>
                <div class="image-placeholder-loading">
                  <el-icon class="is-loading"><Loading /></el-icon>
                </div>
              </template>
              <template #error>
                <div class="image-placeholder-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <span v-else class="no-image">暂无</span>
          </template>
        </el-table-column>
        <el-table-column prop="item_code" label="物品编码" width="120" />
        <el-table-column prop="name" label="物品名称" width="150" />
        <el-table-column prop="specification" label="规格" width="120" />
        <el-table-column prop="model" label="型号" width="100" />
        <el-table-column prop="attribute" label="属性" width="100" />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">¥{{ row.unit_price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="库存数量" width="100">
          <template #default="{ row }">
            <span :class="getQuantityClass(row)">{{ row.quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="location" label="存放位置" width="150" />
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-cell">
              <el-button 
                v-if="authStore.hasAnyRole(['admin', 'operator'])"
                class="action-primary" 
                size="small"
                @click="handleInbound(row)"
              >
                入库
              </el-button>
              <el-button 
                v-if="authStore.hasAnyRole(['admin', 'operator'])"
                class="action-secondary" 
                size="small"
                @click="handleOutbound(row)"
              >
                领用
              </el-button>
              <el-dropdown 
                trigger="click" 
                @command="(cmd) => handleCommand(cmd, row)"
                placement="bottom-end"
              >
                <el-button class="action-more" size="small">
                  <el-icon :size="14"><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu class="action-dropdown-menu">
                    <el-dropdown-item command="view">
                      <el-icon><View /></el-icon>
                      <span>查看详情</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="edit" v-if="authStore.hasAnyRole(['admin', 'operator'])">
                      <el-icon><Edit /></el-icon>
                      <span>编辑</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided v-if="authStore.hasRole('admin')">
                      <el-icon class="delete-icon"><Delete /></el-icon>
                      <span class="delete-text">删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
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
          @size-change="fetchItems"
          @current-change="fetchItems"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" :disabled="isView">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="物品编码" prop="item_code">
              <el-input v-model="form.item_code" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物品名称" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规格" prop="specification">
              <el-input v-model="form.specification" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="型号" prop="model">
              <el-input v-model="form.model" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="属性" prop="attribute">
              <el-input v-model="form.attribute" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品牌" prop="brand">
              <el-input v-model="form.brand" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="form.unit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="库存下限" prop="min_quantity">
              <el-input-number v-model="form.min_quantity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="库存上限" prop="max_quantity">
              <el-input-number v-model="form.max_quantity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-input v-model="form.category" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="存放位置" prop="location">
              <el-input v-model="form.location" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="供应商" prop="supplier">
          <el-input v-model="form.supplier" />
        </el-form-item>
        <el-form-item label="物品图片" prop="image">
          <div class="image-upload-wrapper">
            <el-upload
              class="image-uploader"
              :action="uploadUrl"
              :headers="uploadHeaders"
              :show-file-list="false"
              :on-success="handleUploadSuccess"
              :before-upload="beforeUpload"
              accept="image/*"
            >
              <img v-if="form.image" :src="getImageUrl(form.image)" class="image-preview" />
              <div v-else class="upload-placeholder">
                <el-icon class="upload-icon"><Plus /></el-icon>
                <span class="upload-text">点击上传</span>
              </div>
            </el-upload>
            <div v-if="form.image" class="image-actions">
              <el-button type="danger" size="small" @click="handleRemoveImage">
                <el-icon><Delete /></el-icon>
                删除图片
              </el-button>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer v-if="!isView">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" title="一键导入物品" width="500px">
      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          <p>1. 支持 Excel (.xlsx, .xls) 和 CSV 格式文件</p>
          <p>2. 系统会自动识别列名，无需严格按照模板格式</p>
          <p>3. 物品编码可留空，系统将自动生成</p>
          <p>4. 重复的物品编码将被跳过</p>
        </template>
      </el-alert>
      
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
        accept=".xlsx,.xls,.csv"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/xls/csv 文件
          </div>
        </template>
      </el-upload>
      
      <div style="margin-top: 15px">
        <el-button type="primary" link @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          下载导入模板
        </el-button>
      </div>
      
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing">
          开始导入
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resultDialogVisible" title="导入结果" width="500px">
      <el-result
        :icon="importResult.error_count > 0 ? 'warning' : 'success'"
        :title="importResult.success_count > 0 ? '导入完成' : '导入失败'"
      >
        <template #sub-title>
          <div style="text-align: left">
            <p>成功导入: <span style="color: #67c23a; font-weight: bold">{{ importResult.success_count }}</span> 条</p>
            <p>跳过重复: <span style="color: #909399; font-weight: bold">{{ importResult.skip_count }}</span> 条</p>
            <p v-if="importResult.error_count > 0">
              导入失败: <span style="color: #f56c6c; font-weight: bold">{{ importResult.error_count }}</span> 条
            </p>
          </div>
        </template>
        <template #extra>
          <div v-if="importResult.errors && importResult.errors.length > 0" style="text-align: left; max-height: 200px; overflow-y: auto">
            <el-alert
              v-for="(error, index) in importResult.errors"
              :key="index"
              :title="error"
              type="error"
              :closable="false"
              style="margin-bottom: 5px"
            />
          </div>
        </template>
      </el-result>
      <template #footer>
        <el-button type="primary" @click="resultDialogVisible = false">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="inboundDialogVisible" title="物品入库" width="450px">
      <el-form ref="inboundFormRef" :model="inboundForm" :rules="inboundRules" label-width="100px">
        <el-form-item label="物品信息">
          <div class="item-info">
            <span class="item-name">{{ currentItem?.name }}</span>
            <span class="item-code">({{ currentItem?.item_code }})</span>
          </div>
        </el-form-item>
        <el-form-item label="当前库存">
          <span class="current-stock">{{ currentItem?.quantity }} {{ currentItem?.unit }}</span>
        </el-form-item>
        <el-form-item label="入库数量" prop="quantity">
          <el-input-number v-model="inboundForm.quantity" :min="1" :precision="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="入库单价" prop="unit_price">
          <el-input-number v-model="inboundForm.unit_price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="inboundForm.supplier" placeholder="请输入供应商" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="inboundForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="inboundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitInbound" :loading="inboundLoading">确认入库</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="outboundDialogVisible" title="物品领取" width="450px">
      <el-form ref="outboundFormRef" :model="outboundForm" :rules="outboundRules" label-width="100px">
        <el-form-item label="物品信息">
          <div class="item-info">
            <span class="item-name">{{ currentItem?.name }}</span>
            <span class="item-code">({{ currentItem?.item_code }})</span>
          </div>
        </el-form-item>
        <el-form-item label="当前库存">
          <span class="current-stock">{{ currentItem?.quantity }} {{ currentItem?.unit }}</span>
        </el-form-item>
        <el-form-item label="领取数量" prop="quantity">
          <el-input-number v-model="outboundForm.quantity" :min="1" :max="currentItem?.quantity || 1" :precision="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="领取人" prop="recipient">
          <el-input v-model="outboundForm.recipient" placeholder="请输入领取人" />
        </el-form-item>
        <el-form-item label="领取部门">
          <el-input v-model="outboundForm.department" placeholder="请输入领取部门" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="outboundForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="outboundDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOutbound" :loading="outboundLoading">确认领取</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Download, Upload, View, Edit, MoreFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()

const items = ref([])
const categories = ref([])
const dialogVisible = ref(false)
const isView = ref(false)
const isEdit = ref(false)
const formRef = ref()
const importDialogVisible = ref(false)
const resultDialogVisible = ref(false)
const importing = ref(false)
const uploadRef = ref()
const selectedFile = ref(null)
const inboundDialogVisible = ref(false)
const outboundDialogVisible = ref(false)
const inboundLoading = ref(false)
const outboundLoading = ref(false)
const inboundFormRef = ref()
const outboundFormRef = ref()
const currentItem = ref(null)

const uploadUrl = '/api/items/upload-image'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const importResult = reactive({
  success_count: 0,
  skip_count: 0,
  error_count: 0,
  errors: []
})

const filters = reactive({
  search: '',
  category: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

const form = reactive({
  id: null,
  item_code: '',
  name: '',
  specification: '',
  model: '',
  attribute: '',
  brand: '',
  unit: '',
  unit_price: 0,
  quantity: 0,
  min_quantity: 10,
  max_quantity: 1000,
  category: '',
  location: '',
  supplier: '',
  image: '',
  remark: ''
})

const rules = {
  item_code: [{ required: true, message: '请输入物品编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入物品名称', trigger: 'blur' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }]
}

const inboundForm = reactive({
  item_id: null,
  quantity: 1,
  unit_price: 0,
  supplier: '',
  remark: ''
})

const outboundForm = reactive({
  item_id: null,
  quantity: 1,
  recipient: '',
  department: '',
  remark: ''
})

const inboundRules = {
  quantity: [{ required: true, message: '请输入入库数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入入库单价', trigger: 'blur' }]
}

const outboundRules = {
  quantity: [{ required: true, message: '请输入领取数量', trigger: 'blur' }],
  recipient: [{ required: true, message: '请输入领取人', trigger: 'blur' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看物品'
  return isEdit.value ? '编辑物品' : '新增物品'
})

const fetchItems = async () => {
  try {
    const res = await api.get('/items', {
      params: {
        ...filters,
        page: pagination.page,
        per_page: pagination.per_page,
        sort_by: 'name',
        sort_order: 'asc'
      }
    })
    items.value = res.items
    pagination.total = res.total
  } catch (error) {
    console.error(error)
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/items/categories')
    categories.value = res
  } catch (error) {
    console.error(error)
  }
}

const getQuantityClass = (row) => {
  if (row.quantity <= row.min_quantity) return 'alert-low'
  if (row.quantity >= row.max_quantity) return 'alert-high'
  return 'alert-normal'
}

const resetForm = () => {
  Object.assign(form, {
    id: null,
    item_code: '',
    name: '',
    specification: '',
    model: '',
    attribute: '',
    brand: '',
    unit: '',
    unit_price: 0,
    quantity: 0,
    min_quantity: 10,
    max_quantity: 1000,
    category: '',
    location: '',
    supplier: '',
    image: '',
    remark: ''
  })
}

const getImageUrl = (image) => {
  if (!image) return ''
  if (image.startsWith('http')) return image
  return `/api/items/images/${image}`
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (response) => {
  if (response.filename) {
    form.image = response.filename
    ElMessage.success('图片上传成功')
  }
}

const handleRemoveImage = () => {
  ElMessageBox.confirm('确定要删除这张图片吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    form.image = ''
    ElMessage.success('图片已删除')
  }).catch(() => {})
}

const handleCommand = (command, row) => {
  switch (command) {
    case 'outbound':
      handleOutbound(row)
      break
    case 'view':
      handleView(row)
      break
    case 'edit':
      handleEdit(row)
      break
    case 'delete':
      handleDelete(row)
      break
  }
}

const handleInbound = (row) => {
  currentItem.value = row
  inboundForm.item_id = row.id
  inboundForm.quantity = 1
  inboundForm.unit_price = row.unit_price
  inboundForm.supplier = row.supplier || ''
  inboundForm.remark = ''
  inboundDialogVisible.value = true
}

const handleOutbound = (row) => {
  if (row.quantity <= 0) {
    ElMessage.warning('该物品库存不足，无法领取')
    return
  }
  currentItem.value = row
  outboundForm.item_id = row.id
  outboundForm.quantity = 1
  outboundForm.recipient = ''
  outboundForm.department = ''
  outboundForm.remark = ''
  outboundDialogVisible.value = true
}

const submitInbound = async () => {
  if (!inboundFormRef.value) return
  
  await inboundFormRef.value.validate(async (valid) => {
    if (valid) {
      inboundLoading.value = true
      try {
        await api.post('/inbound', {
          item_id: inboundForm.item_id,
          quantity: inboundForm.quantity,
          unit_price: inboundForm.unit_price,
          supplier: inboundForm.supplier,
          remark: inboundForm.remark
        })
        ElMessage.success('入库成功')
        inboundDialogVisible.value = false
        fetchItems()
      } catch (error) {
        console.error(error)
      } finally {
        inboundLoading.value = false
      }
    }
  })
}

const submitOutbound = async () => {
  if (!outboundFormRef.value) return
  
  await outboundFormRef.value.validate(async (valid) => {
    if (valid) {
      outboundLoading.value = true
      try {
        await api.post('/outbound', {
          item_id: outboundForm.item_id,
          quantity: outboundForm.quantity,
          receiver: outboundForm.recipient,
          destination: outboundForm.department,
          remark: outboundForm.remark
        })
        ElMessage.success('领取成功')
        outboundDialogVisible.value = false
        fetchItems()
      } catch (error) {
        console.error(error)
      } finally {
        outboundLoading.value = false
      }
    }
  })
}

const handleAdd = () => {
  resetForm()
  isView.value = false
  isEdit.value = false
  dialogVisible.value = true
}

const handleView = (row) => {
  Object.assign(form, row)
  isView.value = true
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, row)
  isView.value = false
  isEdit.value = true
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除物品 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/items/${row.id}`)
      ElMessage.success('删除成功')
      fetchItems()
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
          await api.put(`/items/${form.id}`, form)
          ElMessage.success('更新成功')
        } else {
          await api.post('/items', form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchItems()
        fetchCategories()
      } catch (error) {
        console.error(error)
      }
    }
  })
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const downloadTemplate = async () => {
  try {
    const response = await fetch('/api/items/template', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error('下载失败')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '物品导入模板.xlsx'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error(error)
    ElMessage.error('下载模板失败')
  }
}

const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  importing.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const res = await fetch('/api/items/import', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    })
    
    const data = await res.json()
    
    if (res.ok) {
      importResult.success_count = data.success_count
      importResult.skip_count = data.skip_count
      importResult.error_count = data.error_count
      importResult.errors = data.errors || []
      
      importDialogVisible.value = false
      resultDialogVisible.value = true
      
      if (uploadRef.value) {
        uploadRef.value.clearFiles()
      }
      selectedFile.value = null
      
      fetchItems()
      fetchCategories()
    } else {
      ElMessage.error(data.message || '导入失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  fetchItems()
  fetchCategories()
})
</script>

<style scoped>
.items-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.page-desc {
  color: #6b7280;
  font-size: 14px;
  margin-top: 8px;
}

.filter-bar {
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.filter-bar :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-bar :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.filter-bar :deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

.table-container {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.table-container :deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

.table-container :deep(.el-table th.el-table__cell) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  color: #1a1a2e;
  font-weight: 600;
}

.table-container :deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: #fafbfc;
}

.table-container :deep(.el-table__row:hover > td.el-table__cell) {
  background: linear-gradient(90deg, #f0f5ff 0%, #e8f0ff 100%) !important;
}

.action-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.action-primary {
  height: 28px;
  padding: 0 14px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  color: #606266;
  transition: all 0.2s ease;
}

.action-primary:hover {
  background: #e8f4ff;
  border-color: #409eff;
  color: #409eff;
}

.action-primary:active {
  background: #d9ecff;
}

.action-secondary {
  height: 28px;
  padding: 0 14px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
  background: #fdf6ec;
  border: 1px solid #f5dab1;
  color: #e6a23c;
  transition: all 0.2s ease;
}

.action-secondary:hover {
  background: #fdf2e6;
  border-color: #e6a23c;
  color: #cf9236;
}

.action-secondary:active {
  background: #faecd8;
}

.action-more {
  width: 28px;
  height: 28px;
  padding: 0;
  border-radius: 6px;
  background: transparent;
  border: 1px solid #e4e7ed;
  color: #909399;
  transition: all 0.2s ease;
}

.action-more:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
  color: #606266;
}

.action-more:active {
  background: #e4e7ed;
}

.action-dropdown-menu {
  min-width: 120px;
  padding: 4px 0;
}

.action-dropdown-menu :deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 13px;
  color: #606266;
}

.action-dropdown-menu :deep(.el-dropdown-menu__item:hover) {
  background: #f5f7fa;
  color: #409eff;
}

.action-dropdown-menu :deep(.el-dropdown-menu__item .el-icon) {
  font-size: 14px;
}

.action-dropdown-menu :deep(.el-dropdown-menu__item.is-divided) {
  border-top: 1px solid #ebeef5;
  margin-top: 4px;
  padding-top: 12px;
}

.delete-icon,
.delete-text {
  color: #f56c6c;
}

.action-dropdown-menu :deep(.el-dropdown-menu__item:hover .delete-icon),
.action-dropdown-menu :deep(.el-dropdown-menu__item:hover .delete-text) {
  color: #f78989;
}

.alert-low {
  color: #ef4444;
  font-weight: 600;
}

.alert-high {
  color: #f59e0b;
  font-weight: 600;
}

.alert-normal {
  color: #10b981;
  font-weight: 500;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-title {
    font-size: 20px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .table-container :deep(.el-table) {
    font-size: 12px;
  }
  
  .table-container :deep(.el-table th) {
    font-size: 11px;
    padding: 8px 0;
  }
  
  .table-container :deep(.el-table td) {
    padding: 8px 0;
  }
  
  .action-cell {
    flex-wrap: wrap;
    gap: 6px;
  }
  
  .action-primary,
  .action-secondary {
    padding: 0 10px;
    font-size: 11px;
  }
  
  .action-more {
    width: 26px;
    height: 26px;
  }
  
  .pagination-container {
    justify-content: center;
  }
  
  .pagination-container :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  :deep(.el-dialog) {
    width: 95% !important;
    max-width: 500px;
    margin: 5vh auto !important;
  }
  
  :deep(.el-dialog__body) {
    padding: 16px;
    max-height: 70vh;
    overflow-y: auto;
  }
  
  :deep(.el-form-item__label) {
    font-size: 13px;
  }
  
  :deep(.el-input__inner) {
    font-size: 14px;
  }
  
  .image-uploader {
    width: 80px;
    height: 80px;
  }
  
  .image-uploader-icon {
    width: 80px;
    height: 80px;
  }
  
  .image-preview {
    width: 80px;
    height: 80px;
  }
}

:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  padding: 20px 24px;
  margin: 0;
}

:deep(.el-dialog__title) {
  font-weight: 600;
  color: #1a1a2e;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-upload-dragger) {
  border-radius: 12px;
  border: 2px dashed #e5e7eb;
  transition: all 0.3s;
}

:deep(.el-upload-dragger:hover) {
  border-color: #667eea;
  background: #f8fafc;
}

:deep(.el-icon--upload) {
  font-size: 48px;
  color: #667eea;
}

:deep(.el-upload__text) {
  color: #6b7280;
}

:deep(.el-upload__text em) {
  color: #667eea;
}

.image-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-uploader:hover {
  border-color: #667eea;
}

.image-upload-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.upload-icon {
  font-size: 32px;
  color: #8c939d;
}

.upload-text {
  font-size: 12px;
  color: #8c939d;
  margin-top: 8px;
}

.image-actions {
  margin-top: 8px;
}

.image-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview {
  width: 120px;
  height: 120px;
  display: block;
  object-fit: cover;
}

.table-image {
  width: 50px;
  height: 50px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.table-image:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.image-placeholder-loading,
.image-placeholder-error {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 6px;
  color: #94a3b8;
}

.no-image {
  color: #ccc;
  font-size: 12px;
}

@media (max-width: 768px) {
  .page-container {
    padding: 0;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .header-actions .el-button {
    flex: 1;
    min-width: 80px;
  }
  
  .search-bar {
    flex-direction: column;
    gap: 8px;
  }
  
  .search-bar :deep(.el-input),
  .search-bar :deep(.el-select) {
    width: 100% !important;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .table-container :deep(.el-table) {
    min-width: 800px;
  }
  
  .table-container :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }
  
  .pagination-container {
    justify-content: center;
  }
  
  .pagination-container :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 5vh auto !important;
  }
  
  :deep(.el-dialog__body) {
    padding: 16px;
    max-height: 70vh;
    overflow-y: auto;
  }
  
  :deep(.el-form-item__label) {
    float: none;
    text-align: left;
    margin-bottom: 8px;
  }
  
  :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }
  
  .image-upload-wrapper {
    width: 100%;
  }
  
  .image-uploader {
    width: 100px;
    height: 100px;
  }
}

.item-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}

.item-code {
  font-size: 13px;
  color: #6b7280;
}

.current-stock {
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
}
</style>
