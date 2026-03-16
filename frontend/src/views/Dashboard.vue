<template>
  <div class="dashboard-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">欢迎回来，{{ userName }}</h1>
        <p class="page-subtitle">{{ currentDate }}</p>
      </div>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card" v-for="(stat, index) in stats" :key="index">
        <div class="stat-content">
          <div class="stat-info">
            <span class="stat-label">{{ stat.label }}</span>
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-change" :class="stat.trend">
              <el-icon><component :is="stat.trend === 'up' ? 'Top' : 'Bottom'" /></el-icon>
              {{ stat.change }}
            </span>
          </div>
          <div class="stat-icon" :style="{ background: stat.gradient }">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
        </div>
      </div>
    </div>
    
    <div class="content-grid">
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">出入库趋势</h3>
          <div class="card-actions">
            <el-radio-group v-model="trendDays" size="small" @change="fetchTrendData">
              <el-radio-button :value="7">7天</el-radio-button>
              <el-radio-button :value="14">14天</el-radio-button>
              <el-radio-button :value="30">30天</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div ref="trendChartRef" class="chart-container"></div>
      </div>
      
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">物品分类</h3>
        </div>
        <div ref="categoryChartRef" class="chart-container"></div>
      </div>
    </div>
    
    <div class="content-grid">
      <div class="info-card">
        <div class="card-header">
          <h3 class="card-title">今日动态</h3>
        </div>
        <div class="activity-grid">
          <div class="activity-item">
            <div class="activity-icon inbound">
              <el-icon><Download /></el-icon>
            </div>
            <div class="activity-content">
              <span class="activity-label">今日入库</span>
              <span class="activity-value">{{ overview.today?.inbound_quantity || 0 }} 件</span>
            </div>
          </div>
          <div class="activity-item">
            <div class="activity-icon outbound">
              <el-icon><Upload /></el-icon>
            </div>
            <div class="activity-content">
              <span class="activity-label">今日出库</span>
              <span class="activity-value">{{ overview.today?.outbound_quantity || 0 }} 件</span>
            </div>
          </div>
          <div class="activity-item">
            <div class="activity-icon value">
              <el-icon><Money /></el-icon>
            </div>
            <div class="activity-content">
              <span class="activity-label">本月入库金额</span>
              <span class="activity-value">¥{{ formatNumber(overview.month?.inbound_value || 0) }}</span>
            </div>
          </div>
          <div class="activity-item">
            <div class="activity-icon cost">
              <el-icon><Wallet /></el-icon>
            </div>
            <div class="activity-content">
              <span class="activity-label">本月出库金额</span>
              <span class="activity-value">¥{{ formatNumber(overview.month?.outbound_value || 0) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="info-card">
        <div class="card-header">
          <h3 class="card-title">库存预警</h3>
          <el-button type="primary" text size="small" @click="$router.push('/alerts')">
            查看全部
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div v-if="alerts.length === 0" class="empty-state">
          <el-icon :size="48" color="#10b981"><CircleCheck /></el-icon>
          <p>暂无库存预警</p>
        </div>
        <div v-else class="alert-list">
          <div v-for="alert in alerts" :key="alert.id" class="alert-item">
            <div class="alert-indicator" :class="alert.alert_type"></div>
            <div class="alert-content">
              <span class="alert-name">{{ alert.item_name }}</span>
              <span class="alert-detail">库存 {{ alert.current_quantity }} / 阈值 {{ alert.threshold }}</span>
            </div>
            <el-tag :type="alert.alert_type === 'low' ? 'danger' : 'warning'" size="small">
              {{ alert.alert_type === 'low' ? '库存不足' : '库存过剩' }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { 
  Box, Goods, Money, Bell, Download, Upload, 
  Top, Bottom, ArrowRight, CircleCheck, Wallet
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const authStore = useAuthStore()
const trendChartRef = ref()
const categoryChartRef = ref()
const trendDays = ref(7)

const userName = computed(() => authStore.user?.real_name || '用户')
const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    weekday: 'long'
  })
})

const summary = ref({
  total_items: 0,
  total_quantity: 0,
  total_value: 0,
  pending_alerts: 0
})

const overview = ref({
  today: {},
  month: {}
})

const alerts = ref([])
const trendData = ref([])
const categoryData = ref([])

const stats = computed(() => [
  {
    label: '物品总数',
    value: summary.value.total_items,
    change: '种物品',
    trend: 'up',
    icon: Box,
    gradient: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)'
  },
  {
    label: '库存总量',
    value: summary.value.total_quantity,
    change: '件商品',
    trend: 'up',
    icon: Goods,
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
  },
  {
    label: '库存总值',
    value: `¥${formatNumber(summary.value.total_value)}`,
    change: '总价值',
    trend: 'up',
    icon: Money,
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
  },
  {
    label: '预警数量',
    value: summary.value.pending_alerts,
    change: '待处理',
    trend: 'down',
    icon: Bell,
    gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
  }
])

