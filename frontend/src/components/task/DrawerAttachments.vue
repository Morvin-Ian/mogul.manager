<template>
  <div class="attachments-tab">
    <div class="upload-area">
      <label class="upload-btn" :class="{ 'upload-btn--disabled': uploading }">
        <font-awesome-icon :icon="['fas', 'upload']" />
        {{ uploading ? 'Uploading…' : 'Upload file' }}
        <input type="file" class="upload-input" @change="handleUpload" :disabled="uploading" />
      </label>
    </div>

    <div v-if="store.loading" class="feed-empty">Loading attachments…</div>
    <div v-else-if="store.items.length === 0" class="feed-empty">No attachments yet.</div>

    <div v-else class="attachment-list">
      <div v-for="att in store.items" :key="att.id" class="attachment-row">
        <div class="att-icon">
          <font-awesome-icon :icon="['fas', fileIcon(att.mime_type)]" />
        </div>
        <div class="att-info">
          <a :href="att.url" target="_blank" class="att-name">{{ att.original_filename }}</a>
          <div class="att-meta">
            {{ store.formatSize(att.file_size) }}
            <span v-if="att.uploader_name"> · {{ att.uploader_name }}</span>
          </div>
        </div>
        <button class="att-delete" title="Delete" @click="handleDelete(att)">
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

const props = defineProps<{ taskId: number }>()
const store = useAttachmentStore()
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
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function handleDelete(att: TaskAttachment) {
  if (!confirm(`Delete "${att.original_filename}"?`)) return
  await store.remove(props.taskId, att.id)
}
</script>

<style scoped>
.attachments-tab { padding: 1rem 0; }
.upload-area { margin-bottom: 1rem; }
.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--accent);
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: opacity 0.2s;
}
.upload-btn:hover { opacity: 0.85; }
.upload-btn--disabled { opacity: 0.5; pointer-events: none; }
.upload-input { display: none; }
.attachment-list { display: flex; flex-direction: column; gap: 0.5rem; }
.attachment-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  background: var(--surface2);
}
.att-icon {
  width: 2rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 1.25rem;
}
.att-info { flex: 1; min-width: 0; }
.att-name {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text);
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.att-name:hover { color: var(--accent); text-decoration: underline; }
.att-meta { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.125rem; }
.att-delete {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  font-size: 0.875rem;
}
.att-delete:hover { color: var(--danger, #e74c3c); background: var(--surface3); }
.feed-empty { text-align: center; padding: 2rem 0; color: var(--text-muted); font-size: 0.875rem; }
</style>
