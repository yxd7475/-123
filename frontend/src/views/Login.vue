<template>
  <div class="login-container">
    <div class="login-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>
    
    <div class="login-content">
      <div class="login-card">
        <div class="login-header">
          <div class="logo">
            <div class="logo-icon">
              <el-icon><Box /></el-icon>
            </div>
          </div>
          <h1 class="login-title">库房管理系统</h1>
          <p class="login-subtitle">智能仓储 · 高效管理</p>
        </div>
        
        <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="demo-accounts">
          <div class="demo-header" @click="showDemo = !showDemo">
            <span>演示账号</span>
            <el-icon :class="{ 'is-rotate': showDemo }"><ArrowDown /></el-icon>
          </div>
          <transition name="slide-fade">
            <div v-if="showDemo" class="demo-list">
              <div class="demo-item" @click="fillDemo('admin', 'admin123')">
                <span class="demo-role">管理员</span>
                <span class="demo-account">admin / admin123</span>
              </div>
              <div class="demo-item" @click="fillDemo('operator', 'operator123')">
                <span class="demo-role">操作员</span>
                <span class="demo-account">operator / operator123</span>
              </div>
              <div class="demo-item" @click="fillDemo('viewer', 'viewer123')">
                <span class="demo-role">查看员</span>
                <span class="demo-account">viewer / viewer123</span>
              </div>
            </div>
          </transition>
        </div>
      </div>
      
      <div class="login-footer">
        <p>© 2024 库房出入库管理系统 · 专业 · 高效 · 智能</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, ArrowDown, Box } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)
const showDemo = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await api.post('/auth/login', form)
        authStore.setAuth(res.token, res.user)
        ElMessage.success('登录成功')
        router.push('/dashboard')
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}

const fillDemo = (username, password) => {
  form.username = username
  form.password = password
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: rgba(255, 255, 255, 0.1);
  top: -200px;
  right: -200px;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: rgba(255, 255, 255, 0.08);
  bottom: -100px;
  left: -100px;
  animation-delay: -5s;
}

.orb-3 {
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.06);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

.login-content {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  padding: 24px;
}

.login-card {
  width: 400px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.login-subtitle {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.login-form :deep(.el-input__wrapper) {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 4px 16px;
  height: 48px;
  box-shadow: none;
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: var(--text-tertiary);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.login-form :deep(.el-input__inner) {
  font-size: 15px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  margin-top: 8px;
}

.demo-accounts {
  margin-top: 24px;
  border-top: 1px solid var(--border-light);
  padding-top: 20px;
}

.demo-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text-tertiary);
  font-size: 13px;
  padding: 8px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.demo-header:hover {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.demo-header .el-icon {
  transition: transform var(--transition-fast);
}

.demo-header .el-icon.is-rotate {
  transform: rotate(180deg);
}

.demo-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.demo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.demo-item:hover {
  background: var(--bg-tertiary);
  transform: translateX(4px);
}

.demo-role {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.demo-account {
  font-size: 12px;
  color: var(--text-tertiary);
  font-family: monospace;
}

.login-footer {
  text-align: center;
}

.login-footer p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  margin: 0;
}

@media (max-width: 480px) {
  .login-card {
    width: 100%;
    max-width: 360px;
    padding: 32px 24px;
  }
  
  .login-title {
    font-size: 24px;
  }
  
  .logo-icon {
    width: 56px;
    height: 56px;
    font-size: 24px;
  }
}
</style>
