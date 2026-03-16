<template>
  <div class="receiver-layout">
    <header class="receiver-header">
      <div class="header-content">
        <div class="logo">
          <div class="logo-icon">
            <el-icon><Box /></el-icon>
          </div>
          <span class="logo-text">物品领用系统</span>
        </div>
        <div class="user-section">
          <div class="user-info">
            <el-avatar :size="36" class="user-avatar">
              {{ authStore.user?.real_name?.charAt(0) }}
            </el-avatar>
            <div class="user-detail">
              <span class="user-name">{{ authStore.user?.real_name }}</span>
              <span class="user-role">领取人</span>
            </div>
          </div>
          <el-button text @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出
          </el-button>
        </div>
      </div>
    </header>
    
    <nav class="receiver-nav">
      <div class="nav-content">
        <router-link to="/receiver" class="nav-item" :class="{ active: $route.path === '/receiver' }">
          <el-icon><Goods /></el-icon>
          <span>可领物品</span>
        </router-link>
        <router-link to="/receiver/records" class="nav-item" :class="{ active: $route.path === '/receiver/records' }">
          <el-icon><List /></el-icon>
          <span>我的领取记录</span>
        </router-link>
      </div>
    </nav>
    
    <main class="receiver-main">
      <router-view v-slot="{ Component }">
        <transition name="fade-transform" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Box, Goods, List, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      console.error(error)
    }
    authStore.clearAuth()
    router.push('/login')
    ElMessage.success('已退出登录')
  }).catch(() => {})
}
</script>

<style scoped>
.receiver-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
}

.receiver-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  font-weight: 600;
}

.user-detail {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #0f172a;
}

.user-role {
  font-size: 12px;
  color: #94a3b8;
}

.receiver-nav {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px) saturate(180%);
  -webkit-backdrop-filter: blur(8px) saturate(180%);
  border-bottom: 1px solid rgba(226, 232, 240, 0.3);
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.nav-item:hover {
  color: #6366f1;
}

.nav-item.active {
  color: #6366f1;
  border-bottom-color: #6366f1;
}

.receiver-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  min-height: calc(100vh - 120px);
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .logo-text {
    display: none;
  }
  
  .user-detail {
    display: none;
  }
  
  .nav-content {
    padding: 0 16px;
  }
  
  .receiver-main {
    padding: 16px;
  }
}
</style>
