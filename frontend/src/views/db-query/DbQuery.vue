<template>
  <div class="db-query-page">
    <h2 class="page-title">数据库查询</h2>

    <el-row :gutter="20">
      <el-col :md="6" :sm="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>已保存连接</span>
              <el-button type="primary" size="small" @click="showAddForm = true">+ 新建</el-button>
            </div>
          </template>
          <div class="conn-list">
            <div
              v-for="conn in connections"
              :key="conn.id"
              class="conn-item"
              :class="{ active: selectedConn?.id === conn.id }"
              @click="selectConnection(conn)"
            >
              <div class="conn-name text-ellipsis">{{ conn.name }}</div>
              <div class="conn-type">
                <el-tag size="small">{{ conn.db_type }}</el-tag>
              </div>
              <div class="conn-actions">
                <el-button type="primary" link size="small" @click.stop="editConnection(conn)">编辑</el-button>
                <el-button type="danger" link size="small" @click.stop="deleteConnection(conn)">删除</el-button>
              </div>
            </div>
            <el-empty v-if="connections.length === 0" description="暂无连接" :image-size="60" />
          </div>
        </el-card>

        <el-card v-if="showAddForm || editingConn" style="margin-top: 20px;">
          <template #header>
            <span>{{ editingConn ? '编辑连接' : '新建连接' }}</span>
          </template>
          <el-form :model="connForm" label-position="top" size="small">
            <el-form-item label="连接名称">
              <el-input v-model="connForm.name" />
            </el-form-item>
            <el-form-item label="数据库类型">
              <el-select v-model="connForm.db_type" style="width: 100%;">
                <el-option label="PostgreSQL" value="postgres" />
                <el-option label="MySQL" value="mysql" />
                <el-option label="SQLite" value="sqlite" />
              </el-select>
            </el-form-item>
            <template v-if="connForm.db_type !== 'sqlite'">
              <el-form-item label="主机">
                <el-input v-model="connForm.host" />
              </el-form-item>
              <el-form-item label="端口">
                <el-input-number v-model="connForm.port" :min="0" :max="65535" style="width: 100%;" />
              </el-form-item>
            </template>
            <el-form-item v-else label="SQLite 文件路径">
              <el-input v-model="connForm.sqlite_path" placeholder="/path/to/db.sqlite" />
            </el-form-item>
            <el-form-item label="用户名">
              <el-input v-model="connForm.username" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="connForm.password" type="password" show-password />
            </el-form-item>
            <el-form-item label="数据库名">
              <el-input v-model="connForm.database" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" style="width: 100%;" @click="saveConnection">保存</el-button>
              <el-button style="width: 100%;" @click="cancelEdit">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :md="18" :sm="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据库操作</span>
              <div class="actions">
                <el-button size="small" @click="testConnection" :disabled="!hasConnection">测试连接</el-button>
                <el-button size="small" @click="loadTables" :disabled="!hasConnection">获取表列表</el-button>
              </div>
            </div>
          </template>

          <el-row :gutter="16">
            <el-col :md="6" :sm="24">
              <div class="table-list">
                <div class="list-title">表列表</div>
                <div
                  v-for="table in tables"
                  :key="table"
                  class="table-item"
                  :class="{ active: selectedTable === table }"
                  @click="selectTable(table)"
                >
                  <el-icon><Document /></el-icon>
                  <span class="text-ellipsis">{{ table }}</span>
                </div>
                <el-empty v-if="tables.length === 0" description="暂无表" :image-size="50" />
              </div>
            </el-col>
            <el-col :md="18" :sm="24">
              <div v-if="tableSchema.length > 0" class="schema-section">
                <h4>表结构：{{ selectedTable }}</h4>
                <el-table :data="tableSchema" size="small" border>
                  <el-table-column prop="name" label="字段名" width="160" />
                  <el-table-column prop="type" label="类型" width="160" />
                  <el-table-column prop="nullable" label="可空" width="80">
                    <template #default="{ row }">{{ row.nullable ? '是' : '否' }}</template>
                  </el-table-column>
                  <el-table-column prop="default" label="默认值" />
                </el-table>
              </div>

              <div class="sql-section">
                <h4>SQL 查询</h4>
                <el-input
                  v-model="sqlText"
                  type="textarea"
                  :rows="5"
                  placeholder="SELECT * FROM table_name LIMIT 10;"
                  @keyup.ctrl.enter="executeQuery"
                />
                <div class="sql-tip">提示：仅支持 SELECT / SHOW / DESCRIBE / EXPLAIN 等查询语句</div>
                <el-button type="primary" :disabled="!hasConnection" @click="executeQuery">
                  执行查询 (Ctrl+Enter)
                </el-button>
              </div>

              <div v-if="queryResult" class="result-section">
                <h4>查询结果（{{ queryResult.count }} 行）</h4>
                <el-table :data="queryResult.rows || []" size="small" border max-height="300">
                  <el-table-column
                    v-for="col in queryResult.columns || []"
                    :key="col"
                    :prop="col"
                    :label="col"
                    min-width="100"
                    show-overflow-tooltip
                  />
                </el-table>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dbQueryApi, DbConnectionData, DbQueryResult } from '@/api/db-query'

