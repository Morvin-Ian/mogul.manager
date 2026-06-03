<template>
  <div class="docs-page">

    <!-- ── Page header ────────────────────────────────────────── -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Documents</h1>
        <p class="page-sub">{{ store.documents.length }} file{{ store.documents.length !== 1 ? 's' : '' }}</p>
      </div>
      <button class="btn-upload" @click="showUploadModal = true">
        <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
          <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        Upload file
      </button>
    </div>

    <!-- ── Toolbar: filter tabs + search ─────────────────────── -->
    <div class="toolbar">
      <div class="filter-tabs">
        <button
          v-for="tab in filterTabs"
          :key="tab.key"
          class="tab"
          :class="{ active: activeFilter === tab.key }"
          @click="activeFilter = tab.key"
        >
          {{ tab.label }}
          <span class="tab-count">{{ tab.count }}</span>
        </button>
      </div>
      <div class="toolbar-right">
        <div class="search-wrap">
          <svg class="search-icon" viewBox="0 0 16 16" fill="none" width="13" height="13">
            <circle cx="6.5" cy="6.5" r="5" stroke="currentColor" stroke-width="1.6"/>
            <path d="M10.5 10.5L14 14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          <input v-model="searchQuery" class="search-input" placeholder="Search documents…" />
        </div>
        <div class="ws-filter-wrap" v-if="workspacesWithDocs.length > 0">
          <select v-model="wsFilter" class="ws-select">
            <option value="">All workspaces</option>
            <option v-for="ws in workspacesWithDocs" :key="ws.id" :value="ws.id">{{ ws.title }}</option>
          </select>
          <svg class="select-chevron" viewBox="0 0 10 6" fill="none" width="10" height="6">
            <path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- ── Drop zone ─────────────────────────────────────────── -->
    <div
      class="drop-zone"
      :class="{ 'dz-over': dragging }"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="handleDrop"
      @click="triggerFilePicker"
    >
      <svg viewBox="0 0 24 24" fill="none" width="22" height="22" class="dz-icon">
        <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M12 4v12M8 8l4-4 4 4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="dz-text">Drop your documents here, or <span class="dz-link">click to browse</span></span>
      <span class="dz-hint">PDF · DOCX · TXT · CSV · max 20 MB</span>
      <input ref="fileInput" type="file" class="hidden-input" accept=".pdf,.docx,.txt,.csv" @change="handleFilePick" />
    </div>
    <p v-if="uploadError" class="upload-error">{{ uploadError }}</p>

    <!-- ── Empty ──────────────────────────────────────────────── -->
    <div v-if="!store.loading && !store.documents.length" class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" width="26" height="26"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM14 2v6h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <p class="empty-title">No documents yet</p>
      <p class="empty-sub">Upload a PDF, DOCX, TXT, or CSV — the AI will index it and answer questions about it.</p>
    </div>

    <!-- ── Loading skeletons ──────────────────────────────────── -->
    <template v-else-if="store.loading">
      <div class="docs-table">
        <div class="table-head">
          <div class="th th-name">Document Name</div>
          <div class="th th-project">Project</div>
          <div class="th th-size">Size</div>
          <div class="th th-status">Status</div>
          <div class="th th-actions">Actions</div>
        </div>
        <div v-for="n in 5" :key="n" class="table-row sk-row">
          <div class="col-name"><div class="sk sk-icon"></div><div class="sk-lines"><div class="sk sk-title"></div><div class="sk sk-sub"></div></div></div>
          <div class="col-project"><div class="sk sk-sm"></div></div>
          <div class="col-size"><div class="sk sk-xs"></div></div>
          <div class="col-status"><div class="sk sk-badge"></div></div>
          <div class="col-actions"></div>
        </div>
      </div>
    </template>

    <!-- ── Table ─────────────────────────────────────────────── -->
    <template v-else-if="filteredDocs.length">
      <p class="result-count">{{ filteredDocs.length }} document{{ filteredDocs.length !== 1 ? 's' : '' }}</p>
      <div class="docs-table">
        <div class="table-head">
          <div class="th th-name">Document Name</div>
          <div class="th th-project">Project</div>
          <div class="th th-size">Size</div>
          <div class="th th-status">Status</div>
          <div class="th th-actions">Actions</div>
        </div>
        <div
          v-for="doc in filteredDocs"
          :key="doc.uuid"
          class="table-row"
          @click="router.push(`/documents/${doc.uuid}`)"
        >
          <!-- Name -->
          <div class="col-name">
            <span class="file-icon" :class="`ficon-${doc.file_type}`">
              <component :is="fileIcon(doc.file_type)" />
            </span>
            <div class="name-block">
              <p class="doc-name">{{ doc.title }}</p>
              <p class="doc-date">Uploaded {{ formatDate(doc.created_at) }}</p>
            </div>
          </div>
          <!-- Project/Workspace -->
          <div class="col-project">
            <span v-if="doc.project_title" class="proj-label">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M1 5v5a.5.5 0 00.5.5h9a.5.5 0 00.5-.5V5a.5.5 0 00-.5-.5H6.5L5.3 3H1.5a.5.5 0 00-.5.5V5z" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>
              {{ doc.project_title }}
            </span>
            <span v-else-if="doc.workspace_title" class="proj-label">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10"><rect x="1" y="2" width="10" height="8" rx="1.5" stroke="currentColor" stroke-width="1.1"/></svg>
              {{ doc.workspace_title }}
            </span>
            <span v-else class="text-dash">—</span>
          </div>
          <!-- Size -->
          <div class="col-size">{{ formatSize(doc.file_size) }}</div>
          <!-- Status -->
          <div class="col-status">
            <span class="status-pill" :class="`sp-${doc.status}`">
              <span v-if="doc.status === 'processing' || doc.status === 'pending'" class="spin-dot"></span>
              <svg v-else-if="doc.status === 'ready'" viewBox="0 0 10 10" fill="none" width="9" height="9"><path d="M2 5l2.5 2.5L8 2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <svg v-else-if="doc.status === 'failed'" viewBox="0 0 10 10" fill="none" width="9" height="9"><path d="M2.5 2.5l5 5M7.5 2.5l-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
              {{ doc.status }}
            </span>
          </div>
          <!-- Actions -->
          <div class="col-actions" @click.stop>
            <button class="act-btn" @click="router.push(`/documents/${doc.uuid}`)" title="Open">
              <svg viewBox="0 0 14 14" fill="none" width="13" height="13"><path d="M7 3H3a1 1 0 00-1 1v7a1 1 0 001 1h7a1 1 0 001-1V7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><path d="M9 1h4v4M13 1L7 7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
            <button v-if="doc.user_id === auth.user?.id" class="act-btn act-danger" @click="handleDelete(doc.uuid)" title="Delete">
              <svg viewBox="0 0 14 14" fill="none" width="13" height="13"><path d="M1.75 3.5h10.5M5.25 3.5V2a.5.5 0 01.5-.5h2.5a.5.5 0 01.5.5v1.5M3.5 3.5l.583 7.583a.5.5 0 00.5.417h4.834a.5.5 0 00.5-.417L10.5 3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Empty filtered ─────────────────────────────────────── -->
    <div v-else-if="store.documents.length" class="no-results">
      <svg viewBox="0 0 24 24" fill="none" width="20" height="20"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.6"/><path d="M16.5 16.5L21 21" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      No documents match your search.
    </div>

    <!-- ── Upload modal ───────────────────────────────────────── -->
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
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '../stores/documents'
import { useWorkspaceStore } from '../stores/workspaces'
import { useProjectStore } from '../stores/projects'
import { useAuthStore } from '../stores/auth'
import { useConfirm } from '../composables/useConfirm'
import type { Project } from '../types'
import DocUploadModal from '../components/common/DocUploadModal.vue'

