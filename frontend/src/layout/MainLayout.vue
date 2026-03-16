<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapsed ? '64px' : '240px'" class="app-aside">
      <div class="sidebar-header">
        <div class="logo" v-if="!isCollapsed">
          <div class="logo-icon">
            <el-icon><Box /></el-icon>
          </div>
          <span class="logo-text">库房管理</span>
        </div>
        <div class="logo-mini" v-else>
          <el-icon><Box /></el-icon>
        </div>
        <button class="collapse-btn" @click="isCollapsed = !isCollapsed">
          <el-icon><Expand v-if="isCollapsed" /><Fold v-else /></el-icon>
        </button>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="side-menu"
        router
        :collapse="isCollapsed"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页概览</template>
        </el-menu-item>
        
        <el-sub-menu index="items">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>物品管理</span>
          </template>
          <el-menu-item index="/items">物品列表</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="inbound">
          <template #title>
            <el-icon><Download /></el-icon>
            <span>入库管理</span>
          </template>
          <el-menu-item index="/inbound">入库记录</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="outbound">
          <template #title>
            <el-icon><Upload /></el-icon>
            <span>出库管理</span>
          </template>
          <el-menu-item index="/outbound">出库记录</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="inventory">
          <template #title>
            <el-icon><DataBoard /></el-icon>
            <span>库存管理</span>
          </template>
          <el-menu-item index="/inventory">库存查询</el-menu-item>
          <el-menu-item index="/alerts">
            库存预警
            <el-badge v-if="alertCount > 0" :value="alertCount" class="menu-badge" />
          </el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/statistics">
          <el-icon><DataLine /></el-icon>
          <template #title>统计报表</template>
        </el-menu-item>
        
        <el-sub-menu index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/settings">个人设置</el-menu-item>
          <el-menu-item index="/users" v-if="authStore.hasRole('admin')">用户管理</el-menu-item>
          <el-menu-item index="/logs" v-if="authStore.hasRole('admin')">操作日志</el-menu-item>
          <el-menu-item index="/backup" v-if="authStore.hasRole('admin')">数据备份</el-menu-item>
          <el-menu-item @click="handleLogout">退出登录</el-menu-item>
        </el-sub-menu>
      </el-menu>
      
      <div class="sidebar-footer" v-if="!isCollapsed">
        <div class="user-card">
          <div class="user-avatar">
            {{ authStore.user?.real_name?.charAt(0) }}
          </div>
          <div class="user-info">
            <span class="user-name">{{ authStore.user?.real_name }}</span>
            <span class="user-role">{{ getRoleName(authStore.user?.role) }}</span>
          </div>
        </div>
      </div>
    </el-aside>
    
    <el-container class="main-container">
      <el-header class="app-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-badge :value="alertCount" :hidden="alertCount === 0" class="alert-badge">
            <el-button :icon="Bell" circle @click="$router.push('/alerts')" />
          </el-badge>
        </div>
      </el-header>
      
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Box, Bell, HomeFilled, Download, Upload, DataBoard, 
  DataLine, Setting, Fold, Expand
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapsed = ref(false)
const alertCount = ref(0)

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => {
  const titles = {
    '/dashboard': '首页概览',
    '/items': '物品列表',
    '/inbound': '入库记录',
    '/outbound': '出库记录',
    '/inventory': '库存查询',
    '/alerts': '库存预警',
    '/statistics': '统计报表',
    '/settings': '个人设置',
    '/users': '用户管理',
    '/logs': '操作日志',
    '/backup': '数据备份'
  }
  return titles[route.path] || '库房管理'
})

const getRoleName = (role) => {
  const roleMap = {
    admin: '管理员',
    operator: '操作员',
    viewer: '查看员'
  }
  return roleMap[role] || role
}

const fetchAlertCount = async () => {
  try {
    const res = await api.get('/inventory/alerts', { params: { status: 'pending' } })
    alertCount.value = res.total || 0
  } catch (error) {
    console.error(error)
  }
}

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

onMounted(() => {
  if (authStore.hasAnyRole(['admin', 'operator'])) {
    fetchAlertCount()
  }
})
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: var(--bg-secondary);
}

.app-aside {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-right: 1px solid rgba(226, 232, 240, 0.5);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  position: relative;
  z-index: 100;
}

.sidebar-header {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(226, 232, 240, 0.3);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.logo-mini {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  margin: 0 auto;
}

.collapse-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  transition: all var(--transition-fast);
}

.collapse-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.side-menu {
  flex: 1;
  padding: 12px 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.side-menu:not(.el-menu--collapse) {
  width: 240px;
}

.menu-badge {
  margin-left: 8px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(226, 232, 240, 0.3);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(248, 250, 252, 0.6);
  backdrop-filter: blur(8px) saturate(180%);
  -webkit-backdrop-filter: blur(8px) saturate(180%);
  border-radius: var(--radius-md);
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--text-tertiary);
}

.main-container {
  display: flex;
  flex-direction: column;
}

.app-header {
  height: 64px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.alert-badge {
  cursor: pointer;
}

.alert-badge :deep(.el-button) {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.alert-badge :deep(.el-button:hover) {
  background: var(--bg-tertiary);
  border-color: var(--text-tertiary);
  color: var(--text-primary);
}

.app-main {
  padding: 24px;
  background: var(--bg-secondary);
  min-height: calc(100vh - 64px);
  overflow-y: auto;
}

@media (max-width: 768px) {
  .app-aside {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 200;
    transform: translateX(-100%);
  }
  
  .app-aside:not(.collapsed) {
    transform: translateX(0);
  }
  
  .app-main {
    padding: 16px;
  }
  
  .app-header {
    padding: 0 16px;
  }
}
</style>
