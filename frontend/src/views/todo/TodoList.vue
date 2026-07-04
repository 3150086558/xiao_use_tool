<template>
  <div class="todo-page">
    <h2 class="page-title">待办事项</h2>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>新增待办</span>
        </div>
      </template>
      <div class="add-bar">
        <el-input
          v-model="newTodo.title"
          placeholder="输入待办事项，按回车添加"
          size="large"
          style="flex: 1; margin-right: 10px;"
          @keyup.enter="addTodo"
        />
        <el-select v-model="newTodo.priority" size="large" style="width: 100px; margin-right: 10px;">
          <el-option :value="0" label="普通" />
          <el-option :value="1" label="重要" />
          <el-option :value="2" label="紧急" />
        </el-select>
        <el-date-picker
          v-model="newTodo.due_date"
          type="date"
          placeholder="截止日期"
          size="large"
          style="width: 160px; margin-right: 10px;"
          value-format="YYYY-MM-DD"
        />
        <el-button type="primary" size="large" @click="addTodo">添加</el-button>
      </div>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>待办列表</span>
          <el-radio-group v-model="filterStatus" size="small">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="active">进行中</el-radio-button>
            <el-radio-button value="completed">已完成</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table :data="filteredTodos" style="width: 100%">
        <el-table-column width="60">
          <template #default="{ row }">
            <el-checkbox
              :model-value="row.completed"
              @change="toggleTodo(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="事项">
          <template #default="{ row }">
            <span :class="{ completed: row.completed }">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.priority === 2" type="danger" size="small">紧急</el-tag>
            <el-tag v-else-if="row.priority === 1" type="warning" size="small">重要</el-tag>
            <el-tag v-else size="small" type="info">普通</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="140" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editTodo(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteTodo(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="filteredTodos.length === 0" description="暂无待办事项" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { todoApi, TodoData } from '@/api/todos'

const todos = ref<TodoData[]>([])
const filterStatus = ref<'all' | 'active' | 'completed'>('all')

const newTodo = reactive({
  title: '',
  priority: 0,
  due_date: '',
})

const filteredTodos = computed(() => {
  if (filterStatus.value === 'active') {
    return todos.value.filter(t => !t.completed)
  }
  if (filterStatus.value === 'completed') {
    return todos.value.filter(t => t.completed)
  }
  return todos.value
})

async function loadTodos() {
  try {
    todos.value = await todoApi.list()
  } catch (e) {}
}

async function addTodo() {
  if (!newTodo.title.trim()) {
    ElMessage.warning('请输入待办内容')
    return
  }
  try {
    await todoApi.create({
      title: newTodo.title.trim(),
      priority: newTodo.priority,
      due_date: newTodo.due_date || undefined,
    })
    newTodo.title = ''
    newTodo.priority = 0
    newTodo.due_date = ''
    ElMessage.success('添加成功')
    loadTodos()
  } catch (e) {}
}

async function toggleTodo(row: TodoData) {
  try {
    await todoApi.update(row.id!, { completed: !row.completed })
    loadTodos()
  } catch (e) {}
}

async function editTodo(row: TodoData) {
  try {
    const { value } = await ElMessageBox.prompt('编辑待办', '修改内容', {
      inputValue: row.title,
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValidator: (val) => !!val?.trim() || '内容不能为空',
    })
    await todoApi.update(row.id!, { title: value.trim() })
    ElMessage.success('修改成功')
    loadTodos()
  } catch {
    // 用户取消
  }
}

async function deleteTodo(row: TodoData) {
  try {
    await ElMessageBox.confirm('确定要删除这条待办吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await todoApi.delete(row.id!)
    ElMessage.success('删除成功')
    loadTodos()
  } catch {}
}

onMounted(() => {
  loadTodos()
})
</script>

<style lang="scss" scoped>
.todo-page {
  .page-title {
    margin-bottom: 20px;
    font-size: 22px;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: bold;
  }

  .add-bar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 4px;
  }

  .completed {
    text-decoration: line-through;
    color: #909399;
  }
}
</style>
