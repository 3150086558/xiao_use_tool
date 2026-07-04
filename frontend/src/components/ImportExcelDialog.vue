<template>
  <el-dialog
    v-model="dialogVisible"
    title="导入 Excel"
    width="500px"
    :close-on-click-modal="false"
  >
    <div class="import-dialog">
      <div class="tip">
        <el-icon><InfoFilled /></el-icon>
        请先 <el-button type="primary" link @click="downloadTemplate">下载导入模板</el-button>，按模板格式填写后上传
      </div>

      <el-upload
        class="upload-area"
        drag
        :show-file-list="false"
        :before-upload="beforeUpload"
        :http-request="handleUpload"
        accept=".xlsx,.xls"
        :disabled="importing"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将 Excel 文件拖到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">仅支持 .xlsx / .xls 格式，不超过 10MB</div>
        </template>
      </el-upload>

      <div v-if="importing" class="progress-section">
        <div class="progress-label">导入中... {{ progress }}%</div>
        <el-progress :percentage="progress" :status="progress < 100 ? '' : 'success'" />
      </div>

      <div v-if="result" class="result-section">
        <el-alert
          :title="`导入完成：成功 ${result.success} 条，失败 ${result.errors?.length || 0} 条`"
          :type="result.errors?.length ? 'warning' : 'success'"
          :closable="false"
        />
        <div v-if="result.errors && result.errors.length > 0" class="error-list">
          <div class="error-title">错误详情：</div>
          <ul>
            <li v-for="(err, idx) in result.errors" :key="idx">{{ err }}</li>
          </ul>
        </div>
      </div>
    </div>
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, UploadFilled } from '@element-plus/icons-vue'
import { recordApi } from '@/api/records'

const props = defineProps<{
  visible: boolean
}>()
const emit = defineEmits(['update:visible', 'success'])

const importing = ref(false)
const progress = ref(0)
const result = ref<{ success: number; errors: string[]; total: number } | null>(null)
const dialogVisible = ref(props.visible)

watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    progress.value = 0
    result.value = null
    importing.value = false
  }
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

function beforeUpload(file: File) {
  if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
    ElMessage.error('请上传 xlsx / xls 格式的文件')
    return false
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  return true
}

async function handleUpload(options: any) {
  const file = options.file as File
  importing.value = true
  progress.value = 0
  result.value = null

  const interval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += Math.random() * 10
    }
  }, 300)

  try {
    const data = await recordApi.importExcel(file)
    progress.value = 100
    result.value = data
    if (data.success > 0) {
      ElMessage.success(`成功导入 ${data.success} 条记录`)
      emit('success')
    } else {
      ElMessage.warning('导入失败，请检查文件格式')
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
  } finally {
    clearInterval(interval)
    setTimeout(() => {
      progress.value = 100
    }, 100)
    importing.value = false
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
  } catch (e) {}
}

function handleClose() {
  dialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.import-dialog {
  .tip {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 10px 12px;
    background: #ecf5ff;
    border-radius: 4px;
    color: #409eff;
    font-size: 13px;
    margin-bottom: 20px;
  }

  .upload-area {
    margin-bottom: 20px;
  }

  .progress-section {
    margin-bottom: 16px;

    .progress-label {
      font-size: 13px;
      color: $text-secondary;
      margin-bottom: 6px;
    }
  }

  .result-section {
    margin-top: 16px;

    .error-list {
      margin-top: 12px;
      max-height: 200px;
      overflow-y: auto;
      background: #fef0f0;
      border-radius: 4px;
      padding: 10px 12px;

      .error-title {
        font-size: 13px;
        color: $danger-color;
        margin-bottom: 6px;
        font-weight: bold;
      }

      ul {
        margin: 0;
        padding-left: 20px;
        font-size: 12px;
        color: $danger-color;

        li {
          margin-bottom: 2px;
        }
      }
    }
  }
}
</style>
