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

    <DocExplainer v-if="!dismissedExplainer" @dismiss="dismissExplainer" />

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
        @click="router.push(`/documents/${doc.uuid}`)"
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

    <DocUploadModal
      v-if="showUploadModal"
      :workspaces="workspaceStore.workspaces"
      :projects="contextProjects"
      :error="uploadError"
      :uploading="uploading"
      @close="showUploadModal = false"
      @upload="handleModalUpload"
      @workspace-change="onUploadWorkspaceChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '../stores/documents'
import { useWorkspaceStore } from '../stores/workspaces'
import { useProjectStore } from '../stores/projects'
import { useConfirm } from '../composables/useConfirm'
import type { Project } from '../types'
import DocExplainer from '../components/common/DocExplainer.vue'
import DocUploadModal from '../components/common/DocUploadModal.vue'

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
const contextProjects = ref<Project[]>([])

async function onUploadWorkspaceChange(wsId: number | null) {
  contextProjects.value = []
  if (!wsId) return
  try {
    await projectStore.fetchByWorkspace(wsId)
    contextProjects.value = [...projectStore.projects]
  } catch { /* noop */ }
}

async function handleModalUpload(file: File, ctx: { workspace_id?: number; project_id?: number }) {
  await doUpload(file, ctx)
  if (!uploadError.value) showUploadModal.value = false
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
  padding: 36px 40px 80px;
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

@media (max-width: 600px) {
  .docs-page { padding: 24px 16px 60px; }
}
</style>
