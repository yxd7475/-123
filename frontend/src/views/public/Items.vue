<template>
  <div class="public-page">
    <div class="page-header">
      <h1 class="page-title">可领物品</h1>
      <p class="page-subtitle">选择您需要领取的物品</p>
    </div>
    
    <div class="search-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索物品名称、规格..."
        size="large"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="selectedCategory"
        placeholder="选择分类"
        size="large"
        clearable
        @change="handleSearch"
        style="width: 160px"
      >
        <el-option
          v-for="cat in categories"
          :key="cat"
          :label="cat"
          :value="cat"
        />
      </el-select>
    </div>
    
    <div class="items-grid" v-loading="loading">
      <div
        v-for="item in items"
        :key="item.id"
        class="item-card"
      >
        <div class="item-image-wrapper">
          <el-image 
            v-if="item.image" 
            :src="getImageUrl(item.image)" 
            :preview-src-list="[getImageUrl(item.image)]"
            :initial-index="0"
            fit="cover"
            class="item-image"
            lazy
            :preview-teleported="true"
          >
            <template #placeholder>
              <div class="image-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
              </div>
            </template>
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <div v-else class="image-placeholder">
            <el-icon :size="32"><Box /></el-icon>
          </div>
        </div>
        <div class="item-content">
          <h3 class="item-name">{{ item.name }}</h3>
          <p class="item-spec">{{ item.specification || '无规格' }}</p>
          <div class="item-meta">
            <span class="item-unit">{{ item.unit }}</span>
            <span class="item-stock" :class="{ low: item.quantity <= item.min_quantity }">
              库存: {{ item.quantity }}
            </span>
          </div>
          <div class="item-actions">
            <el-tag v-if="item.quantity <= 0" type="danger" size="small">不可领</el-tag>
            <el-tag v-else-if="item.quantity <= item.min_quantity" type="warning" size="small">库存不足</el-tag>
            <el-tag v-else type="success" size="small">可领取</el-tag>
            <el-button 
              v-if="item.quantity > 0"
              type="primary" 
              size="small"
              @click="openReceiveDialog(item)"
            >
              领取
            </el-button>
          </div>
        </div>
      </div>
      
      <el-empty v-if="!loading && items.length === 0" description="暂无可领取物品" />
    </div>
    
    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchItems"
      />
    </div>
    
    <el-dialog
      v-model="receiveDialogVisible"
      title="领取物品"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="receive-item-info" v-if="currentItem">
        <div class="receive-item-header">
          <h3>{{ currentItem.name }}</h3>
          <el-tag type="success" size="small">库存: {{ currentItem.quantity }}</el-tag>
        </div>
        <p class="receive-item-spec">{{ currentItem.specification || '无规格' }}</p>
        <el-divider />
        <el-form :model="receiveForm" label-position="top">
          <el-form-item label="领取人姓名" required>
            <el-input v-model="receiveForm.receiver_name" placeholder="请输入您的姓名" />
          </el-form-item>
          <el-form-item label="领取数量" required>
            <el-input-number
              v-model="receiveForm.quantity"
              :min="1"
              :max="currentItem.quantity"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="联系电话">
            <el-input v-model="receiveForm.phone" placeholder="请输入联系电话（选填）" />
          </el-form-item>
          <el-form-item label="领取用途">
            <el-input
              v-model="receiveForm.purpose"
              type="textarea"
              :rows="2"
              placeholder="请输入领取用途（选填）"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="receiveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReceive" :loading="receiveLoading">
          确认领取
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Box, Loading, Picture } from '@element-plus/icons-vue'
import api from '@/utils/api'

const loading = ref(false)
const items = ref([])
const categories = ref([])
const searchText = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const receiveDialogVisible = ref(false)
const receiveLoading = ref(false)
const currentItem = ref(null)
const receiveForm = reactive({
  receiver_name: '',
  quantity: 1,
  phone: '',
  purpose: ''
})

const getImageUrl = (image) => {
  if (!image) return ''
  if (image.startsWith('http')) return image
  return `/api/items/images/${image}`
}

const fetchItems = async () => {
  loading.value = true
  try {
    const res = await api.get('/public/items', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value,
        search: searchText.value,
        category: selectedCategory.value
      }
    })
    items.value = res.items
    total.value = res.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/public/categories')
    categories.value = res.categories
  } catch (error) {
    console.error(error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchItems()
}

const openReceiveDialog = (item) => {
  if (item.quantity <= 0) {
    ElMessage.warning('该物品库存不足，无法领取')
    return
  }
  currentItem.value = item
  receiveForm.receiver_name = ''
  receiveForm.quantity = 1
  receiveForm.phone = ''
  receiveForm.purpose = ''
  receiveDialogVisible.value = true
}

const submitReceive = async () => {
  if (!currentItem.value) return
  if (!receiveForm.receiver_name.trim()) {
    ElMessage.warning('请输入领取人姓名')
    return
  }
  if (receiveForm.quantity < 1) {
    ElMessage.warning('请输入有效的领取数量')
    return
  }
  if (receiveForm.quantity > currentItem.value.quantity) {
    ElMessage.warning('领取数量不能超过库存数量')
    return
  }
  
  receiveLoading.value = true
  try {
    await api.post('/public/receive', {
      item_id: currentItem.value.id,
      quantity: receiveForm.quantity,
      receiver_name: receiveForm.receiver_name,
      phone: receiveForm.phone,
      purpose: receiveForm.purpose
    })
    ElMessage.success('领取成功')
    receiveDialogVisible.value = false
    fetchItems()
  } catch (error) {
    console.error(error)
  } finally {
    receiveLoading.value = false
  }
}

onMounted(() => {
  fetchItems()
  fetchCategories()
})
</script>

<style scoped>
.public-page {
  max-width: 1200px;
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

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.item-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-radius: 14px;
  border: 1px solid rgba(226, 232, 240, 0.5);
  overflow: hidden;
  transition: all 0.25s ease;
}

.item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.item-image-wrapper {
  height: 180px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  position: relative;
  overflow: hidden;
}

.item-image {
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.image-loading,
.image-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #94a3b8;
  font-size: 24px;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.item-content {
  padding: 16px;
}

.item-name {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-spec {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 12px 0;
}

.item-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.item-unit {
  font-size: 12px;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 4px;
}

.item-stock {
  font-size: 13px;
  font-weight: 500;
  color: #10b981;
}

.item-stock.low {
  color: #ef4444;
}

.item-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.receive-item-info {
  padding: 4px 0;
}

.receive-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.receive-item-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.receive-item-spec {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

@media (max-width: 768px) {
  .items-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .search-bar .el-select {
    width: 100% !important;
  }
}
</style>
