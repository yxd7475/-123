<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>系统设置</h2>
      <p class="page-desc">管理您的账户信息和系统配置</p>
    </div>

    <el-row :gutter="24">
      <el-col :span="8">
        <el-card class="settings-card profile-card">
          <template #header>
            <div class="card-header">
              <div class="header-icon user-icon">
                <el-icon :size="24"><User /></el-icon>
              </div>
              <div class="header-text">
                <span class="header-title">个人信息</span>
                <span class="header-desc">修改您的个人资料</span>
              </div>
            </div>
          </template>
          <div class="avatar-section">
            <el-avatar :size="80" class="user-avatar">
              {{ profileForm.real_name?.charAt(0) || 'U' }}
            </el-avatar>
            <div class="user-info-text">
              <h3>{{ profileForm.real_name || '未设置姓名' }}</h3>
              <el-tag :type="getRoleType(profileForm.role)" size="small">
                {{ getRoleLabel(profileForm.role) }}
              </el-tag>
            </div>
          </div>
          <el-form :model="profileForm" label-width="80px" class="settings-form">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled>
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="姓名">
              <el-input v-model="profileForm.real_name" placeholder="请输入姓名">
                <template #prefix>
                  <el-icon><EditPen /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="注册时间">
              <el-input :value="formatDate(profileForm.created_at)" disabled>
                <template #prefix>
                  <el-icon><Clock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="profileLoading">
                <el-icon><Check /></el-icon>
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="settings-card password-card">
          <template #header>
            <div class="card-header">
              <div class="header-icon lock-icon">
                <el-icon :size="24"><Lock /></el-icon>
              </div>
              <div class="header-text">
                <span class="header-title">修改密码</span>
                <span class="header-desc">定期更换密码更安全</span>
              </div>
            </div>
          </template>
          <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px" class="settings-form">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入原密码">
                <template #prefix>
                  <el-icon><Key /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码">
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password placeholder="请再次输入新密码">
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="passwordLoading">
                <el-icon><Check /></el-icon>
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="settings-card system-card">
          <template #header>
            <div class="card-header">
              <div class="header-icon system-icon">
                <el-icon :size="24"><Monitor /></el-icon>
              </div>
              <div class="header-text">
                <span class="header-title">系统信息</span>
                <span class="header-desc">当前系统版本信息</span>
              </div>
            </div>
          </template>
          <div class="system-info">
            <div class="info-item">
              <div class="info-icon">
                <el-icon><Box /></el-icon>
              </div>
              <div class="info-content">
                <span class="info-label">系统名称</span>
                <span class="info-value">库房出入库管理系统</span>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon version">
                <el-icon><Promotion /></el-icon>
              </div>
              <div class="info-content">
                <span class="info-label">版本号</span>
                <span class="info-value">v1.0.0</span>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon tech">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="info-content">
                <span class="info-label">技术栈</span>
                <span class="info-value">Vue3 + Flask</span>
              </div>
            </div>
            <div class="info-item">
              <div class="info-icon db">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="info-content">
                <span class="info-label">数据库</span>
                <span class="info-value">SQLite</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px" v-if="authStore.hasRole('admin')">
      <el-col :span="24">
        <el-card class="settings-card public-page-card">
          <template #header>
            <div class="card-header">
              <div class="header-icon public-icon">
                <el-icon :size="24"><Link /></el-icon>
              </div>
              <div class="header-text">
                <span class="header-title">公开领用页面</span>
                <span class="header-desc">无需登录的物品领用入口</span>
              </div>
            </div>
          </template>
          <div class="public-page-content">
            <div class="public-url-section">
              <div class="url-label">访问地址</div>
              <div class="url-input-wrapper">
                <el-input :value="publicPageUrl" readonly size="large">
                  <template #prefix>
                    <el-icon><Link /></el-icon>
                  </template>
                </el-input>
                <el-button type="primary" size="large" @click="copyPublicUrl">
                  <el-icon><DocumentCopy /></el-icon>
                  复制链接
                </el-button>
                <el-button size="large" @click="openPublicPage">
                  <el-icon><View /></el-icon>
                  打开页面
                </el-button>
              </div>
            </div>
            
            <el-divider />
            
            <div class="public-stats">
              <div class="stat-item">
                <div class="stat-value">{{ publicStats.todayReceive }}</div>
                <div class="stat-label">今日领取</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ publicStats.totalReceive }}</div>
                <div class="stat-label">总领取次数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ publicStats.availableItems }}</div>
                <div class="stat-label">可领物品</div>
              </div>
            </div>
            
            <div class="public-actions">
              <el-button type="primary" @click="$router.push('/public-records')">
                <el-icon><List /></el-icon>
                查看领取记录
              </el-button>
              <el-button @click="exportPublicRecords">
                <el-icon><Download /></el-icon>
                导出记录
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px" v-if="authStore.hasRole('admin')">
      <el-col :span="24">
        <el-card class="settings-card admin-card">
          <template #header>
            <div class="card-header">
              <div class="header-icon admin-icon">
                <el-icon :size="24"><Tools /></el-icon>
              </div>
              <div class="header-text">
                <span class="header-title">管理员功能</span>
                <span class="header-desc">系统管理快捷入口</span>
              </div>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="admin-action" @click="$router.push('/users')">
                <div class="action-icon users">
                  <el-icon :size="28"><UserFilled /></el-icon>
                </div>
                <span class="action-text">用户管理</span>
                <span class="action-desc">管理系统用户账户</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="admin-action" @click="$router.push('/logs')">
                <div class="action-icon logs">
                  <el-icon :size="28"><Document /></el-icon>
                </div>
                <span class="action-text">操作日志</span>
                <span class="action-desc">查看系统操作记录</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="admin-action" @click="$router.push('/backup')">
                <div class="action-icon backup">
                  <el-icon :size="28"><FolderOpened /></el-icon>
                </div>
                <span class="action-text">数据备份</span>
                <span class="action-desc">备份与恢复数据</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="admin-action" @click="clearCache">
                <div class="action-icon cache">
                  <el-icon :size="28"><RefreshRight /></el-icon>
                </div>
                <span class="action-text">清理缓存</span>
                <span class="action-desc">清理系统临时文件</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  User, EditPen, Clock, Check, Lock, Key, Monitor, Box, 
  Promotion, Cpu, Coin, Tools, UserFilled, Document, 
  FolderOpened, RefreshRight, Link, DocumentCopy, View, 
  List, Download
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()
const passwordFormRef = ref()
const profileLoading = ref(false)
const passwordLoading = ref(false)

