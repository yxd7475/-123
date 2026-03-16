<template>
  <div>
    <div class="page-header">
      <h2>数据备份</h2>
    </div>

    <el-card style="margin-bottom: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>备份操作</span>
          <el-button type="primary" @click="handleCreateBackup" :loading="creating">
            <el-icon><Plus /></el-icon>
            创建备份
          </el-button>
        </div>
      </template>
      <el-alert
        title="提示"
        type="info"
        description="定期备份数据可以防止数据丢失。建议每天进行一次数据备份。"
        :closable="false"
        show-icon
      />
    </el-card>

    <el-card>
      <template #header>
        <span>备份列表</span>
      </template>
      <el-table :data="backups" stripe>
        <el-table-column prop="filename" label="文件名" min-width="250" />
        <el-table-column prop="size" label="文件大小" width="120">
          <template #default="{ row }">{{ formatSize(row.size) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDownload(row)">下载</el-button>
            <el-button link type="warning" @click="handleRestore(row)" :loading="row.restoring">
              恢复
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const backups = ref([])
const creating = ref(false)

const fetchBackups = async () => {
  try {
    const res = await api.get('/backup')
    backups.value = res.backups
  } catch (error) {
    console.error(error)
  }
}

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const handleCreateBackup = async () => {
  creating.value = true
  try {
    const res = await api.post('/backup')
    ElMessage.success('备份创建成功')
    fetchBackups()
  } catch (error) {
    console.error(error)
  } finally {
    creating.value = false
  }
}

const handleDownload = (row) => {
  window.open(`/api/backup/${row.filename}/download`, '_blank')
}

const handleRestore = (row) => {
  ElMessageBox.confirm(
    '恢复数据将覆盖当前数据库，确定要继续吗？恢复后需要重启服务器。',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    row.restoring = true
    try {
      await api.post(`/backup/${row.filename}/restore`)
      ElMessage.success('数据恢复成功，请重启服务器')
    } catch (error) {
      console.error(error)
    } finally {
      row.restoring = false
    }
  }).catch(() => {})
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除备份文件 "${row.filename}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/backup/${row.filename}`)
      ElMessage.success('删除成功')
      fetchBackups()
    } catch (error) {
      console.error(error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchBackups()
})
</script>