const formatNumber = (num) => {
  if (!num) return '0.00'
  return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const fetchData = async () => {
  try {
    const [summaryRes, overviewRes, alertsRes, trendRes, categoryRes] = await Promise.all([
      api.get('/inventory/summary'),
      api.get('/statistics/overview'),
      api.get('/inventory/alerts?status=pending'),
      api.get(`/statistics/trend?days=${trendDays.value}`),
      api.get('/statistics/category')
    ])
    
    summary.value = summaryRes
    overview.value = overviewRes
    alerts.value = alertsRes.alerts.slice(0, 5)
    trendData.value = trendRes
    categoryData.value = categoryRes
    
    initCharts()
  } catch (error) {
    console.error(error)
  }
}

const fetchTrendData = async () => {
  try {
    const trendRes = await api.get(`/statistics/trend?days=${trendDays.value}`)
    trendData.value = trendRes
    initTrendChart()
  } catch (error) {
    console.error(error)
  }
}

const initCharts = () => {
  initTrendChart()
  initCategoryChart()
}

const initTrendChart = () => {
  const trendChart = echarts.init(trendChartRef.value)
  
  const trendOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: { color: '#0f172a', fontSize: 13 },
      padding: [12, 16],
      borderRadius: 8
    },
    legend: {
      data: ['入库', '出库'],
      top: 0,
      right: 0,
      icon: 'roundRect',
      itemWidth: 12,
      itemHeight: 4
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '40px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trendData.value.map(item => item.date.slice(5)),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#94a3b8', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#94a3b8', fontSize: 12 },
      splitLine: { lineStyle: { color: '#f1f5f9' } }
    },
    series: [
      {
        name: '入库',
        type: 'line',
        smooth: true,
        data: trendData.value.map(item => item.inbound),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.15)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0)' }
          ])
        },
        lineStyle: { width: 3, color: '#10b981' },
        itemStyle: { color: '#10b981' },
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: '出库',
        type: 'line',
        smooth: true,
        data: trendData.value.map(item => item.outbound),
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(99, 102, 241, 0.15)' },
            { offset: 1, color: 'rgba(99, 102, 241, 0)' }
          ])
        },
        lineStyle: { width: 3, color: '#6366f1' },
        itemStyle: { color: '#6366f1' },
        symbol: 'circle',
        symbolSize: 6
      }
    ]
  }
  
  trendChart.setOption(trendOption)
  
  window.addEventListener('resize', () => {
    trendChart.resize()
  })
}

const initCategoryChart = () => {
  const categoryChart = echarts.init(categoryChartRef.value)
  
  const categoryOption = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: { color: '#0f172a', fontSize: 13 },
      padding: [12, 16],
      borderRadius: 8
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center',
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8
    },
    series: [
      {
        type: 'pie',
        radius: ['50%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: '600'
          }
        },
        data: categoryData.value.map((item, index) => ({
          name: item.category || '未分类',
          value: item.total_quantity,
          itemStyle: {
            color: ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'][index % 6]
          }
        }))
      }
    ]
  }
  
  categoryChart.setOption(categoryOption)
  
  window.addEventListener('resize', () => {
    categoryChart.resize()
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 24px;
  transition: all var(--transition-normal);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.95);
}

.stat-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.stat-change.up {
  color: #10b981;
}

.stat-change.down {
  color: #ef4444;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card, .info-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-container {
  height: 280px;
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(248, 250, 252, 0.6);
  backdrop-filter: blur(8px) saturate(180%);
  -webkit-backdrop-filter: blur(8px) saturate(180%);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.activity-item:hover {
  background: rgba(241, 245, 249, 0.8);
}

.activity-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.activity-icon.inbound {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.activity-icon.outbound {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
}

.activity-icon.value {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.activity-icon.cost {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.activity-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.activity-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.activity-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 0;
  color: var(--text-tertiary);
}

.empty-state p {
  margin-top: 12px;
  font-size: 14px;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(248, 250, 252, 0.6);
  backdrop-filter: blur(8px) saturate(180%);
  -webkit-backdrop-filter: blur(8px) saturate(180%);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.alert-item:hover {
  background: rgba(241, 245, 249, 0.8);
}

.alert-indicator {
  width: 4px;
  height: 36px;
  border-radius: 2px;
}

.alert-indicator.low {
  background: #ef4444;
}

.alert-indicator.high {
  background: #f59e0b;
}

.alert-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.alert-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.alert-detail {
  font-size: 12px;
  color: var(--text-tertiary);
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .activity-grid {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 24px;
  }
}
</style>