const publicPageUrl = computed(() => {
  return `${window.location.origin}/public`
})

const publicStats = reactive({
  todayReceive: 0,
  totalReceive: 0,
  availableItems: 0
})

const profileForm = reactive({
  username: '',
  real_name: '',
  role: '',
  created_at: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const roles = [
  { value: 'admin', label: '管理员' },
  { value: 'operator', label: '操作员' },
  { value: 'viewer', label: '查看员' }
]

const getRoleType = (role) => {
  switch (role) {
    case 'admin': return 'danger'
    case 'operator': return 'primary'
    default: return 'info'
  }
}

const getRoleLabel = (role) => {
  const roleObj = roles.find(r => r.value === role)
  return roleObj ? roleObj.label : role
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchProfile = async () => {
  try {
    const res = await api.get('/auth/profile')
    Object.assign(profileForm, res)
  } catch (error) {
    console.error(error)
  }
}

const updateProfile = async () => {
  profileLoading.value = true
  try {
    await api.put('/auth/profile', profileForm)
    ElMessage.success('保存成功')
    authStore.user.real_name = profileForm.real_name
    localStorage.setItem('user', JSON.stringify(authStore.user))
  } catch (error) {
    console.error(error)
  } finally {
    profileLoading.value = false
  }
}

const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true
      try {
        await api.post('/auth/change-password', {
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password
        })
        ElMessage.success('密码修改成功')
        passwordFormRef.value.resetFields()
      } catch (error) {
        console.error(error)
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

const clearCache = () => {
  ElMessage.success('缓存已清理')
}

const copyPublicUrl = () => {
  navigator.clipboard.writeText(publicPageUrl.value)
  ElMessage.success('链接已复制到剪贴板')
}

const openPublicPage = () => {
  window.open(publicPageUrl.value, '_blank')
}

const fetchPublicStats = async () => {
  try {
    const res = await api.get('/public/stats')
    publicStats.todayReceive = res.today_receive || 0
    publicStats.totalReceive = res.total_receive || 0
    publicStats.availableItems = res.available_items || 0
  } catch (error) {
    console.error(error)
  }
}

const exportPublicRecords = async () => {
  try {
    const res = await api.get('/public/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `公开领取记录_${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  fetchProfile()
  if (authStore.hasRole('admin')) {
    fetchPublicStats()
  }
})
</script>

<style scoped>
.settings-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.page-desc {
  color: #6b7280;
  font-size: 14px;
  margin-top: 8px;
}

.settings-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
}

.settings-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.settings-card :deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.settings-card :deep(.el-card__body) {
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-icon.user-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-icon.lock-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.header-icon.system-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.header-icon.admin-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.header-text {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}

.header-desc {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  border-radius: 12px;
  margin-bottom: 24px;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 32px;
  font-weight: 600;
}

.user-info-text h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #1a1a2e;
}

.settings-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e5e7eb;
  transition: all 0.3s;
}

.settings-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #667eea;
}

.settings-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.settings-form :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  height: 40px;
  padding: 0 24px;
}

.settings-form :deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #5a6fd6 0%, #6a4190 100%);
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  transition: all 0.3s;
}

