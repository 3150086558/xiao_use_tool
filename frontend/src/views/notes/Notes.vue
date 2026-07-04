<template>
  <div class="notes-page">
    <h2 class="page-title">备忘录</h2>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>新建备忘录</span>
        </div>
      </template>
      <div class="add-bar">
        <el-input
          v-model="newNote.title"
          placeholder="标题"
          size="large"
          style="margin-right: 10px; width: 240px;"
        />
        <el-button type="primary" size="large" @click="addNote">新建</el-button>
      </div>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>备忘录列表</span>
          <el-input
            v-model="keyword"
            placeholder="搜索标题/内容"
            clearable
            style="width: 240px;"
            @clear="loadNotes"
            @keyup.enter="loadNotes"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>

      <div class="notes-grid">
        <el-card
          v-for="note in notes"
          :key="note.id"
          class="note-card"
          shadow="hover"
        >
          <div class="note-title text-ellipsis">{{ note.title }}</div>
          <div class="note-content">{{ note.content || '（无内容）' }}</div>
          <div class="note-footer">
            <span class="note-date">{{ formatDate(note.updated_at) }}</span>
            <div class="note-actions">
              <el-button type="primary" link size="small" @click="editNote(note)">编辑</el-button>
              <el-button type="danger" link size="small" @click="deleteNote(note)">删除</el-button>
            </div>
          </div>
        </el-card>
        <el-empty v-if="notes.length === 0" description="暂无备忘录" />
      </div>
    </el-card>

    <el-dialog v-model="editVisible" title="编辑备忘录" width="500px">
      <el-form :model="editForm" label-position="top">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="editForm.content" type="textarea" :rows="8" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { noteApi, NoteData } from '@/api/notes'

const notes = ref<NoteData[]>([])
const keyword = ref('')
const editVisible = ref(false)
const editingId = ref<number | null>(null)

const newNote = reactive({
  title: '',
})

const editForm = reactive({
  title: '',
  content: '',
})

async function loadNotes() {
  try {
    notes.value = await noteApi.list(keyword.value)
  } catch (e) {}
}

async function addNote() {
  if (!newNote.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  try {
    await noteApi.create({ title: newNote.title.trim() })
    newNote.title = ''
    ElMessage.success('创建成功')
    loadNotes()
  } catch (e) {}
}

function editNote(note: NoteData) {
  editingId.value = note.id || null
  editForm.title = note.title
  editForm.content = note.content
  editVisible.value = true
}

async function saveEdit() {
  if (!editingId.value || !editForm.title.trim()) {
    ElMessage.warning('标题不能为空')
    return
  }
  try {
    await noteApi.update(editingId.value, {
      title: editForm.title.trim(),
      content: editForm.content,
    })
    ElMessage.success('保存成功')
    editVisible.value = false
    loadNotes()
  } catch (e) {}
}

async function deleteNote(note: NoteData) {
  try {
    await ElMessageBox.confirm('确定要删除这条备忘录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await noteApi.delete(note.id!)
    ElMessage.success('删除成功')
    loadNotes()
  } catch {}
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  return dateStr.replace('T', ' ').substring(0, 16)
}

onMounted(() => {
  loadNotes()
})
</script>

<style lang="scss" scoped>
.notes-page {
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
  }

  .notes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }

  .note-card {
    display: flex;
    flex-direction: column;
    min-height: 180px;

    .note-title {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 8px;
      color: $text-primary;
    }

    .note-content {
      flex: 1;
      font-size: 13px;
      color: $text-secondary;
      line-height: 1.6;
      display: -webkit-box;
      -webkit-line-clamp: 5;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .note-footer {
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid #eee;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      color: $text-secondary;

      .note-actions {
        display: flex;
        gap: 8px;
      }
    }
  }
}
</style>
