<template>
  <div class="receiver-page">
    <div class="page-header">
      <h1 class="page-title">我的领取记录</h1>
      <p class="page-subtitle">查看您的物品领取历史</p>
    </div>
    
    <div class="records-container" v-loading="loading">
      <div v-if="records.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无领取记录">
          <el-button type="primary" @click="$router.push('/receiver')">去领取物品</el-button>
        </el-empty>
      </div>
      
      <div v-else class="records-list">
        <div v-for="record in records" :key="record.id" class="record-card">
          <div class="record-header">
            <div class="record-info">
              <h3 class="record-item-name">{{ record.item_name }}</h3>
              <span class="record-time">{{ formatTime(record.created_at) }}</span>
            </div>
            <el-tag :type="getStatusType(record.status)" size="small">
              {{ getStatusText(record.status) }}
            </el-tag>
          </div>
          <div class="record-details">
            <div class="detail-item">
              <span class="detail-label">领取数量</span>
              <span class="detail-value">{{ record.quantity }} {{ record.item_unit || '件' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">单号</span>
              <span class="detail-value mono">{{ record.record_no }}</span>
            </div>
            <div class="detail-item" v-if="record.purpose">
              <span class="detail-label">用途</span>
              <span class="detail-value">{{ record.purpose }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="pagination-wrapper" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="fetchRecords"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const loading = ref(false)
const records = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusType = (status) => {
  const statusMap = {
    completed: 'success',
    pending: 'warning',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    completed: '已完成',
    pending: '待处理',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const fetchRecords = async () => {
  loading.value = true
  try {
    const res = await api.get('/receiver/records', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value
      }
    })
    records.value = res.records
    total.value = res.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.receiver-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.records-container {
  min-height: 300px;
}

.empty-state {
  padding: 60px 0;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.record-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-radius: 14px;
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 20px;
  transition: all 0.2s ease;
}

.record-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.record-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.record-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.record-item-name {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.record-time {
  font-size: 13px;
  color: #94a3b8;
}

.record-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(226, 232, 240, 0.3);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #94a3b8;
}

.detail-value {
  font-size: 14px;
  color: #0f172a;
  font-weight: 500;
}

.detail-value.mono {
  font-family: monospace;
  font-size: 13px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .record-details {
    grid-template-columns: 1fr;
  }
}
</style>
