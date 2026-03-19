<template>
  <div>
    <div class="page-header">
      <h2>出库管理</h2>
    </div>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filters">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="单号/物品编码/名称" clearable @keyup.enter="fetchRecords" />
        </el-form-item>
        <el-form-item label="出库类型">
          <el-select v-model="filters.outbound_type" placeholder="全部" clearable>
            <el-option v-for="(label, value) in outboundTypes" :key="value" :label="label" :value="value" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item label="领取人">
          <el-input v-model="filters.receiver" placeholder="请输入领取人" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchRecords">查询</el-button>
          <el-button type="success" @click="handleAdd" v-if="authStore.hasAnyRole(['admin', 'operator'])">新增出库</el-button>
          <el-button type="warning" @click="importDialogVisible = true" v-if="authStore.hasAnyRole(['admin', 'operator'])">
            <el-icon><Upload /></el-icon>
            一键预领
          </el-button>
          <el-button type="info" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="records" stripe>
        <el-table-column prop="record_no" label="出库单号" width="180" />
        <el-table-column prop="item_code" label="物品编码" width="120" />
        <el-table-column prop="item_name" label="物品名称" width="150" />
        <el-table-column prop="outbound_type" label="出库类型" width="120">
          <template #default="{ row }">
            <el-tag type="warning">{{ outboundTypes[row.outbound_type] || row.outbound_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">¥{{ row.unit_price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_price" label="总价" width="120">
          <template #default="{ row }">¥{{ row.total_price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="destination" label="去向" width="120" />
        <el-table-column prop="receiver" label="领取人" width="100" />
        <el-table-column prop="handler" label="经手人" width="100" />
        <el-table-column prop="created_at" label="出库时间" width="180" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
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
          @size-change="fetchRecords"
          @current-change="fetchRecords"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" :disabled="isView">
        <el-form-item label="物品" prop="item_id" v-if="!isView">
          <el-select v-model="form.item_id" placeholder="请选择物品" filterable style="width: 100%" @change="handleItemChange">
            <el-option v-for="item in itemList" :key="item.id" :label="`${item.item_code} - ${item.name} (库存: ${item.quantity})`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="物品信息" v-if="isView">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="物品编码">{{ form.item_code }}</el-descriptions-item>
            <el-descriptions-item label="物品名称">{{ form.item_name }}</el-descriptions-item>
          </el-descriptions>
        </el-form-item>
        <el-form-item label="出库类型" prop="outbound_type">
          <el-select v-model="form.outbound_type" placeholder="请选择出库类型" style="width: 100%">
            <el-option v-for="(label, value) in outboundTypes" :key="value" :label="label" :value="value" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="form.quantity" :min="1" :max="maxQuantity" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="去向" prop="destination">
          <el-input v-model="form.destination" placeholder="请输入去向" />
        </el-form-item>
        <el-form-item label="领用人" prop="receiver">
          <el-input v-model="form.receiver" placeholder="请输入领用人" />
        </el-form-item>
        <el-form-item label="经手人" prop="handler">
          <el-input v-model="form.handler" placeholder="请输入经手人" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer v-if="!isView">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定出库</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" title="一键预领" width="500px">
      <el-alert title="导入说明" type="info" :closable="false" style="margin-bottom: 20px">
        <template #default>
          <p>1. 支持 Excel (.xlsx, .xls) 和 CSV 格式文件</p>
          <p>2. 系统会自动识别列名，无需严格按照模板格式</p>
          <p>3. 物品编码或物品名称至少填写一个</p>
          <p>4. 库存不足的物品将被跳过</p>
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
            <p v-if="importResult.insufficient_count > 0">
              库存不足: <span style="color: #f56c6c; font-weight: bold">{{ importResult.insufficient_count }}</span> 条
            </p>
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
          <div v-if="importResult.insufficient_stock && importResult.insufficient_stock.length > 0" style="text-align: left; max-height: 200px; overflow-y: auto; margin-top: 10px">
            <el-alert
              v-for="(item, index) in importResult.insufficient_stock"
              :key="index"
              :title="`第${item.row}行: ${item.item} 库存不足，需${item.requested}，现有${item.available}`"
              type="warning"
              :closable="false"
            />
          </div>
        </template>
      </el-result>
      <template #footer>
        <el-button type="primary" @click="resultDialogVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()

const records = ref([])
const itemList = ref([])
const outboundTypes = ref({})
const dialogVisible = ref(false)
const isView = ref(false)
const formRef = ref()
const dateRange = ref([])
const maxQuantity = ref(999999)
const importDialogVisible = ref(false)
const resultDialogVisible = ref(false)
const importing = ref(false)
const uploadRef = ref()
const selectedFile = ref(null)

const importResult = reactive({
  success_count: 0,
  insufficient_count: 0,
  error_count: 0,
  errors: [],
  insufficient_stock: []
})

const filters = reactive({
  search: '',
  outbound_type: '',
  start_date: '',
  end_date: '',
  receiver: ''
})

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

const form = reactive({
  item_id: null,
  item_code: '',
  item_name: '',
  outbound_type: '',
  quantity: 1,
  unit_price: 0,
  destination: '',
  receiver: '',
  handler: '',
  remark: ''
})

const rules = {
  item_id: [{ required: true, message: '请选择物品', trigger: 'change' }],
  outbound_type: [{ required: true, message: '请选择出库类型', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  receiver: [{ required: true, message: '请输入领用人', trigger: 'blur' }],
  handler: [{ required: true, message: '请输入经手人', trigger: 'blur' }]
}

const dialogTitle = computed(() => isView.value ? '查看出库记录' : '新增出库')

const fetchRecords = async () => {
  try {
    const res = await api.get('/outbound', {
      params: {
        page: pagination.page,
        per_page: pagination.per_page,
        ...filters
      }
    })
    records.value = res.records
    pagination.total = res.total
  } catch (error) {
    console.error(error)
  }
}

const fetchOutboundTypes = async () => {
  try {
    const res = await api.get('/outbound/types')
    outboundTypes.value = res
  } catch (error) {
    console.error(error)
  }
}

const fetchItemList = async () => {
  try {
    const res = await api.get('/items', { params: { per_page: 1000, status: 'true' } })
    itemList.value = res.items
  } catch (error) {
    console.error(error)
  }
}

const handleDateChange = (val) => {
  if (val) {
    filters.start_date = val[0]
    filters.end_date = val[1]
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
}

const handleItemChange = (itemId) => {
  const item = itemList.value.find(i => i.id === itemId)
  if (item) {
    form.item_code = item.item_code
    form.item_name = item.name
    form.unit_price = item.unit_price
    maxQuantity.value = item.quantity
  }
}

const resetForm = () => {
  Object.assign(form, {
    item_id: null,
    item_code: '',
    item_name: '',
    outbound_type: '',
    quantity: 1,
    unit_price: 0,
    destination: '',
    receiver: '',
    handler: '',
    remark: ''
  })
}

const handleAdd = () => {
  resetForm()
  isView.value = false
  dialogVisible.value = true
}

const handleView = (row) => {
  Object.assign(form, row)
  isView.value = true
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await api.post('/outbound', form)
        ElMessage.success('出库成功')
        dialogVisible.value = false
        fetchRecords()
        fetchItemList()
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
    const response = await fetch('/api/outbound/template', {
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
    a.download = '批量出库模板.xlsx'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error(error)
    ElMessage.error('下载模板失败')
  }
}

const handleExport = async () => {
  try {
    const params = new URLSearchParams({
      search: filters.search,
      outbound_type: filters.outbound_type,
      start_date: filters.start_date,
      end_date: filters.end_date,
      receiver: filters.receiver
    })
    
    const response = await fetch(`/api/outbound/export?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error('导出失败')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '出库记录.xlsx'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error(error)
    ElMessage.error('导出失败')
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
    
    const res = await fetch('/api/outbound/import', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    })
    
    const data = await res.json()
    
    if (res.ok) {
      importResult.success_count = data.success_count
      importResult.insufficient_count = data.insufficient_count
      importResult.error_count = data.error_count
      importResult.errors = data.errors || []
      importResult.insufficient_stock = data.insufficient_stock || []
      
      importDialogVisible.value = false
      resultDialogVisible.value = true
      
      if (uploadRef.value) {
        uploadRef.value.clearFiles()
      }
      selectedFile.value = null
      
      fetchRecords()
      fetchItemList()
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
  fetchRecords()
  fetchOutboundTypes()
  fetchItemList()
})
</script>