const store = useDocumentStore()
const workspaceStore = useWorkspaceStore()
const projectStore = useProjectStore()
const auth = useAuthStore()
const router = useRouter()
const { confirm } = useConfirm()

// ── Filter state ─────────────────────────────────────────────────
const activeFilter = ref<'all' | 'pdf' | 'docx' | 'txt' | 'csv'>('all')
const searchQuery = ref('')
const wsFilter = ref<number | ''>('')

const filterTabs = computed(() => [
  { key: 'all',  label: 'All',  count: store.documents.length },
  { key: 'pdf',  label: 'PDF',  count: store.documents.filter(d => d.file_type === 'pdf').length },
  { key: 'docx', label: 'DOCX', count: store.documents.filter(d => d.file_type === 'docx').length },
  { key: 'txt',  label: 'TXT',  count: store.documents.filter(d => d.file_type === 'txt').length },
  { key: 'csv',  label: 'CSV',  count: store.documents.filter(d => d.file_type === 'csv').length },
] as const)

const workspacesWithDocs = computed(() => {
  const ids = new Set(store.documents.map(d => d.workspace_id).filter(Boolean) as number[])
  return workspaceStore.workspaces.filter(ws => ids.has(ws.id))
})

const filteredDocs = computed(() => {
  let list = store.documents
  if (activeFilter.value !== 'all') list = list.filter(d => d.file_type === activeFilter.value)
  if (wsFilter.value !== '') list = list.filter(d => d.workspace_id === wsFilter.value)
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(d => d.title.toLowerCase().includes(q) || d.original_filename.toLowerCase().includes(q))
  }
  return list
})

