<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">入库管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd" v-if="authStore.hasAnyRole(['admin', 'operator'])">
          <el-icon><Plus /></el-icon>
          新增入库
        </el-button>
        <el-button type="success" @click="importDialogVisible = true" v-if="authStore.hasAnyRole(['admin', 'operator'])">
          <el-icon><Upload /></el-icon>
          一键入库
        </el-button>
        <el-button type="info" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>
    
    <div class="filter-bar">
      <el-input
        v-model="filters.search"
        placeholder="搜索单号、物品编码、物品名称"
        clearable
        class="filter-item"
        @keyup.enter="fetchRecords"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="filters.inbound_type"
        placeholder="入库类型"
        clearable
        class="filter-item"
        @change="fetchRecords"
      >
        <el-option label="采购入库" value="purchase" />
        <el-option label="退货入库" value="return" />
        <el-option label="调拨入库" value="transfer" />
        <el-option label="其他入库" value="other" />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
        @change="handleDateChange"
        class="filter-item date-picker"
      />
      <el-button type="primary" @click="fetchRecords">查询</el-button>
    </div>
    
    <div class="table-wrapper">
      <el-table :data="records" stripe style="min-width: 900px" v-loading="loading">
        <el-table-column prop="record_no" label="入库单号" width="160" />
        <el-table-column prop="item_code" label="物品编码" width="120" />
        <el-table-column prop="item_name" label="物品名称" width="150" />
        <el-table-column prop="inbound_type" label="入库类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ inboundTypes[row.inbound_type] || row.inbound_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">¥{{ row.unit_price?.toFixed(2) || '0.00' }}</template>
        </el-table-column>
        <el-table-column prop="total_price" label="总价" width="120">
          <template #default="{ row }">¥{{ row.total_price?.toFixed(2) || '0.00' }}</template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column prop="handler" label="经手人" width="100" />
        <el-table-column prop="created_at" label="入库时间" width="160">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row)" v-if="authStore.hasAnyRole(['admin', 'operator'])">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)" v-if="authStore.hasRole('admin')">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        :small="isMobile"
        @current-change="fetchRecords"
        @size-change="fetchRecords"
      />
    </div>
    
    <el-dialog v-model="importDialogVisible" title="一键入库" width="500px">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".xlsx,.xls,.csv"
        :limit="1"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">支持 Excel 或 CSV 文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit" :loading="importLoading">确认导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, Search, UploadFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()
const loading = ref(false)
const records = ref([])
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})
const dateRange = ref([])
const filters = reactive({
  search: '',
  inbound_type: '',
  start_date: '',
  end_date: ''
})
const importDialogVisible = ref(false)
const importLoading = ref(false)
const importFile = ref(null)

const isMobile = computed(() => window.innerWidth <= 768)

const inboundTypes = {
  purchase: '采购入库',
  return: '退货入库',
  transfer: '调拨入库',
  other: '其他入库'
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const res = await api.get('/inbound', {
      params: {
        page: pagination.page,
        per_page: pagination.per_page,
        search: filters.search,
        inbound_type: filters.inbound_type,
        start_date: filters.start_date,
        end_date: filters.end_date
      }
    })
    records.value = res.records
    pagination.total = res.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
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

const handleAdd = () => {
  ElMessage.info('新增入库功能开发中')
}

const handleExport = async () => {
  try {
    const params = new URLSearchParams({
      search: filters.search,
      inbound_type: filters.inbound_type,
      start_date: filters.start_date,
      end_date: filters.end_date
    })
    
    const response = await fetch(`/api/inbound/export?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) throw new Error('导出失败')
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `入库记录_${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const handleImportSubmit = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  
  importLoading.value = true
  const formData = new FormData()
  formData.append('file', importFile.value)
  
  try {
    const res = await api.post('/inbound/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success(`成功导入 ${res.success_count} 条记录`)
    importDialogVisible.value = false
    importFile.value = null
    fetchRecords()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '导入失败')
  } finally {
    importLoading.value = false
  }
}

const handleView = (row) => {
  ElMessage.info(`查看详情: ${row.record_no}`)
}

const handleEdit = (row) => {
  ElMessage.info(`编辑: ${row.record_no}`)
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条入库记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('删除成功')
    fetchRecords()
  }).catch(() => {})
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.filter-item {
  width: 180px;
}

.date-picker {
  width: 260px;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  background: white;
  border-radius: 12px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
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
  
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-bar > * {
    width: 100% !important;
  }
  
  .filter-item,
  .date-picker {
    width: 100%;
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
}
</style>
