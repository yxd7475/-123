<template>
  <el-container class="layout-container">
    <el-aside 
      v-if="!isMobile"
      :width="isCollapsed ? '64px' : '240px'" 
      class="app-aside"
    >
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
            {{ authStore.user?.username?.charAt(0).toUpperCase() }}
          </div>
          <div class="user-info">
            <span class="user-name">{{ authStore.user?.username }}</span>
            <span class="user-role">{{ roleNames[authStore.user?.role] || '用户' }}</span>
          </div>
        </div>
      </div>
    </el-aside>
    
    <el-container class="app-main">
      <el-header class="app-header">
        <div class="header-left">
          <button class="menu-toggle" v-if="isMobile" @click="showMobileMenu = true">
            <el-icon><Menu /></el-icon>
          </button>
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ authStore.user?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <div class="user-details" v-if="!isMobile">
                <span class="user-name">{{ authStore.user?.username }}</span>
                <span class="user-role">{{ roleNames[authStore.user?.role] || '用户' }}</span>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人设置
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
    
    <div 
      v-if="isMobile && showMobileMenu" 
      class="mobile-menu-overlay" 
      @click="showMobileMenu = false"
    ></div>
    <div 
      v-if="isMobile" 
      class="mobile-drawer"
      :class="{ 'show': showMobileMenu }"
    >
      <div class="mobile-drawer-header">
        <div class="mobile-logo">
          <div class="mobile-logo-icon">
            <el-icon><Box /></el-icon>
          </div>
          <span class="mobile-logo-text">库房管理</span>
        </div>
        <el-icon class="mobile-drawer-close" @click="showMobileMenu = false"><Close /></el-icon>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="mobile-menu"
        router
        @select="showMobileMenu = false"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页概览</template>
        </el-menu-item>
        
        <el-menu-item index="/items">
          <el-icon><Box /></el-icon>
          <template #title>物品管理</template>
        </el-menu-item>
        
        <el-menu-item index="/inbound">
          <el-icon><Download /></el-icon>
          <template #title>入库管理</template>
        </el-menu-item>
        
        <el-menu-item index="/outbound">
          <el-icon><Upload /></el-icon>
          <template #title>出库管理</template>
        </el-menu-item>
        
        <el-menu-item index="/inventory">
          <el-icon><DataBoard /></el-icon>
          <template #title>库存查询</template>
        </el-menu-item>
        
        <el-menu-item index="/alerts">
          <el-icon><Bell /></el-icon>
          <template #title>库存预警</template>
          <el-badge v-if="alertCount > 0" :value="alertCount" class="menu-badge" />
        </el-menu-item>
        
        <el-menu-item index="/statistics">
          <el-icon><DataLine /></el-icon>
          <template #title>统计报表</template>
        </el-menu-item>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>个人设置</template>
        </el-menu-item>
        
        <el-menu-item index="/users" v-if="authStore.hasRole('admin')">
          <el-icon><UserFilled /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        
        <el-menu-item @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          <template #title>退出登录</template>
        </el-menu-item>
      </el-menu>
    </div>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Box, HomeFilled, Download, Upload, DataBoard, DataLine, 
  Setting, User, SwitchButton, Menu, Close, Fold, Expand, Bell, UserFilled
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const route = useRoute()
const authStore = useAuthStore()

const isCollapsed = ref(false)
const isMobile = ref(false)
const showMobileMenu = ref(false)
const alertCount = ref(0)

const roleNames = {
  admin: '管理员',
  operator: '操作员',
  viewer: '查看员',
  receiver: '领用人'
}

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const nameMap = {
    '/dashboard': '首页概览',
    '/items': '物品管理',
    '/inbound': '入库管理',
    '/outbound': '出库管理',
    '/inventory': '库存查询',
    '/alerts': '库存预警',
    '/statistics': '统计报表',
    '/users': '用户管理',
    '/logs': '操作日志',
    '/backup': '数据备份',
    '/settings': '个人设置'
  }
  return nameMap[route.path] || '库房管理'
})

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
  if (isMobile.value) {
    isCollapsed.value = true
  }
}

const fetchAlertCount = async () => {
  try {
    const res = await api.get('/inventory/alerts', { params: { status: 'pending', per_page: 1 } })
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
  }).then(() => {
    authStore.clearAuth()
    window.location.href = '/login'
  }).catch(() => {})
}

const handleUserCommand = (command) => {
  if (command === 'profile') {
    window.location.href = '/settings'
  } else if (command === 'logout') {
    handleLogout()
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  fetchAlertCount()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.app-aside {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-right: 1px solid rgba(226, 232, 240, 0.5);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
}

.app-aside:not(.collapsed) .el-menu {
  width: 240px;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
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
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: 1px;
}

.logo-mini {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border-radius: 10px;
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
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.side-menu {
  flex: 1;
  border-right: none;
  padding: 12px 0;
  overflow-y: auto;
}

.side-menu :deep(.el-menu-item),
.side-menu :deep(.el-sub-menu__title) {
  color: #475569;
}

.side-menu :deep(.el-menu-item:hover),
.side-menu :deep(.el-sub-menu__title:hover) {
  background-color: #f8fafc !important;
}

.side-menu :deep(.el-menu-item.is-active) {
  background-color: #eef2ff !important;
  color: #4f46e5;
}

.side-menu :deep(.el-sub-menu .el-menu-item) {
  padding-left: 50px !important;
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
  background: #f8fafc;
  border-radius: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border-radius: 10px;
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
  color: #0f172a;
}

.user-role {
  font-size: 12px;
  color: #94a3b8;
}

.app-main {
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.app-header {
  height: 64px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-toggle {
  display: none;
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  color: #475569;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-info:hover {
  background: #f8fafc;
}

.user-avatar {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
}

.user-details {
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

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.mobile-menu-overlay {
  display: none;
}

.mobile-drawer {
  display: none;
}

@media (max-width: 768px) {
  .app-aside {
    display: none;
  }
  
  .menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .app-header {
    padding: 0 16px;
    height: 56px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .user-details {
    display: none;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .mobile-menu-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 998;
  }
  
  .mobile-drawer {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 280px;
    background: white;
    z-index: 999;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .mobile-drawer.show {
    transform: translateX(0);
  }
  
  .mobile-drawer-header {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .mobile-logo {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .mobile-logo-icon {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
  }
  
  .mobile-logo-text {
    font-size: 18px;
    font-weight: 600;
    color: #0f172a;
  }
  
  .mobile-drawer-close {
    font-size: 20px;
    color: #64748b;
    cursor: pointer;
  }
  
  .mobile-menu {
    flex: 1;
    border: none;
    overflow-y: auto;
  }
  
  .mobile-menu :deep(.el-menu-item),
  .mobile-menu :deep(.el-sub-menu__title) {
    color: #475569;
    height: 50px;
    line-height: 50px;
  }
  
  .mobile-menu :deep(.el-menu-item:hover),
  .mobile-menu :deep(.el-sub-menu__title:hover) {
    background-color: #f8fafc !important;
  }
  
  .mobile-menu :deep(.el-menu-item.is-active) {
    background-color: #eef2ff !important;
    color: #4f46e5;
  }
}
</style>
