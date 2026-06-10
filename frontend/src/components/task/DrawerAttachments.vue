<template>
  <div class="attachments-tab">
    <div class="upload-area">
      <label class="btn btn-sm btn-primary upload-btn" :class="{ 'upload-btn--disabled': uploading }">
        <span v-if="uploading" class="ai-spinner" />
        <font-awesome-icon v-else :icon="['fas', 'upload']" />
        {{ uploading ? 'Uploading…' : 'Upload file' }}
        <input type="file" class="upload-input" @change="handleUpload" :disabled="uploading" />
      </label>
    </div>

    <div v-if="store.loading" class="feed-empty">Loading attachments…</div>

    <div v-else-if="store.items.length === 0" class="empty-state">
      <div class="empty-state-glyph">
        <font-awesome-icon :icon="['fas', 'paperclip']" />
      </div>
      <div class="empty-state-title">No attachments yet</div>
      <div class="empty-state-hint">Share context with your team — upload specs, screenshots, or related files.</div>
    </div>

    <div v-else class="attachment-list">
      <div v-for="att in store.items" :key="att.id" class="attachment-row">
        <a v-if="att.mime_type.startsWith('image/')" :href="att.url" target="_blank" class="att-thumb">
          <img :src="att.url" :alt="att.original_filename" loading="lazy" />
        </a>
        <div v-else class="att-icon">
          <font-awesome-icon :icon="['fas', fileIcon(att.mime_type)]" />
        </div>
        <div class="att-info">
          <a :href="att.url" target="_blank" class="att-name">{{ att.original_filename }}</a>
          <div class="att-meta">
            {{ store.formatSize(att.file_size) }}
            <span v-if="att.uploader_name"> · {{ att.uploader_name }}</span>
          </div>
        </div>
        <button
          class="icon-btn icon-btn--danger"
          :aria-label="`Delete ${att.original_filename}`"
          @click="handleDelete(att)"
        >
          <font-awesome-icon :icon="['fas', 'trash-can']" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { TaskAttachment } from '../../types'
import { useAttachmentStore } from '../../stores/attachments'
import { useConfirm } from '../../composables/useConfirm'
import { useToast } from '../../composables/useToast'

const props = defineProps<{ taskId: number }>()
const store = useAttachmentStore()
const { confirm } = useConfirm()
const toast = useToast()
const uploading = ref(false)

onMounted(() => store.fetchByTask(props.taskId))

function fileIcon(mime: string): string {
  if (mime.startsWith('image/')) return 'image'
  if (mime.startsWith('video/')) return 'video'
  if (mime.startsWith('audio/')) return 'music'
  if (mime.includes('pdf')) return 'file-pdf'
  if (mime.includes('word') || mime.includes('document')) return 'file-word'
  if (mime.includes('spreadsheet') || mime.includes('excel') || mime.includes('csv')) return 'file-excel'
  if (mime.includes('zip') || mime.includes('tar') || mime.includes('rar') || mime.includes('7z')) return 'file-zipper'
  return 'file'
}

async function handleUpload(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    await store.upload(props.taskId, file)
    toast.success(`Uploaded "${file.name}"`)
  } catch (err: any) {
    toast.error(err?.message || `Failed to upload "${file.name}"`, {
      actionLabel: 'Retry',
      onAction: () => retryUpload(file),
    })
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function retryUpload(file: File) {
  uploading.value = true
  try {
    await store.upload(props.taskId, file)
    toast.success(`Uploaded "${file.name}"`)
  } catch (err: any) {
    toast.error(err?.message || `Failed to upload "${file.name}"`)
  } finally {
    uploading.value = false
  }
}

async function handleDelete(att: TaskAttachment) {
  const ok = await confirm({
    title: 'Delete attachment?',
    message: `"${att.original_filename}" will be permanently removed from this task.`,
    confirmLabel: 'Delete',
    danger: true,
  })
  if (!ok) return
  try {
    await store.remove(props.taskId, att.id)
    toast.success('Attachment deleted')
  } catch (err: any) {
    toast.error(err?.message || 'Failed to delete attachment')
  }
}
</script>

<style scoped>
.attachments-tab { padding: 16px 0; }
.upload-area { margin-bottom: 16px; }
.upload-btn { position: relative; overflow: hidden; }
.upload-btn--disabled { opacity: 0.6; pointer-events: none; }
.upload-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.attachment-list { display: flex; flex-direction: column; gap: 8px; }
.attachment-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 10px;
  background: var(--bg);
  border: 1px solid var(--border);
}

.att-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 18px;
  flex-shrink: 0;
}
.att-thumb {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  border: 1px solid var(--border);
  display: block;
}
.att-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }

.att-info { flex: 1; min-width: 0; }
.att-name {
  display: block;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text);
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.att-name:hover { color: var(--primary); text-decoration: underline; }
.att-meta { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

.feed-empty { text-align: center; padding: 32px 0; color: var(--text-muted); font-size: 13.5px; }
</style>
