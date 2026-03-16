<template>
  <div class="public-layout">
    <header class="public-header">
      <div class="header-content">
        <div class="logo">
          <div class="logo-icon">
            <el-icon><Box /></el-icon>
          </div>
          <span class="logo-text">物品领用系统</span>
        </div>
      </div>
    </header>
    
    <nav class="public-nav">
      <div class="nav-content">
        <router-link to="/public" class="nav-item" :class="{ active: $route.path === '/public' }">
          <el-icon><Goods /></el-icon>
          <span>物品列表</span>
        </router-link>
        <router-link to="/public/records" class="nav-item" :class="{ active: $route.path === '/public/records' }">
          <el-icon><List /></el-icon>
          <span>领取记录</span>
        </router-link>
      </div>
    </nav>
    
    <main class="public-main">
      <router-view />
    </main>
    
    <footer class="public-footer">
      <p>© 2024 物品领用系统</p>
    </footer>
  </div>
</template>

<script setup>
import { Box, Goods, List } from '@element-plus/icons-vue'
</script>

<style scoped>
.public-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  display: flex;
  flex-direction: column;
}

.public-header {
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
  justify-content: center;
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

.public-nav {
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

.public-main {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
}

.public-footer {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px) saturate(180%);
  -webkit-backdrop-filter: blur(8px) saturate(180%);
  border-top: 1px solid rgba(226, 232, 240, 0.3);
  padding: 16px;
  text-align: center;
}

.public-footer p {
  color: #94a3b8;
  font-size: 13px;
  margin: 0;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .nav-content {
    padding: 0 16px;
  }
  
  .public-main {
    padding: 16px;
  }
}
</style>
