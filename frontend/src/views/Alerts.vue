<template>
  <div>
    <div class="page-header">
      <h2>库存预警</h2>
    </div>
    
    <div class="filter-bar">
      <el-form :inline="true">
        <el-form-item label="预警状态">
          <el-select v-model="status" placeholder="全部" @change="fetchAlerts">
            <el-option label="待处理" value="pending" />
            <el-option label="已处理" value="resolved" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchAlerts">查询</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="alerts" stripe>
        <el-table-column prop="item_code" label="物品编码" width="120" />
        <el-table-column prop="item_name" label="物品名称" width="150" />
        <el-table-column prop="alert_type" label="预警类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.alert_type === 'low' ? 'danger' : 'warning'">
              {{ row.alert_type === 'low' ? '库存不足' : '库存过剩' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_quantity" label="当前库存" width="120">
          <template #default="{ row }">
            <span :class="row.alert_type === 'low' ? 'alert-low' : 'alert-high'">
              {{ row.current_quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="预警阈值" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : 'success'">
              {{ row.status === 'pending' ? '待处理' : '已处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="预警时间" width="180" />
        <el-table-column prop="resolved_at" label="处理时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              link 
              type="primary" 
              @click="handleResolve(row)"
              v-if="row.status === 'pending' && authStore.hasAnyRole(['admin', 'operator'])"
            >
              标记已处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()
const alerts = ref([])
const status = ref('pending')

const fetchAlerts = async () => {
  try {
    const res = await api.get('/inventory/alerts', {
      params: { status: status.value }
    })
    alerts.value = res.alerts
  } catch (error) {
    console.error(error)
  }
}

const handleResolve = async (row) => {
  try {
    await api.post(`/inventory/alerts/${row.id}/resolve`)
    ElMessage.success('已标记为处理')
    fetchAlerts()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  fetchAlerts()
})
</script>