// ── Drag & drop ─────────────────────────────────────────────────
const dragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const uploadError = ref<string | null>(null)
const uploading = ref(false)

function triggerFilePicker() { fileInput.value?.click() }

function handleFilePick(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) doUpload(file, {})
}

function handleDrop(e: DragEvent) {
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) doUpload(file, {})
}

// ── Upload modal ─────────────────────────────────────────────────
const showUploadModal = ref(false)
const contextProjects = ref<Project[]>([])

async function onUploadWorkspaceChange(wsId: number | null) {
  contextProjects.value = []
  if (!wsId) return
  await projectStore.fetchByWorkspace(wsId)
  contextProjects.value = [...projectStore.projects]
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
    if (fileInput.value) fileInput.value.value = ''
  }
}

// ── Delete ───────────────────────────────────────────────────────
async function handleDelete(uuid: string) {
  const doc = store.documents.find(d => d.uuid === uuid)
  const ok = await confirm({
    title: 'Delete document?',
    message: doc?.original_filename ? `"${doc.original_filename}" will be permanently removed.` : 'This document will be permanently removed.',
    consequences: ['All indexed content and search data will be deleted', 'The AI will no longer reference this file'],
    confirmLabel: 'Delete document',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  await store.remove(uuid)
}

// ── Helpers ──────────────────────────────────────────────────────
function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

// File type icons — same badge-stripe style as the detail page
const PdfIcon = () => h('svg', { viewBox: '0 0 20 24', fill: 'none', width: 20, height: 24 }, [
  h('path', { d: 'M4 0h9l7 7v17H4V0z', fill: '#FEE2E2', stroke: '#FECACA', 'stroke-width': '0.5' }),
  h('path', { d: 'M13 0v7h7', fill: 'none', stroke: '#FECACA', 'stroke-width': '0.5' }),
  h('rect', { x: '2', y: '13', width: '16', height: '8', rx: '1.5', fill: '#DC2626' }),
  h('text', { x: '10', y: '19.5', 'text-anchor': 'middle', 'font-size': '5.5', 'font-weight': '800', fill: '#fff', 'font-family': 'system-ui' }, 'PDF'),
])
const DocxIcon = () => h('svg', { viewBox: '0 0 20 24', fill: 'none', width: 20, height: 24 }, [
  h('path', { d: 'M4 0h9l7 7v17H4V0z', fill: '#DBEAFE', stroke: '#BFDBFE', 'stroke-width': '0.5' }),
  h('path', { d: 'M13 0v7h7', fill: 'none', stroke: '#BFDBFE', 'stroke-width': '0.5' }),
  h('rect', { x: '2', y: '13', width: '16', height: '8', rx: '1.5', fill: '#2563EB' }),
  h('text', { x: '10', y: '19.5', 'text-anchor': 'middle', 'font-size': '4.5', 'font-weight': '800', fill: '#fff', 'font-family': 'system-ui' }, 'DOCX'),
])
const TxtIcon = () => h('svg', { viewBox: '0 0 20 24', fill: 'none', width: 20, height: 24 }, [
  h('path', { d: 'M4 0h9l7 7v17H4V0z', fill: '#F3F4F6', stroke: '#E5E7EB', 'stroke-width': '0.5' }),
  h('path', { d: 'M13 0v7h7', fill: 'none', stroke: '#E5E7EB', 'stroke-width': '0.5' }),
  h('rect', { x: '2', y: '13', width: '16', height: '8', rx: '1.5', fill: '#6B7280' }),
  h('text', { x: '10', y: '19.5', 'text-anchor': 'middle', 'font-size': '5.5', 'font-weight': '800', fill: '#fff', 'font-family': 'system-ui' }, 'TXT'),
])
const CsvIcon = () => h('svg', { viewBox: '0 0 20 24', fill: 'none', width: 20, height: 24 }, [
  h('path', { d: 'M4 0h9l7 7v17H4V0z', fill: '#DCFCE7', stroke: '#BBF7D0', 'stroke-width': '0.5' }),
  h('path', { d: 'M13 0v7h7', fill: 'none', stroke: '#BBF7D0', 'stroke-width': '0.5' }),
  h('rect', { x: '2', y: '13', width: '16', height: '8', rx: '1.5', fill: '#16A34A' }),
  h('text', { x: '10', y: '19.5', 'text-anchor': 'middle', 'font-size': '5.5', 'font-weight': '800', fill: '#fff', 'font-family': 'system-ui' }, 'CSV'),
])

function fileIcon(type: string) {
  return { pdf: PdfIcon, docx: DocxIcon, txt: TxtIcon, csv: CsvIcon }[type] ?? TxtIcon
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

/* ── Header ── */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.5px;
  line-height: 1;
}
.page-sub {
  font-size: 13px;
  color: var(--text-light);
  margin-top: 4px;
}
.btn-upload {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  background: #1C1C1E;
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.14s;
}
.btn-upload:hover { background: #333; }

/* ── Toolbar ── */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.filter-tabs {
  display: flex;
  gap: 2px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 3px;
}
.tab {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, color 0.12s;
  white-space: nowrap;
}
.tab:hover { background: var(--surface); color: var(--text); }
.tab.active { background: #fff; color: var(--text); box-shadow: var(--shadow-xs); }
.tab-count {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-light);
  background: var(--bg);
  border-radius: var(--radius-full);
  padding: 1px 6px;
}
.tab.active .tab-count { background: var(--primary-light); color: var(--primary); }

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.search-wrap {
  position: relative;
}
.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
  pointer-events: none;
}
.search-input {
  height: 36px;
  width: 220px;
  padding: 0 12px 0 32px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: var(--surface);
  color: var(--text);
  outline: none;
  font-family: inherit;
  transition: border-color 0.14s;
}
.search-input:focus { border-color: var(--primary); }

.ws-filter-wrap { position: relative; }
.ws-select {
  height: 36px;
  padding: 0 28px 0 11px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: var(--surface);
  color: var(--text);
  outline: none;
  font-family: inherit;
  appearance: none;
  cursor: pointer;
  transition: border-color 0.14s;
}
.ws-select:focus { border-color: var(--primary); }
.select-chevron {
  position: absolute;
  right: 9px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: var(--text-light);
}

/* ── Drop zone ── */
.drop-zone {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 14px 20px;
  margin-bottom: 20px;
  color: var(--text-light);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s, color 0.15s;
}
.drop-zone:hover, .drop-zone.dz-over {
  border-color: var(--primary);
  background: var(--primary-muted);
  color: var(--primary);
}
.dz-icon { flex-shrink: 0; opacity: 0.7; }
.dz-text { font-size: 13px; }
.dz-link { color: var(--primary); font-weight: 600; }
.dz-hint { font-size: 11px; color: var(--text-light); margin-left: auto; white-space: nowrap; }
.hidden-input { display: none; }
.upload-error { font-size: 12.5px; color: var(--danger); margin-bottom: 12px; }

/* ── Result count ── */
.result-count {
  font-size: 12.5px;
  color: var(--text-light);
  margin-bottom: 8px;
}

/* ── Table ── */
.docs-table {
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  background: #fff;
  overflow: hidden;
}
.table-head {
  display: grid;
  grid-template-columns: 1fr 160px 90px 110px 80px;
  padding: 0 16px;
  border-bottom: 1.5px solid var(--border);
  background: var(--bg);
}
.th {
  padding: 10px 8px;
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.th-actions { text-align: right; }

.table-row {
  display: grid;
  grid-template-columns: 1fr 160px 90px 110px 80px;
  padding: 0 16px;
  border-bottom: 1px solid var(--border);
  align-items: center;
  cursor: pointer;
  transition: background 0.1s;
}
.table-row:last-child { border-bottom: none; }
.table-row:hover { background: #F8F9FC; }

.col-name {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 8px;
}
.col-project, .col-size, .col-status, .col-actions {
  padding: 14px 8px;
}

/* File icon */
.file-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.08));
}

.name-block { min-width: 0; }
.doc-name {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 340px;
}
.doc-date { font-size: 11.5px; color: var(--text-light); margin-top: 1px; }

.proj-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12.5px;
  color: var(--text-muted);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  padding: 2px 9px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}