const connections = ref<DbConnectionData[]>([])
const selectedConn = ref<DbConnectionData | null>(null)
const showAddForm = ref(false)
const editingConn = ref<DbConnectionData | null>(null)

const connForm = reactive<DbConnectionData>({
  name: '',
  db_type: 'postgres',
  host: '127.0.0.1',
  port: 5432,
  username: '',
  password: '',
  database: '',
  sqlite_path: '',
})

const tables = ref<string[]>([])
const selectedTable = ref('')
const tableSchema = ref<any[]>([])
const sqlText = ref('')
const queryResult = ref<DbQueryResult | null>(null)

const hasConnection = computed(() => !!selectedConn.value)

async function loadConnections() {
  try {
    connections.value = await dbQueryApi.listConnections()
  } catch (e) {}
}

function selectConnection(conn: DbConnectionData) {
  selectedConn.value = conn
  tables.value = []
  selectedTable.value = ''
  tableSchema.value = []
  queryResult.value = null
}

function editConnection(conn: DbConnectionData) {
  editingConn.value = conn
  connForm.name = conn.name
  connForm.db_type = conn.db_type
  connForm.host = conn.host
  connForm.port = conn.port
  connForm.username = conn.username
  connForm.password = conn.password === '******' ? '' : conn.password
  connForm.database = conn.database
  connForm.sqlite_path = conn.sqlite_path
  showAddForm.value = false
}

async function saveConnection() {
  if (!connForm.name.trim()) {
    ElMessage.warning('请输入连接名称')
    return
  }
  try {
    if (editingConn.value) {
      await dbQueryApi.updateConnection(editingConn.value.id!, connForm)
      ElMessage.success('更新成功')
    } else {
      await dbQueryApi.createConnection(connForm)
      ElMessage.success('创建成功')
    }
    showAddForm.value = false
    editingConn.value = null
    loadConnections()
  } catch (e) {}
}

function cancelEdit() {
  showAddForm.value = false
  editingConn.value = null
}

async function deleteConnection(conn: DbConnectionData) {
  try {
    await ElMessageBox.confirm('确定要删除这个连接吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await dbQueryApi.deleteConnection(conn.id!)
    ElMessage.success('删除成功')
    if (selectedConn.value?.id === conn.id) {
      selectedConn.value = null
    }
    loadConnections()
  } catch {}
}

function getActiveConfig(): DbConnectionData {
  return {
    ...(selectedConn.value || connForm),
  }
}

async function testConnection() {
  if (!selectedConn.value) {
    ElMessage.warning('请先选择或创建一个连接')
    return
  }
  try {
    const result = await dbQueryApi.query('connect', getActiveConfig())
    ElMessage.success(result.message || '连接成功')
  } catch (e) {}
}

async function loadTables() {
  if (!selectedConn.value) return
  try {
    const result = await dbQueryApi.query('tables', getActiveConfig())
    tables.value = result.tables || []
    selectedTable.value = ''
    tableSchema.value = []
  } catch (e) {}
}

async function selectTable(table: string) {
  selectedTable.value = table
  try {
    const result = await dbQueryApi.query('schema', getActiveConfig(), table)
    tableSchema.value = result.columns_info || []
    sqlText.value = `SELECT * FROM "${table}" LIMIT 100;`
  } catch (e) {}
}

async function executeQuery() {
  if (!sqlText.value.trim() || !selectedConn.value) return
  try {
    const result = await dbQueryApi.query('query', getActiveConfig(), undefined, sqlText.value)
    queryResult.value = result
  } catch (e) {}
}

onMounted(() => {
  loadConnections()
})
</script>

<style lang="scss" scoped>
.db-query-page {
  .page-title {
    margin-bottom: 20px;
    font-size: 22px;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: bold;

    .actions {
      display: flex;
      gap: 8px;
    }
  }

  .conn-list {
    .conn-item {
      padding: 10px 12px;
      border: 1px solid #eee;
      border-radius: 4px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        border-color: $primary-color;
      }

      &.active {
        border-color: $primary-color;
        background: #ecf5ff;
      }

      .conn-name {
        font-weight: bold;
        margin-bottom: 4px;
      }

      .conn-type {
        margin-bottom: 6px;
      }

      .conn-actions {
        display: flex;
        gap: 8px;
      }
    }
  }

  .table-list {
    border-right: 1px solid #eee;
    padding-right: 12px;
    min-height: 300px;

    .list-title {
      font-weight: bold;
      margin-bottom: 10px;
    }

    .table-item {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 8px;
      cursor: pointer;
      border-radius: 4px;
      font-size: 13px;

      &:hover {
        background: #f5f7fa;
      }

      &.active {
        background: #ecf5ff;
        color: $primary-color;
      }
    }
  }

  .schema-section {
    margin-bottom: 20px;

    h4 {
      margin-bottom: 10px;
      font-size: 15px;
    }
  }

  .sql-section {
    margin-bottom: 20px;

    h4 {
      margin-bottom: 10px;
      font-size: 15px;
    }

    .sql-tip {
      font-size: 12px;
      color: $text-secondary;
      margin: 6px 0 10px;
    }
  }

  .result-section {
    h4 {
      margin-bottom: 10px;
      font-size: 15px;
    }
  }
}
</style>
