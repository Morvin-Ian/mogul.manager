<template>
  <div class="docs-page">
    <div class="page-head">
      <div>
        <h2>Documents</h2>
        <p>Upload files, attach them to a workspace or project, and ask the AI anything about them.</p>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" @click="showUploadModal = true">
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          Upload file
        </button>
      </div>
    </div>

    <!-- Explainer -->
    <div v-if="!dismissedExplainer" class="explainer-callout">
      <button class="explainer-dismiss" @click="dismissExplainer">×</button>
      <div class="explainer-body">
        <div class="explainer-col">
          <div class="explainer-icon explainer-icon--upload">
            <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
              <path d="M3 15h14M10 3v8M6 7l4-4 4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="explainer-label">1. Upload &amp; attach</p>
            <p class="explainer-text">Upload any PDF, Word doc, plain text, or CSV. Optionally attach it to a workspace or project so the AI uses it only in that context.</p>
          </div>
        </div>
        <div class="explainer-col">
          <div class="explainer-icon explainer-icon--process">
            <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
              <circle cx="10" cy="10" r="7.5" stroke="currentColor" stroke-width="1.5"/>
              <path d="M7 10l2 2 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="explainer-label">2. Auto-process</p>
            <p class="explainer-text">The AI extracts text, splits it into chunks, and builds a searchable knowledge base from your file.</p>
          </div>
        </div>
        <div class="explainer-col">
          <div class="explainer-icon explainer-icon--chat">
            <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
              <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd"/>
            </svg>
          </div>
          <div>
            <p class="explainer-label">3. Ask anything</p>
            <p class="explainer-text">Go to AI Chat and ask questions. Relevant excerpts are automatically injected into context before the AI responds.</p>
          </div>
        </div>
      </div>
      <p class="explainer-tip">
        <svg viewBox="0 0 16 16" fill="none" width="13" height="13" style="flex-shrink:0"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.3"/><path d="M8 7v4M8 5.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
        <span><strong>Tip:</strong> Attach a file to a project and the AI will ground its answers in that file when you're working in that project's context. Global files are available everywhere.</span>
      </p>
    </div>

    <!-- Filter bar -->
    <div v-if="store.documents.length > 0" class="filter-bar">
      <button class="filter-chip" :class="{ active: activeFilter === 'all' }" @click="activeFilter = 'all'">
        All <span class="chip-count">{{ store.documents.length }}</span>
      </button>
      <button class="filter-chip" :class="{ active: activeFilter === 'global' }" @click="activeFilter = 'global'">
        Global <span class="chip-count">{{ globalCount }}</span>
      </button>
      <button
        v-for="ws in workspacesWithDocs"
        :key="ws.id"
        class="filter-chip"
        :class="{ active: activeFilter === ws.id }"
        @click="activeFilter = ws.id"
      >
        {{ ws.title }} <span class="chip-count">{{ docCountFor(ws.id) }}</span>
      </button>
    </div>

    <!-- Drop zone (global) -->
    <div
      class="dropzone"
      :class="{ 'dropzone-over': dragging }"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="handleDrop"
    >
      <svg viewBox="0 0 24 24" fill="none" width="28" height="28"><path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M12 4v12M8 8l4-4 4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <p>Drop a file here to upload globally, or use the button above to attach to a workspace</p>
      <p class="dropzone-hint">PDF · DOCX · TXT · CSV · max 20 MB</p>
    </div>

    <p v-if="uploadError" class="upload-error">{{ uploadError }}</p>

    <!-- Loading skeletons -->
    <div v-if="store.loading" class="docs-grid">
      <div v-for="n in 3" :key="n" class="doc-card sk-card">
        <div class="sk-line sk-title"></div>
        <div class="sk-line sk-desc"></div>
        <div class="sk-line sk-bar"></div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="!store.documents.length" class="empty">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" width="28" height="28"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <p class="empty-title">No documents yet</p>
      <p>Upload a PDF, DOCX, TXT, or CSV and the AI will be able to read, summarise, and answer questions about it.</p>
    </div>

    <!-- Grid -->
    <div v-else class="docs-grid">
      <div
        v-for="doc in filteredDocs"
        :key="doc.id"
        class="doc-card"
        @click="router.push(`/documents/${doc.id}`)"
      >
        <div class="doc-card-head">
          <span class="file-type-badge" :class="`badge-${doc.file_type}`">{{ doc.file_type.toUpperCase() }}</span>
          <span class="doc-status" :class="`status-${doc.status}`">
            <span v-if="doc.status === 'processing' || doc.status === 'pending'" class="spin-dot"></span>
            <svg v-else-if="doc.status === 'ready'" viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else-if="doc.status === 'failed'" viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            {{ doc.status }}
          </span>
          <button class="doc-delete" @click.stop="handleDelete(doc.id)" title="Delete">
            <svg viewBox="0 0 12 12" fill="none" width="11" height="11"><path d="M1.5 3h9M4.5 3V2a.5.5 0 01.5-.5h1a.5.5 0 01.5.5v1M3 3l.5 6.5a.5.5 0 00.5.5h4a.5.5 0 00.5-.5L9 3" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>

        <h3 class="doc-title">{{ doc.title }}</h3>

        <p v-if="doc.summary" class="doc-summary">{{ doc.summary }}</p>
        <p v-else-if="doc.status === 'processing' || doc.status === 'pending'" class="doc-processing">
          <span class="spin-dot spin-dot-inline"></span> Processing…
        </p>
        <p v-else-if="doc.status === 'failed'" class="doc-failed">{{ doc.error_message || 'Processing failed' }}</p>

        <!-- Context badge -->
        <div v-if="doc.project_title || doc.workspace_title" class="doc-context">
          <svg viewBox="0 0 14 14" fill="none" width="11" height="11" style="flex-shrink:0">
            <path d="M2 5v6a1 1 0 001 1h8a1 1 0 001-1V5.5a1 1 0 00-1-1H7L5.5 3H3a1 1 0 00-1 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
          </svg>
          <span v-if="doc.project_title">{{ doc.project_title }}</span>
          <span v-else>{{ doc.workspace_title }}</span>
        </div>

        <div class="doc-meta">
          <span v-if="doc.word_count" class="meta-chip">{{ doc.word_count.toLocaleString() }} words</span>
          <span v-if="doc.page_count" class="meta-chip">{{ doc.page_count }} pages</span>
          <span v-if="doc.chunk_count" class="meta-chip">{{ doc.chunk_count }} chunks</span>
          <span class="meta-chip meta-size">{{ formatSize(doc.file_size) }}</span>
        </div>
      </div>
    </div>

    <!-- ── Upload Modal ── -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal upload-modal">
        <div class="modal-header">
          <h2>Upload Document</h2>
          <button class="modal-close" @click="closeUploadModal">×</button>
        </div>

        <!-- File drop zone inside modal -->
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
            <svg viewBox="0 0 24 24" fill="none" width="22" height="22" style="color:#68CC80">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
              <path d="M14 2v6h6M9 13l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p class="pending-file-name">{{ pendingFile.name }}</p>
            <button class="change-file-btn" @click="pendingFile = null">Change file</button>
          </template>
        </div>

        <!-- Context selectors -->
        <div class="modal-context-section">
          <p class="modal-context-label">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 5v6a1 1 0 001 1h8a1 1 0 001-1V5.5a1 1 0 00-1-1H7L5.5 3H3a1 1 0 00-1 2z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>
            Attach to (optional)
          </p>
          <p class="modal-context-hint">Scopes this file so the AI uses it only within the selected context.</p>
          <div class="modal-selectors">
            <div class="modal-select-group">
              <label>Workspace</label>
              <select v-model="uploadWorkspaceId" @change="onUploadWorkspaceChange">
                <option :value="null">None — global file</option>
                <option v-for="ws in workspaceStore.workspaces" :key="ws.id" :value="ws.id">{{ ws.title }}</option>
              </select>
            </div>
            <div class="modal-select-group">
              <label>Project <span class="select-optional">(within workspace)</span></label>
              <select v-model="uploadProjectId" :disabled="!uploadWorkspaceId || loadingContextProjects">
                <option :value="null">{{ uploadWorkspaceId ? 'Workspace-level' : 'Select a workspace first' }}</option>
                <option v-for="p in contextProjects" :key="p.id" :value="p.id">{{ p.title }}</option>
              </select>
            </div>
          </div>
        </div>

        <p v-if="uploadError" class="form-error" style="margin: 0 24px;">{{ uploadError }}</p>

        <div class="modal-footer">
          <button class="btn" @click="closeUploadModal">Cancel</button>
          <button class="btn btn-primary upload-submit-btn" :disabled="!pendingFile || uploading" @click="submitUpload">
            <span v-if="uploading" class="spinner spinner-white"></span>
            {{ uploading ? 'Uploading…' : 'Upload' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '../stores/documents'
import { useWorkspaceStore } from '../stores/workspaces'
import { useProjectStore } from '../stores/projects'
import { useConfirm } from '../composables/useConfirm'
import type { Project } from '../types'

const store = useDocumentStore()
const workspaceStore = useWorkspaceStore()
const { confirm } = useConfirm()
const projectStore = useProjectStore()
const router = useRouter()

// ── Explainer ───────────────────────────────────────────────────
const dismissedExplainer = ref(localStorage.getItem('docs_explainer_dismissed') === '1')
function dismissExplainer() {
  dismissedExplainer.value = true
  localStorage.setItem('docs_explainer_dismissed', '1')
}

// ── Main page drag/drop (global upload) ─────────────────────────
const dragging = ref(false)
const uploadError = ref<string | null>(null)
const uploading = ref(false)

function handleDrop(e: DragEvent) {
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) doUpload(file, {})
}

// ── Filter bar ──────────────────────────────────────────────────
const activeFilter = ref<'all' | 'global' | number>('all')

const globalCount = computed(() =>
  store.documents.filter(d => !d.workspace_id && !d.project_id).length
)

const workspacesWithDocs = computed(() => {
  const ids = new Set(store.documents.map(d => d.workspace_id).filter(Boolean) as number[])
  return workspaceStore.workspaces.filter(ws => ids.has(ws.id))
})

function docCountFor(wsId: number) {
  return store.documents.filter(d => d.workspace_id === wsId).length
}

const filteredDocs = computed(() => {
  if (activeFilter.value === 'all') return store.documents
  if (activeFilter.value === 'global') return store.documents.filter(d => !d.workspace_id && !d.project_id)
  return store.documents.filter(d => d.workspace_id === activeFilter.value)
})

// ── Upload modal ─────────────────────────────────────────────────
const showUploadModal = ref(false)
const pendingFile = ref<File | null>(null)
const modalDragging = ref(false)
const uploadWorkspaceId = ref<number | null>(null)
const uploadProjectId = ref<number | null>(null)
const contextProjects = ref<Project[]>([])
const loadingContextProjects = ref(false)

function closeUploadModal() {
  showUploadModal.value = false
  pendingFile.value = null
  uploadWorkspaceId.value = null
  uploadProjectId.value = null
  contextProjects.value = []
  uploadError.value = null
}

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

async function onUploadWorkspaceChange() {
  uploadProjectId.value = null
  contextProjects.value = []
  if (!uploadWorkspaceId.value) return
  loadingContextProjects.value = true
  try {
    await projectStore.fetchByWorkspace(uploadWorkspaceId.value)
    contextProjects.value = [...projectStore.projects]
  } finally {
    loadingContextProjects.value = false
  }
}

async function submitUpload() {
  if (!pendingFile.value) return
  const ctx = {
    workspace_id: uploadWorkspaceId.value ?? undefined,
    project_id: uploadProjectId.value ?? undefined,
  }
  await doUpload(pendingFile.value, ctx)
  if (!uploadError.value) closeUploadModal()
}

async function doUpload(file: File, ctx: { workspace_id?: number; project_id?: number }) {
  uploadError.value = null
  uploading.value = true
  try {
    await store.upload(file, ctx)
  } catch (e) {
    uploadError.value = (e as Error).message
  } finally {
    uploading.value = false
  }
}

// ── Other ───────────────────────────────────────────────────────
async function handleDelete(id: number) {
  const doc = store.documents.find((d) => d.id === id)
  const ok = await confirm({
    title: 'Delete document?',
    message: doc?.original_filename ? `"${doc.original_filename}" will be permanently removed.` : 'This document will be permanently removed.',
    consequences: ['All indexed content and search data will be deleted', 'The AI will no longer reference this file'],
    confirmLabel: 'Delete document',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  await store.remove(id)
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

onMounted(async () => {
  await store.fetchAll()
  if (!workspaceStore.workspaces.length) workspaceStore.fetchAll()
})
</script>

<style scoped>
.docs-page {
  padding: 36px 32px 80px;
  max-width: 960px;
}

/* Drop zone */
.dropzone {
  border: 2px dashed var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  color: var(--text-light);
  margin-bottom: 24px;
  transition: border-color 0.15s, background 0.15s;
  cursor: default;
}
.dropzone p { font-size: 13px; margin: 0; text-align: center; }
.dropzone-hint { font-size: 11px !important; }
.dropzone-over {
  border-color: var(--primary);
  background: var(--primary-light);
  color: var(--primary);
}

.upload-error {
  color: var(--danger);
  font-size: 13px;
  margin-bottom: 16px;
}

/* ── Explainer ── */
.explainer-callout {
  position: relative;
  background: var(--primary-light);
  border: 1px solid var(--primary-border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  margin-bottom: 24px;
}
.explainer-dismiss {
  position: absolute;
  top: 10px;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  color: var(--text-light);
  line-height: 1;
  padding: 2px 6px;
  border-radius: 4px;
  transition: color 0.1s, background 0.1s;
}
.explainer-dismiss:hover { color: var(--text); background: var(--primary-border); }
.explainer-body {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: wrap;
}
.explainer-col {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  flex: 1;
  min-width: 200px;
}
.explainer-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.explainer-icon--upload  { background: #E5E2FF; border: 1px solid #B0A8E8; color: #3830A0; }
.explainer-icon--process { background: #D8F0D8; border: 1px solid #70C878; color: #1A5820; }
.explainer-icon--chat    { background: #F2E0CC; border: 1px solid #CFA070; color: #7A3410; }
.explainer-label { font-size: 12.5px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.explainer-text  { font-size: 12.5px; color: var(--text-muted); line-height: 1.55; margin-bottom: 6px; }
.explainer-tip {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  font-size: 11.5px;
  color: var(--text-muted);
  background: rgba(255,255,255,0.5);
  border: 1px solid var(--primary-border);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  line-height: 1.55;
  margin-top: 14px;
}
.explainer-tip svg { margin-top: 1px; color: var(--primary); }

/* ── Filter bar ── */
.filter-bar {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  font-size: 12.5px;
  font-weight: 600;
  border: 1.5px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s, color 0.12s;
  font-family: inherit;
}
.filter-chip:hover { background: var(--bg); border-color: var(--border-strong); color: var(--text); }
.filter-chip.active { background: #1C1C1E; border-color: #1C1C1E; color: #fff; }
.chip-count {
  font-size: 11px;
  font-weight: 700;
  opacity: 0.7;
}
.filter-chip.active .chip-count { opacity: 0.75; }

/* ── Grid ── */
.docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 4px;
}

.doc-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.12s;
  box-shadow: var(--shadow-xs);
}
.doc-card:hover {
  border-color: var(--primary-border);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.doc-card-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-type-badge {
  font-size: 9.5px;
  font-weight: 800;
  letter-spacing: 0.5px;
  padding: 2px 7px;
  border-radius: var(--radius-full);
  border: 1px solid;
  flex-shrink: 0;
}
.badge-pdf  { background: #FFF1F2; color: #BE123C; border-color: #FECDD3; }
.badge-docx { background: #EFF6FF; color: #1D4ED8; border-color: #BFDBFE; }
.badge-txt  { background: var(--bg); color: var(--text-light); border-color: var(--border); }
.badge-csv  { background: #F0FDF4; color: #15803D; border-color: #BBF7D0; }

.doc-status {
  display: flex; align-items: center; gap: 4px;
  font-size: 10.5px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.4px; flex: 1; color: var(--text-light);
}
.status-ready      { color: #1A5820; }
.status-failed     { color: var(--danger); }
.status-processing,
.status-pending    { color: var(--primary); }

.spin-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--primary);
  animation: pulse 1s ease-in-out infinite;
  display: inline-block;
}
.spin-dot-inline { margin-right: 4px; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.7)} }

.doc-delete {
  opacity: 0; background: none; border: none; cursor: pointer;
  color: var(--text-light); padding: 3px; border-radius: 4px;
  display: flex; transition: opacity 0.1s, color 0.1s;
}
.doc-card:hover .doc-delete { opacity: 1; }
.doc-delete:hover { color: var(--danger); }

.doc-title {
  font-size: 14px; font-weight: 700; color: var(--text);
  letter-spacing: -0.3px; line-height: 1.3;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}

.doc-summary {
  font-size: 12.5px; color: var(--text-muted); line-height: 1.55;
  display: -webkit-box; -webkit-line-clamp: 3;
  -webkit-box-orient: vertical; overflow: hidden;
}

.doc-processing { font-size: 12.5px; color: var(--primary); display: flex; align-items: center; gap: 4px; }
.doc-failed { font-size: 12px; color: var(--danger); font-style: italic; }

/* Context badge on card */
.doc-context {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  background: #E5E2FF;
  border: 1px solid #B0A8E8;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  color: #3830A0;
  align-self: flex-start;
}

.doc-meta {
  display: flex; gap: 6px; flex-wrap: wrap;
}
.meta-chip {
  font-size: 11px; color: var(--text-light);
  background: var(--bg); border: 1px solid var(--border);
  padding: 1px 8px; border-radius: var(--radius-full);
}

/* Empty */
.empty {
  display: flex; flex-direction: column; align-items: center;
  gap: 14px; padding: 80px 40px; text-align: center;
}
.empty-icon {
  width: 64px; height: 64px; border-radius: var(--radius-lg);
  background: var(--primary-light); border: 1px solid var(--primary-border);
  display: flex; align-items: center; justify-content: center; color: var(--primary);
}
.empty-title { font-size: 17px; font-weight: 700; color: var(--text); }
.empty p { font-size: 13.5px; color: var(--text-muted); max-width: 360px; line-height: 1.6; }

/* Skeleton */
.sk-card { cursor: default; pointer-events: none; }
@keyframes shimmer { 0%{background-position:-300px 0} 100%{background-position:300px 0} }
.sk-line {
  background: linear-gradient(90deg,var(--bg) 25%,var(--border) 50%,var(--bg) 75%);
  background-size: 300px 100%; animation: shimmer 1.4s ease-in-out infinite; border-radius: 4px;
}
.sk-title { height: 14px; width: 60%; }
.sk-desc  { height: 11px; width: 90%; }
.sk-bar   { height: 9px;  width: 50%; border-radius: 99px; }

/* ── Upload Modal ── */
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
.modal-dropzone.has-file { border-color: #70C878; background: #F0FAF0; color: #1A5820; }

.browse-link {
  color: var(--primary);
  text-decoration: underline;
  cursor: pointer;
  font-weight: 600;
}

.pending-file-name {
  font-size: 13.5px;
  font-weight: 600;
  color: #1A5820;
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

/* Context selectors in modal */
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

.upload-submit-btn {
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  padding: 9px 22px;
  box-shadow: none;
}
.upload-submit-btn:hover:not(:disabled) { background: #2e2e30; box-shadow: none; }
.upload-submit-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* Spinner */
.spinner { display: inline-block; width: 12px; height: 12px; border: 2px solid rgba(0,0,0,.1); border-top-color: var(--primary); border-radius: 50%; animation: spin .65s linear infinite; }
.spinner-white { border-color: rgba(255,255,255,.3); border-top-color: #fff; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 600px) {
  .docs-page { padding: 24px 16px 60px; }
  .modal-selectors { grid-template-columns: 1fr; }
}
</style>