.text-dash { color: var(--text-light); font-size: 13px; }

.col-size { font-size: 12.5px; color: var(--text-muted); }

/* Status pill */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  border: 1px solid;
  white-space: nowrap;
  text-transform: capitalize;
}
.sp-ready      { background: #ECFDF5; color: #047857; border-color: #A7F3D0; }
.sp-failed     { background: #FFF5F5; color: var(--danger); border-color: #FECDD3; }
.sp-processing,
.sp-pending    { background: var(--primary-light); color: var(--primary); border-color: var(--primary-border); }

.spin-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: currentColor;
  animation: pulse 1s ease-in-out infinite;
  display: inline-block; flex-shrink: 0;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.7)} }

/* Actions */
.col-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}
.act-btn {
  width: 28px; height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  border-radius: 6px;
  color: var(--text-light);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.act-btn:hover { background: var(--bg); color: var(--text); }
.act-danger:hover { background: #FFF5F5; color: var(--danger); }

/* Skeleton rows */
.sk-row { cursor: default; pointer-events: none; }
@keyframes shimmer { 0%{background-position:-300px 0} 100%{background-position:300px 0} }
.sk {
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 300px 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: 4px;
}
.sk-icon  { width: 20px; height: 24px; border-radius: 3px; flex-shrink: 0; }
.sk-lines { flex: 1; display: flex; flex-direction: column; gap: 5px; }
.sk-title { height: 13px; width: 55%; }
.sk-sub   { height: 10px; width: 35%; }
.sk-sm    { height: 20px; width: 80px; border-radius: var(--radius-full); }
.sk-xs    { height: 12px; width: 50px; }
.sk-badge { height: 20px; width: 70px; border-radius: var(--radius-full); }

/* Empty */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 80px 40px;
  text-align: center;
}
.empty-icon {
  width: 60px; height: 60px;
  border-radius: var(--radius-lg);
  background: var(--primary-light);
  border: 1px solid var(--primary-border);
  display: flex; align-items: center; justify-content: center;
  color: var(--primary);
}
.empty-title { font-size: 17px; font-weight: 700; color: var(--text); }
.empty-sub { font-size: 13.5px; color: var(--text-muted); max-width: 380px; line-height: 1.6; }

.no-results {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
  color: var(--text-muted);
  padding: 24px 0;
}

@media (max-width: 700px) {
  .docs-page { padding: 20px 16px 60px; }
  .table-head, .table-row {
    grid-template-columns: 1fr 80px 80px;
  }
  .th-project, .col-project,
  .th-size, .col-size { display: none; }
  .search-input { width: 160px; }
}

/* ══════════════════════════════════════════════════════════
   DARK MODE
══════════════════════════════════════════════════════════ */

/* Upload button inverts to white pill (matches global dark btn-primary) */
[data-theme="dark"] .btn-upload {
  background: #F7F9F9;
  color: #15202B;
}
[data-theme="dark"] .btn-upload:hover {
  background: #E1E4E7;
}

/* Filter tabs container + active tab */
[data-theme="dark"] .tab.active {
  background: #253341;
  color: var(--text);
  box-shadow: 0 1px 3px rgba(0,0,0,0.4);
}

/* Search inputs */
[data-theme="dark"] .search-input,
[data-theme="dark"] .ws-select {
  background: #253341;
  border-color: #38444D;
  color: var(--text);
}
[data-theme="dark"] .search-input::placeholder { color: var(--text-light); }
[data-theme="dark"] .search-input:focus,
[data-theme="dark"] .ws-select:focus { border-color: var(--primary); }

/* Drop zone */
[data-theme="dark"] .drop-zone {
  border-color: #38444D;
}
[data-theme="dark"] .drop-zone:hover,
[data-theme="dark"] .drop-zone.dz-over {
  background: var(--primary-muted);
  border-color: var(--primary);
}

/* Table */
[data-theme="dark"] .docs-table {
  background: #1E2732;
  border-color: #38444D;
}
[data-theme="dark"] .table-head {
  background: #15202B;
  border-bottom-color: #38444D;
}
[data-theme="dark"] .table-row {
  border-bottom-color: #38444D;
}
[data-theme="dark"] .table-row:hover {
  background: #253341;
}

/* Project/workspace label on row */
[data-theme="dark"] .proj-label {
  background: #253341;
  border-color: #38444D;
  color: var(--text-muted);
}

/* Status pills — hardcoded light colours need dark overrides */
[data-theme="dark"] .sp-ready {
  background: rgba(0,186,124,0.15);
  color: #00BA7C;
  border-color: rgba(0,186,124,0.3);
}
[data-theme="dark"] .sp-failed {
  background: rgba(255,107,120,0.15);
  border-color: rgba(255,107,120,0.3);
}

/* Action buttons */
[data-theme="dark"] .act-btn:hover {
  background: #253341;
  color: var(--text);
}
[data-theme="dark"] .act-danger:hover {
  background: rgba(255,107,120,0.15);
  color: var(--danger);
}

/* Empty state */
[data-theme="dark"] .empty-state .empty-icon {
  background: #F7F9F9;
  border-color: transparent;
  color: #15202B;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
</style>
