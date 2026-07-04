<template>
  <div class="stats-page">
    <h2 class="page-title">统计报表</h2>

    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="8" :sm="6">
        <el-card class="stat-card income" shadow="hover">
          <div class="stat-label">总收入</div>
          <div class="stat-value">¥{{ summary.income.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :xs="8" :sm="6">
        <el-card class="stat-card expense" shadow="hover">
          <div class="stat-label">总支出</div>
          <div class="stat-value">¥{{ summary.expense.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :xs="8" :sm="6">
        <el-card class="stat-card balance" shadow="hover">
          <div class="stat-label">总结余</div>
          <div class="stat-value" :class="summary.balance >= 0 ? 'positive' : 'negative'">
            ¥{{ summary.balance.toFixed(2) }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :md="16" :sm="24">
        <el-card>
          <template #header><span>月度收支趋势</span></template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :md="8" :sm="24">
        <el-card>
          <template #header>
            <el-radio-group v-model="pieType" size="small">
              <el-radio-button value="expense">支出</el-radio-button>
              <el-radio-button value="income">收入</el-radio-button>
            </el-radio-group>
          </template>
          <div ref="pieChartRef" class="chart-container pie-chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header><span>分类排行</span></template>
          <el-row :gutter="20">
            <el-col :md="12" :sm="24">
              <h4 style="margin-bottom: 12px;">支出 TOP 10</h4>
              <div ref="barExpenseRef" class="bar-chart"></div>
            </el-col>
            <el-col :md="12" :sm="24">
              <h4 style="margin-bottom: 12px;">收入 TOP 10</h4>
              <div ref="barIncomeRef" class="bar-chart"></div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { recordApi, SummaryResponse, StatsResponse } from '@/api/records'

const summary = ref<SummaryResponse>({
  income: 0,
  expense: 0,
  balance: 0,
  categories: [],
})
const statsData = ref<StatsResponse>({
  monthly_trend: [],
  category_pie: [],
  top_categories: [],
})
const pieType = ref<'expense' | 'income'>('expense')

const trendChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
const barExpenseRef = ref<HTMLElement>()
const barIncomeRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null
let barExpenseChart: echarts.ECharts | null = null
let barIncomeChart: echarts.ECharts | null = null

async function loadData() {
  try {
    const [sum, stats] = await Promise.all([
      recordApi.summary({}),
      recordApi.stats(),
    ])
    summary.value = sum
    statsData.value = stats
    await nextTick()
    initCharts()
  } catch (e) {}
}

function initCharts() {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    const months = statsData.value.monthly_trend.map(d => d.month)
    const incomeData = statsData.value.monthly_trend.map(d => d.income)
    const expenseData = statsData.value.monthly_trend.map(d => d.expense)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['收入', '支出'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: months },
      yAxis: { type: 'value' },
      series: [
        { name: '收入', type: 'line', smooth: true, data: incomeData, itemStyle: { color: '#67c23a' }, areaStyle: { opacity: 0.1 } },
        { name: '支出', type: 'line', smooth: true, data: expenseData, itemStyle: { color: '#f56c6c' }, areaStyle: { opacity: 0.1 } },
      ],
    })
  }

  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
  }

  if (barExpenseRef.value) {
    barExpenseChart = echarts.init(barExpenseRef.value)
    const expenseCats = statsData.value.category_pie.filter(d => d.type === 'expense').slice(0, 10).reverse()
    barExpenseChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: expenseCats.map(d => d.category) },
      series: [
        { type: 'bar', data: expenseCats.map(d => d.total), itemStyle: { color: '#f56c6c' } },
      ],
    })
  }

  if (barIncomeRef.value) {
    barIncomeChart = echarts.init(barIncomeRef.value)
    const incomeCats = statsData.value.category_pie.filter(d => d.type === 'income').slice(0, 10).reverse()
    barIncomeChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: incomeCats.map(d => d.category) },
      series: [
        { type: 'bar', data: incomeCats.map(d => d.total), itemStyle: { color: '#67c23a' } },
      ],
    })
  }

  updatePieChart()
}

function updatePieChart() {
  if (!pieChart) return
  const data = statsData.value.category_pie
    .filter(d => d.type === pieType.value)
    .map(d => ({ name: d.category, value: d.total }))
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 16, fontWeight: 'bold' },
      },
      data,
    }],
    color: pieType.value === 'expense'
      ? ['#f56c6c', '#e6a23c', '#f0c78a', '#f7d88a', '#ffd591', '#ffd8bf', '#ffecd9', '#fff2e8', '#fff7e6', '#fffbe6']
      : ['#67c23a', '#85ce61', '#95d475', '#a7d98c', '#b3e19d', '#c2e7b0', '#d0edc2', '#dcf2d4', '#e7f6e1', '#f0faec'],
  })
}

watch(pieType, () => {
  updatePieChart()
})

function handleResize() {
  trendChart?.resize()
  pieChart?.resize()
  barExpenseChart?.resize()
  barIncomeChart?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.stats-page {
  .page-title {
    margin-bottom: 20px;
    font-size: 22px;
  }

  .stats-cards {
    margin-bottom: 20px;
  }

  .stat-card {
    text-align: center;
    margin-bottom: 16px;

    .stat-label {
      font-size: 13px;
      color: $text-secondary;
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 22px;
      font-weight: bold;

      &.positive { color: $success-color; }
      &.negative { color: $danger-color; }
    }

    &.income .stat-value { color: $success-color; }
    &.expense .stat-value { color: $danger-color; }
    &.balance .stat-value { color: $primary-color; }
  }

  .chart-container {
    width: 100%;
    height: 340px;
  }

  .pie-chart {
    height: 300px;
  }

  .bar-chart {
    height: 280px;
  }
}
</style>
