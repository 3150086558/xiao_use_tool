<template>
  <div class="dashboard">
    <h2 class="page-title">仪表盘</h2>

    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="12" :sm="8" :md="6">
        <el-card class="stat-card income-card" shadow="hover">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <div class="stat-label">本月收入</div>
            <div class="stat-value">¥{{ summary.income.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <el-card class="stat-card expense-card" shadow="hover">
          <div class="stat-icon">💸</div>
          <div class="stat-info">
            <div class="stat-label">本月支出</div>
            <div class="stat-value">¥{{ summary.expense.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <el-card class="stat-card balance-card" shadow="hover">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-label">本月结余</div>
            <div class="stat-value" :class="summary.balance >= 0 ? 'positive' : 'negative'">
              ¥{{ summary.balance.toFixed(2) }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="6">
        <el-card class="stat-card todo-card" shadow="hover">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <div class="stat-label">待办事项</div>
            <div class="stat-value">{{ todoCount }} 项</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="dashboard-panels">
      <el-col :md="16" :sm="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近记账</span>
              <el-button type="primary" link @click="$router.push('/accounting')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentRecords" style="width: 100%" size="small">
            <el-table-column prop="record_date" label="日期" width="120" />
            <el-table-column label="类型" width="80">
              <template #default="{ row }">
                <el-tag :type="row.type === 'income' ? 'success' : 'danger'" size="small">
                  {{ row.type === 'income' ? '收入' : '支出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="120" align="right">
              <template #default="{ row }">
                <span :class="row.type === 'income' ? 'income-text' : 'expense-text'">
                  {{ row.type === 'income' ? '+' : '-' }}¥{{ row.amount }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="项目" min-width="100" show-overflow-tooltip />
            <el-table-column prop="note" label="备注" min-width="120" show-overflow-tooltip />
          </el-table>
          <el-empty v-if="recentRecords.length === 0" description="暂无记录" :image-size="80" />
        </el-card>
      </el-col>
      <el-col :md="8" :sm="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/accounting')" size="large" style="width: 100%; margin-bottom: 10px;">
              记一笔
            </el-button>
            <el-button type="success" @click="$router.push('/stats')" size="large" style="width: 100%; margin-bottom: 10px;">
              查看统计
            </el-button>
            <el-button type="warning" @click="$router.push('/todos')" size="large" style="width: 100%; margin-bottom: 10px;">
              待办事项
            </el-button>
            <el-button type="info" @click="$router.push('/notes')" size="large" style="width: 100%;">
              备忘录
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { recordApi, RecordData, SummaryResponse } from '@/api/records'
import { todoApi } from '@/api/todos'

const summary = ref<SummaryResponse>({
  income: 0,
  expense: 0,
  balance: 0,
  categories: [],
})
const recentRecords = ref<RecordData[]>([])
const todoCount = ref(0)

function getCurrentMonth(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

async function loadSummary() {
  try {
    const data = await recordApi.summary({ month: getCurrentMonth() })
    summary.value = data
  } catch (e) {}
}

async function loadRecentRecords() {
  try {
    const data = await recordApi.list({ page: 1, page_size: 5 })
    recentRecords.value = data.items
  } catch (e) {}
}

async function loadTodos() {
  try {
    const data = await todoApi.list()
    todoCount.value = data.filter(t => !t.completed).length
  } catch (e) {}
}

onMounted(() => {
  loadSummary()
  loadRecentRecords()
  loadTodos()
})
</script>

<style lang="scss" scoped>
.dashboard {
  .page-title {
    margin-bottom: 20px;
    font-size: 22px;
    color: $text-primary;
  }

  .stats-cards {
    margin-bottom: 20px;
  }

  .stat-card {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;

    .stat-icon {
      font-size: 40px;
    }

    .stat-info {
      flex: 1;

      .stat-label {
        font-size: 13px;
        color: $text-secondary;
        margin-bottom: 4px;
      }

      .stat-value {
        font-size: 22px;
        font-weight: bold;
        color: $text-primary;

        &.positive { color: $success-color; }
        &.negative { color: $danger-color; }
      }
    }
  }

  .income-text { color: $success-color; }
  .expense-text { color: $danger-color; }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: bold;
  }

  .dashboard-panels {
    .quick-actions {
      display: flex;
      flex-direction: column;
    }
  }
}
</style>
