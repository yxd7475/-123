<template>
  <div class="public-page">
    <div class="page-header">
      <h1 class="page-title">领取记录查询</h1>
      <p class="page-subtitle">输入领取人姓名查询领取记录</p>
    </div>
    
    <div class="search-section">
      <el-input
        v-model="searchName"
        placeholder="请输入领取人姓名"
        size="large"
        clearable
        @keyup.enter="searchRecords"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" size="large" @click="searchRecords" :loading="loading">
        查询
      </el-button>
    </div>
    
    <div class="records-container" v-loading="loading">
      <div v-if="!searched" class="empty-hint">
        <el-icon :size="48"><Search /></el-icon>
        <p>请输入领取人姓名查询记录</p>
      </div>
      
      <div v-else-if="records.length === 0" class="empty-state">
        <el-empty description="未找到相关领取记录" />
      </div>
      
      <div v-else class="records-list">
        <div v-for="record in records" :key="record.id" class="record-card">
          <div class="record-header">
            <div class="record-info">
              <h3 class="record-item-name">{{ record.item_name }}</h3>
              <span class="record-time">{{ formatTime(record.created_at) }}</span>
            </div>
            <el-tag type="success" size="small">已领取</el-tag>
          </div>
          <div class="record-details">
            <div class="detail-item">
              <span class="detail-label">领取数量</span>
              <span class="detail-value">{{ record.quantity }} 件</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">单号</span>
              <span class="detail-value mono">{{ record.record_no }}</span>
            </div>
            <div class="detail-item" v-if="record.phone">
              <span class="detail-label">联系电话</span>
              <span class="detail-value">{{ record.phone }}</span>
            </div>
            <div class="detail-item" v-if="record.purpose">
              <span class="detail-label">用途</span>
              <span class="detail-value">{{ record.purpose }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

const route = useRoute()
const loading = ref(false)
const searched = ref(false)
const searchName = ref('')
const records = ref([])

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

const searchRecords = async () => {
  if (!searchName.value.trim()) {
    return
  }
  
  loading.value = true
  searched.value = true
  try {
    const res = await api.get('/public/records', {
      params: {
        receiver_name: searchName.value.trim()
      }
    })
    records.value = res.records
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (route.query.name) {
    searchName.value = route.query.name
    searchRecords()
  }
})
</script>

<style scoped>
.public-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px;
}

.page-header {
  margin-bottom: 16px;
  padding-top: 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

.search-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.search-section .el-button {
  width: 100%;
}

.records-container {
  min-height: 300px;
}

.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #94a3b8;
}

.empty-hint p {
  margin-top: 16px;
  font-size: 14px;
}

.empty-state {
  padding: 40px 0;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 16px;
  transition: all 0.2s ease;
}

.record-card:active {
  transform: scale(0.98);
}

.record-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
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
  font-size: 12px;
  color: #94a3b8;
}

.record-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(226, 232, 240, 0.3);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 11px;
  color: #94a3b8;
}

.detail-value {
  font-size: 13px;
  color: #0f172a;
  font-weight: 500;
}

.detail-value.mono {
  font-family: monospace;
  font-size: 12px;
}

@media (min-width: 768px) {
  .public-page {
    padding: 0 24px;
  }
  
  .page-header {
    margin-bottom: 24px;
    padding-top: 0;
  }
  
  .page-title {
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  .page-subtitle {
    font-size: 14px;
  }
  
  .search-section {
    flex-direction: row;
    gap: 12px;
  }
  
  .search-section .el-button {
    width: auto;
  }
  
  .records-list {
    gap: 16px;
  }
  
  .record-card {
    padding: 20px;
  }
  
  .record-details {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
  }
}
</style>
