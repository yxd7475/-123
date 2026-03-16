<template>
  <div>
    <div class="page-header">
      <h2>操作日志</h2>
    </div>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filters">
        <el-form-item label="模块">
          <el-select v-model="filters.module" placeholder="全部" clearable>
            <el-option label="认证" value="认证" />
            <el-option label="物品管理" value="物品管理" />
            <el-option label="入库管理" value="入库管理" />
            <el-option label="出库管理" value="出库管理" />
            <el-option label="用户管理" value="用户管理" />
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
        <el-form-item>
          <el-button type="primary" @click="fetchLogs">查询</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="logs" stripe>
        <el-table-column prop="username" label="操作用户" width="120" />
        <el-table-column prop="operation" label="操作类型" width="120" />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="created_at" label="操作时间" width="180" />
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchLogs"
          @current-change="fetchLogs"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/utils/api'

const logs = ref([])
const dateRange = ref([])

const filters = reactive({
  module: '',
  start_date: '',
  end_date: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const fetchLogs = async () => {
  try {
    const res = await api.get('/users/logs', {
      params: {
        page: pagination.page,
        per_page: pagination.per_page,
        ...filters
      }
    })
    logs.value = res.logs
    pagination.total = res.total
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

onMounted(() => {
  fetchLogs()
})
</script>
