<template>
  <div>
    <div class="page-header">
      <h2>统计报表</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="chart-container">
          <div class="chart-title">入库类型统计</div>
          <div ref="inboundTypeChartRef" style="height: 300px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-container">
          <div class="chart-title">出库类型统计</div>
          <div ref="outboundTypeChartRef" style="height: 300px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <div class="chart-container">
          <div class="chart-title">出入库趋势（近30天）</div>
          <div ref="trendChartRef" style="height: 350px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-container">
          <div class="chart-title">库存分类占比</div>
          <div ref="categoryChartRef" style="height: 350px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <div class="chart-container">
          <div class="chart-title">入库TOP10物品</div>
          <el-table :data="topInboundItems" max-height="300">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="item_name" label="物品名称" />
            <el-table-column prop="total_quantity" label="入库数量" />
          </el-table>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-container">
          <div class="chart-title">出库TOP10物品</div>
          <el-table :data="topOutboundItems" max-height="300">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="item_name" label="物品名称" />
            <el-table-column prop="total_quantity" label="出库数量" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

const inboundTypeChartRef = ref()
const outboundTypeChartRef = ref()
const trendChartRef = ref()
const categoryChartRef = ref()

const topInboundItems = ref([])
const topOutboundItems = ref([])

const fetchData = async () => {
  try {
    const [inboundTypeRes, outboundTypeRes, trendRes, categoryRes, topInRes, topOutRes] = await Promise.all([
      api.get('/statistics/inbound-type'),
      api.get('/statistics/outbound-type'),
      api.get('/statistics/trend?days=30'),
      api.get('/statistics/category'),
      api.get('/statistics/top-items?type=inbound&limit=10'),
      api.get('/statistics/top-items?type=outbound&limit=10')
    ])
    
    topInboundItems.value = topInRes
    topOutboundItems.value = topOutRes
    
    initCharts(inboundTypeRes, outboundTypeRes, trendRes, categoryRes)
  } catch (error) {
    console.error(error)
  }
}

const initCharts = (inboundType, outboundType, trend, category) => {
  const inboundTypeChart = echarts.init(inboundTypeChartRef.value)
  const outboundTypeChart = echarts.init(outboundTypeChartRef.value)
  const trendChart = echarts.init(trendChartRef.value)
  const categoryChart = echarts.init(categoryChartRef.value)
  
  const typeLabels = {
    purchase: '采购入库',
    return: '退货入库',
    transfer: '调拨入库',
    other: '其他入库',
    sale: '销售出库',
    requisition: '领用出库',
    transfer: '调拨出库'
  }
  
  const inboundTypeOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '50%',
      data: inboundType.map(item => ({
        name: typeLabels[item.type] || item.type,
        value: item.total_quantity
      }))
    }]
  }
  
  const outboundTypeOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '50%',
      data: outboundType.map(item => ({
        name: typeLabels[item.type] || item.type,
        value: item.total_quantity
      }))
    }]
  }
  
  const trendOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['入库', '出库'] },
    xAxis: {
      type: 'category',
      data: trend.map(item => item.date.slice(5))
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '入库',
        type: 'line',
        data: trend.map(item => item.inbound),
        smooth: true,
        itemStyle: { color: '#67c23a' },
        areaStyle: { opacity: 0.3 }
      },
      {
        name: '出库',
        type: 'line',
        data: trend.map(item => item.outbound),
        smooth: true,
        itemStyle: { color: '#409eff' },
        areaStyle: { opacity: 0.3 }
      }
    ]
  }
  
  const categoryOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: category.map(item => ({
        name: item.category,
        value: item.total_value
      }))
    }]
  }
  
  inboundTypeChart.setOption(inboundTypeOption)
  outboundTypeChart.setOption(outboundTypeOption)
  trendChart.setOption(trendOption)
  categoryChart.setOption(categoryOption)
  
  window.addEventListener('resize', () => {
    inboundTypeChart.resize()
    outboundTypeChart.resize()
    trendChart.resize()
    categoryChart.resize()
  })
}

onMounted(() => {
  fetchData()
})
</script>
