<template>
  <div class="accounting-page">
    <h2 class="page-title">记账管理</h2>

    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="8" :sm="6" :md="4">
        <el-card class="stat-card income" shadow="hover">
          <div class="stat-label">本月收入</div>
          <div class="stat-value">¥{{ summary.income.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :xs="8" :sm="6" :md="4">
        <el-card class="stat-card expense" shadow="hover">
          <div class="stat-label">本月支出</div>
          <div class="stat-value">¥{{ summary.expense.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :xs="8" :sm="6" :md="4">
        <el-card class="stat-card balance" shadow="hover">
          <div class="stat-label">本月结余</div>
          <div class="stat-value" :class="summary.balance >= 0 ? 'positive' : 'negative'">
            ¥{{ summary.balance.toFixed(2) }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="main-section">
      <el-col :md="6" :sm="24">
        <el-card>
          <template #header>
            <span>{{ editingId ? '编辑记录' : '新增记录' }}</span>
          </template>
          <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
            <el-form-item label="日期" prop="record_date">
              <el-date-picker
                v-model="form.record_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item label="类型" prop="type">
              <el-radio-group v-model="form.type">
                <el-radio-button value="expense">支出</el-radio-button>
                <el-radio-button value="income">收入</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="项目" prop="category">
              <el-input
                v-model="form.category"
                type="textarea"
                :rows="3"
                placeholder="请输入项目名称"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
            <el-form-item label="子分类">
              <el-input v-model="form.sub_category" placeholder="选填" />
            </el-form-item>
            <el-form-item label="金额" prop="amount">
              <el-input-number
                v-model="form.amount"
                :precision="2"
                :step="1"
                :min="0"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
            <el-form-item label="账户">
              <el-input v-model="form.account" placeholder="选填，如微信、支付宝" />
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="form.note" type="textarea" :rows="2" placeholder="选填" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" style="width: 100%" @click="handleSubmit" :loading="submitting">
                {{ editingId ? '保存修改' : '添加' }}
              </el-button>
              <el-button v-if="editingId" style="width: 100%" @click="resetForm">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :md="18" :sm="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>账单列表</span>
              <div class="header-actions">
                <el-button type="primary" @click="downloadTemplate">下载模板</el-button>
                <el-upload
                  :show-file-list="false"
                  :before-upload="handleBeforeUpload"
                  :http-request="handleImport"
                  accept=".xlsx,.xls"
                >
                  <el-button type="success">导入 Excel</el-button>
                </el-upload>
                <el-dropdown @command="handleExport">
                  <el-button type="warning">
                    导出<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="xlsx">导出 Excel</el-dropdown-item>
                      <el-dropdown-item command="csv">导出 CSV</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-button type="danger" @click="handleClearAll">清空全部</el-button>
              </div>
            </div>
          </template>

          <div class="filter-bar">
            <el-form :inline="true" :model="filters">
              <el-form-item label="月份">
                <el-date-picker
                  v-model="filters.month"
                  type="month"
                  placeholder="选择月份"
                  value-format="YYYY-MM"
                  @change="loadRecords"
                />
              </el-form-item>
              <el-form-item label="类型">
                <el-select v-model="filters.type" placeholder="全部" clearable style="width: 120px" @change="loadRecords">
                  <el-option label="收入" value="income" />
                  <el-option label="支出" value="expense" />
                </el-select>
              </el-form-item>
              <el-form-item label="关键词">
                <el-input
                  v-model="filters.keyword"
                  placeholder="搜索项目/账户/备注"
                  clearable
                  style="width: 200px"
                  @clear="loadRecords"
                  @keyup.enter="loadRecords"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadRecords">搜索</el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table :data="records" style="width: 100%" v-loading="loading">
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
            <el-table-column prop="category" label="项目" min-width="140" show-overflow-tooltip />
            <el-table-column prop="sub_category" label="子分类" width="100" show-overflow-tooltip />
            <el-table-column prop="account" label="账户" width="100" show-overflow-tooltip />
            <el-table-column prop="note" label="备注" min-width="120" show-overflow-tooltip />
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="editRecord(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="deleteRecord(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>

          <div class="category-summary">
            <h3>分类汇总</h3>
            <el-row :gutter="12">
              <el-col v-for="cat in summary.categories" :key="cat.category + cat.type" :sm="8" :md="6" :lg="4">
                <div class="cat-item">
                  <div class="cat-name">
                    <el-tag :type="cat.type === 'income' ? 'success' : 'danger'" size="small">
                      {{ cat.type === 'income' ? '收' : '支' }}
                    </el-tag>
                    <span class="text-ellipsis">{{ cat.category }}</span>
                  </div>
                  <div class="cat-amount" :class="cat.type === 'income' ? 'income-text' : 'expense-text'">
                    ¥{{ cat.total.toFixed(2) }}
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <ImportExcelDialog v-model:visible="importVisible" @success="handleImportSuccess" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { recordApi, RecordData, SummaryResponse } from '@/api/records'
import ImportExcelDialog from '@/components/ImportExcelDialog.vue'

const loading = ref(false)
const submitting = ref(false)
const records = ref<RecordData[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const editingId = ref<number | null>(null)
const importVisible = ref(false)

const summary = ref<SummaryResponse>({
  income: 0,
  expense: 0,
  balance: 0,
  categories: [],
})

const filters = reactive({
  month: getCurrentMonth(),
  type: '',
  keyword: '',
})

const formRef = ref<FormInstance>()
const form = reactive<RecordData>({
  record_date: getToday(),
  type: 'expense',
  category: '',
  sub_category: '',
  amount: 0,
  account: '',
  note: '',
})

const rules = {
  record_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  category: [{ required: true, message: '请输入项目', trigger: 'blur' }],
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于 0', trigger: 'blur' },
  ],
}

function getToday(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function getCurrentMonth(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

async function loadRecords() {
  loading.value = true
  try {
    const data = await recordApi.list({
      month: filters.month,
      type: filters.type,
      keyword: filters.keyword,
      page: page.value,
      page_size: pageSize.value,
    })
    records.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function loadSummary() {
  try {
    const data = await recordApi.summary({
      month: filters.month,
      type: filters.type,
      keyword: filters.keyword,
    })
    summary.value = data
  } catch (e) {}
}

function handlePageChange(p: number) {
  page.value = p
  loadRecords()
}

function handleSizeChange(s: number) {
  pageSize.value = s
  page.value = 1
  loadRecords()
}

function resetForm() {
  editingId.value = null
  form.record_date = getToday()
  form.type = 'expense'
  form.category = ''
  form.sub_category = ''
  form.amount = 0
  form.account = ''
  form.note = ''
  formRef.value?.resetFields()
}

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    if (editingId.value) {
      await recordApi.update(editingId.value, form)
      ElMessage.success('修改成功')
    } else {
      await recordApi.create(form)
      ElMessage.success('添加成功')
    }
    resetForm()
    loadRecords()
    loadSummary()
  } finally {
    submitting.value = false
  }
}

function editRecord(row: RecordData) {
  editingId.value = row.id || null
  form.record_date = row.record_date
  form.type = row.type
  form.category = row.category
  form.sub_category = row.sub_category || ''
  form.amount = row.amount
  form.account = row.account || ''
  form.note = row.note || ''
}

async function deleteRecord(row: RecordData) {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await recordApi.delete(row.id!)
    ElMessage.success('删除成功')
    loadRecords()
    loadSummary()
  } catch {
  }
}

async function handleClearAll() {
  try {
    await ElMessageBox.confirm('确定要清空所有记账记录吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定清空',
      cancelButtonText: '取消',
      type: 'error',
    })
    await recordApi.clearAll()
    ElMessage.success('已清空所有记录')
    loadRecords()
    loadSummary()
  } catch {
  }
}

async function handleExport(format: string) {
  try {
    const blob = await recordApi.export(format as 'xlsx' | 'csv', {
      month: filters.month,
      type: filters.type,
      keyword: filters.keyword,
    }) as any
    const url = window.URL.createObjectURL(new Blob([blob]))
    const a = document.createElement('a')
    a.href = url
    a.download = `records.${format}`
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

async function downloadTemplate() {
  try {
    const blob = await recordApi.importTemplate() as any
    const url = window.URL.createObjectURL(new Blob([blob]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'import_template.xlsx'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载模板失败')
  }
}

function handleBeforeUpload(file: File) {
  if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
    ElMessage.error('请上传 xlsx 格式的 Excel 文件')
    return false
  }
  importVisible.value = true
  return false
}

async function handleImport(options: any) {
}

function handleImportSuccess() {
  importVisible.value = false
  loadRecords()
  loadSummary()
}

onMounted(() => {
  loadRecords()
  loadSummary()
})
</script>

<style lang="scss" scoped>
.accounting-page {
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

  .main-section {
    .filter-bar {
      margin-bottom: 16px;
      padding: 12px;
      background: #fafafa;
      border-radius: 4px;
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: bold;

    .header-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
  }

  .income-text { color: $success-color; font-weight: bold; }
  .expense-text { color: $danger-color; font-weight: bold; }

  .pagination {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }

  .category-summary {
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #eee;

    h3 {
      margin-bottom: 16px;
      font-size: 16px;
    }

    .cat-item {
      background: #fafafa;
      border-radius: 6px;
      padding: 10px 12px;
      margin-bottom: 10px;

      .cat-name {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;
        font-size: 13px;

        span {
          flex: 1;
        }
      }

      .cat-amount {
        font-size: 15px;
        font-weight: bold;
      }
    }
  }
}
</style>
