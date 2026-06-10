<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal upload-modal">
      <div class="modal-header">
        <h2>Upload Document</h2>
        <button class="modal-close" aria-label="Close dialog" @click="$emit('close')">×</button>
      </div>

      <div
        class="modal-dropzone"
        :class="{ 'modal-dropzone-over': modalDragging, 'has-file': !!pendingFile }"
        @dragover.prevent="modalDragging = true"
        @dragleave="modalDragging = false"
        @drop.prevent="handleModalDrop"
      >
        <template v-if="!pendingFile">
          <svg viewBox="0 0 24 24" fill="none" width="26" height="26">
            <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M12 4v12M8 8l4-4 4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p>Drop file here or <label class="browse-link">browse<input type="file" accept=".pdf,.docx,.txt,.csv" @change="handleModalFilePick" style="display:none"/></label></p>
          <p class="dropzone-hint">PDF · DOCX · TXT · CSV · max 20 MB</p>
        </template>
        <template v-else>
          <svg viewBox="0 0 24 24" fill="none" width="22" height="22">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
            <path d="M14 2v6h6M9 13l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p class="pending-file-name">{{ pendingFile.name }}</p>
          <button class="change-file-btn" @click="pendingFile = null">Change file</button>
        </template>
      </div>

      <div v-if="!lockedProjectId" class="modal-context-section">
        <p class="modal-context-label">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 5v6a1 1 0 001 1h8a1 1 0 001-1V5.5a1 1 0 00-1-1H7L5.5 3H3a1 1 0 00-1 2z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>
          Attach to (optional)
        </p>
        <p class="modal-context-hint">Scopes this file so the AI uses it only within the selected context.</p>
        <div class="modal-selectors">
          <div class="modal-select-group">
            <label>Workspace</label>
            <select v-model="workspaceId" @change="onWorkspaceChange">
              <option :value="null">None — global file</option>
              <option v-for="ws in workspaces" :key="ws.id" :value="ws.id">{{ ws.title }}</option>
            </select>
          </div>
          <div class="modal-select-group">
            <label>Project <span class="select-optional">(within workspace)</span></label>
            <select v-model="projectId" :disabled="!workspaceId">
              <option :value="null">{{ workspaceId ? 'Workspace-level' : 'Select a workspace first' }}</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
            </select>
          </div>
        </div>
      </div>

      <p v-if="error" class="form-error" style="margin: 0 24px;">{{ error }}</p>

      <div class="modal-footer">
        <button class="btn" @click="$emit('close')">Cancel</button>
        <button class="btn btn-primary upload-submit-btn" :disabled="!pendingFile || uploading" @click="submit">
          <span v-if="uploading" class="spinner spinner-white"></span>
          {{ uploading ? 'Uploading…' : 'Upload' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Project, Workspace } from '../../types'

const props = defineProps<{
  workspaces: Workspace[]
  projects: Project[]
  error: string | null
  uploading: boolean
  lockedProjectId?: number | null  // when set, skip selectors and use this project
}>()

const emit = defineEmits<{
  close: []
  upload: [file: File, ctx: { workspace_id?: number; project_id?: number }]
  workspaceChange: [id: number | null]
}>()

const pendingFile = ref<File | null>(null)
const modalDragging = ref(false)
const workspaceId = ref<number | null>(null)
const projectId = ref<number | null>(props.lockedProjectId ?? null)

function handleModalDrop(e: DragEvent) {
  modalDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) pendingFile.value = file
}

function handleModalFilePick(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) pendingFile.value = file
  ;(e.target as HTMLInputElement).value = ''
}

function onWorkspaceChange() {
  projectId.value = null
  emit('workspaceChange', workspaceId.value)
}

function submit() {
  if (!pendingFile.value) return
  const ctx = {
    workspace_id: workspaceId.value ?? undefined,
    project_id: projectId.value ?? undefined,
  }
  emit('upload', pendingFile.value, ctx)
}
</script>

<style scoped>
.upload-modal {
  width: 520px;
  max-width: calc(100vw - 32px);
}

.modal-dropzone {
  margin: 0 24px;
  border: 2px dashed var(--border);
  border-radius: var(--radius-lg);
  padding: 28px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--text-light);
  transition: border-color 0.15s, background 0.15s;
  text-align: center;
}
.modal-dropzone p { font-size: 13px; margin: 0; }
.modal-dropzone-over { border-color: var(--primary); background: var(--primary-light); color: var(--primary); }
.modal-dropzone.has-file { border-color: var(--success); background: var(--success-bg); color: var(--success); }

.browse-link {
  color: var(--primary);
  text-decoration: underline;
  cursor: pointer;
  font-weight: 600;
}

.pending-file-name {
  font-size: 13.5px;
  font-weight: 600;
  color: inherit;
  word-break: break-all;
}

.change-file-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: var(--text-light);
  cursor: pointer;
  text-decoration: underline;
  font-family: inherit;
  padding: 0;
}
.change-file-btn:hover { color: var(--text-muted); }

.modal-context-section {
  padding: 18px 24px 4px;
}

.modal-context-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.modal-context-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
  line-height: 1.4;
}

.modal-selectors {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.modal-select-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.modal-select-group label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.select-optional {
  font-weight: 400;
  color: var(--text-light);
  font-size: 11px;
}

.modal-select-group select {
  padding: 8px 10px;
  border: 1.5px solid var(--border);
  border-radius: 9px;
  background: var(--surface);
  color: var(--text);
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.12s;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 10 6' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23999' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 10px;
  padding-right: 28px;
}
.modal-select-group select:focus { border-color: var(--primary); outline: none; }
.modal-select-group select:disabled { opacity: 0.4; cursor: not-allowed; }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 18px 24px 24px;
}

/* Colors come from .btn-primary tokens; only adjust sizing here */
.upload-submit-btn {
  border: none;
  font-size: 13px;
  padding: 9px 22px;
  box-shadow: none;
}
.upload-submit-btn:hover:not(:disabled) { box-shadow: none; }

.spinner { display: inline-block; width: 12px; height: 12px; border: 2px solid rgba(0,0,0,.1); border-top-color: var(--primary); border-radius: 50%; animation: spin .65s linear infinite; }
.spinner-white { border-color: rgba(255,255,255,.3); border-top-color: #fff; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 600px) {
  .modal-selectors { grid-template-columns: 1fr; }
}
</style>