.info-item:hover {
  background: #f3f4f6;
}

.info-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 20px;
}

.info-icon.version {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.info-icon.tech {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.info-icon.db {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.info-content {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 12px;
  color: #9ca3af;
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-top: 4px;
}

.admin-card :deep(.el-card__body) {
  padding: 24px;
}

.admin-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.admin-action:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.admin-action:hover .action-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.admin-action:hover .action-text {
  color: white;
}

.admin-action:hover .action-desc {
  color: rgba(255, 255, 255, 0.8);
}

.action-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s;
}

.action-icon.users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.action-icon.logs {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.action-icon.backup {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.action-icon.cache {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.action-text {
  margin-top: 16px;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  transition: color 0.3s;
}

.action-desc {
  margin-top: 6px;
  font-size: 12px;
  color: #9ca3af;
  text-align: center;
  transition: color 0.3s;
}

.public-page-card :deep(.el-card__body) {
  padding: 24px;
}

.public-page-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.public-url-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.url-label {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.url-input-wrapper {
  display: flex;
  gap: 12px;
}

.url-input-wrapper .el-input {
  flex: 1;
}

.public-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
  border-radius: 12px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

.public-actions {
  display: flex;
  gap: 12px;
}

.header-icon.public-icon {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

@media (max-width: 768px) {
  .settings-page {
    padding: 0;
  }
  
  .page-header h2 {
    font-size: 20px;
  }
  
  .page-desc {
    font-size: 13px;
  }
  
  :deep(.el-col) {
    width: 100% !important;
    max-width: 100% !important;
    margin-bottom: 16px;
  }
  
  :deep(.el-row) {
    margin-left: 0 !important;
    margin-right: 0 !important;
  }
  
  .settings-card {
    min-width: 0;
  }
  
  .settings-card,
  .settings-card * {
    writing-mode: horizontal-tb !important;
    text-orientation: mixed !important;
    word-break: break-word;
    white-space: normal;
  }
  
  .settings-card :deep(.el-card__header) {
    padding: 16px;
  }
  
  .settings-card :deep(.el-card__body) {
    padding: 16px;
  }
  
  .card-header {
    flex-wrap: wrap;
  }
  
  .header-icon {
    width: 40px;
    height: 40px;
  }
  
  .header-title {
    font-size: 15px;
  }
  
  .header-desc {
    font-size: 11px;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
    padding: 16px;
  }
  
  .user-info-text h3 {
    font-size: 16px;
  }
  
  .settings-form :deep(.el-form-item__label) {
    font-size: 13px;
  }
  
  .info-item {
    padding: 12px;
  }
  
  .info-icon {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
  
  .info-value {
    font-size: 13px;
  }
  
  .admin-action {
    padding: 16px 12px;
  }
  
  .action-icon {
    width: 44px;
    height: 44px;
  }
  
  .action-text {
    font-size: 14px;
  }
  
  .url-input-wrapper {
    flex-direction: column;
  }
  
  .url-input-wrapper .el-button {
    width: 100%;
  }
  
  .public-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stat-item {
    padding: 16px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .public-actions {
    flex-direction: column;
  }
  
  .public-actions .el-button {
    width: 100%;
  }
}
</style>
