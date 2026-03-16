<template>
  <div>
    <div class="page-header">
      <h2>库存查询</h2>
    </div>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filters">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="编码/名称" clearable @keyup.enter="fetchInventory" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.category" placeholder="全部" clearable>
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="预警状态">
          <el-select v-model="filters.alert_status" placeholder="全部" clearable>
            <el-option label="库存不足" value="low" />
            <el-option label="库存过剩" value="high" />
            <el-option label="正常" value="normal" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchInventory">查询</el-button>
          <el-button @click="handleExport">导出</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card>
          <el-statistic title="物品总数" :value="summary.total_items" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="库存总量" :value="summary.total_quantity" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="库存总值" :value="summary.total_value" prefix="¥" :precision="2" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <el-statistic title="预警数量" :value="summary.pending_alerts" />
        </el-card>
      </el-col>
    </el-row>

    <div class="table-container">
      <el-table :data="inventory" stripe>
        <el-table-column prop="item_code" label="物品编码" width="120" />
        <el-table-column prop="name" label="物品名称" width="150" />
        <el-table-column prop="specification" label="规格" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="quantity" label="库存数量" width="120">
          <template #default="{ row }">
            <span :class="getAlertClass(row.alert_level)">{{ row.quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="min_quantity" label="库存下限" width="100" />
        <el-table-column prop="max_quantity" label="库存上限" width="100" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">¥{{ row.unit_price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="库存价值" width="120">
          <template #default="{ row }">¥{{ (row.quantity * row.unit_price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="location" label="存放位置" width="150" />
        <el-table-column label="预警状态" width="100" fixed="right">
          <template #default="{ row }">
            <el-tag :type="getAlertType(row.alert_level)">
              {{ getAlertText(row.alert_level) }}
            </el-tag>
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
          @size-change="fetchInventory"
          @current-change="fetchInventory"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const inventory = ref([])
const categories = ref([])
const summary = ref({
  total_items: 0,
  total_quantity: 0,
  total_value: 0,
  pending_alerts: 0
})

const filters = reactive({
  search: '',
  category: '',
  alert_status: ''
})

const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

const fetchInventory = async () => {
  try {
    const res = await api.get('/inventory', {
      params: {
        page: pagination.page,
        per_page: pagination.per_page,
        ...filters
      }
    })
    inventory.value = res.inventory
    pagination.total = res.total
  } catch (error) {
    console.error(error)
  }
}

const fetchSummary = async () => {
  try {
    const res = await api.get('/inventory/summary')
    summary.value = res
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

const getAlertClass = (level) => {
  switch (level) {
    case 'low': return 'alert-low'
    case 'high': return 'alert-high'
    default: return 'alert-normal'
  }
}

const getAlertType = (level) => {
  switch (level) {
    case 'low': return 'danger'
    case 'high': return 'warning'
    default: return 'success'
  }
}

const getAlertText = (level) => {
  switch (level) {
    case 'low': return '库存不足'
    case 'high': return '库存过剩'
    default: return '正常'
  }
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

onMounted(() => {
  fetchInventory()
  fetchSummary()
  fetchCategories()
})
</script>
