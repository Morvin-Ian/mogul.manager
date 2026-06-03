<template>
  <!-- Skeleton while loading doc -->
  <div v-if="store.loading && !doc" class="detail-layout sk-detail-layout">
    <!-- Sidebar skeleton -->
    <div class="sk-sidebar-wrap">
      <div class="sk sk-back-btn"></div>
      <div class="sk-identity">
        <div class="sk sk-file-icon"></div>
        <div class="sk-title-col">
          <div class="sk sk-doc-title"></div>
          <div class="sk sk-doc-title sk-doc-title-short"></div>
          <div class="sk-badge-row">
            <div class="sk sk-badge"></div>
            <div class="sk sk-badge"></div>
          </div>
        </div>
      </div>
      <div class="sk-stats-g">
        <div v-for="n in 4" :key="n" class="sk sk-stat"></div>
      </div>
      <div class="sk-section-blk">
        <div class="sk sk-section-lbl"></div>
        <div class="sk sk-summary-block"></div>
      </div>
    </div>
    <!-- Viewer skeleton -->
    <div class="sk-viewer-wrap">
      <div class="sk-toolbar-bar">
        <div class="sk sk-filename"></div>
        <div class="sk sk-open-btn"></div>
      </div>
      <div class="sk-viewer-body"></div>
    </div>
  </div>

  <!-- Not found -->
  <div v-else-if="!doc" class="not-found">
    <svg viewBox="0 0 24 24" fill="none" width="28" height="28"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM14 2v6h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
    <p>Document not found.</p>
    <button class="btn-back" @click="router.push('/documents')">Back to Documents</button>
  </div>

  <!-- Split panel -->
  <div v-else class="detail-layout">

    <!-- ── LEFT SIDEBAR ─────────────────────────────────────── -->
    <aside class="sidebar">
      <!-- Back -->
      <button class="back-btn" @click="router.push('/documents')">
        <svg viewBox="0 0 10 16" fill="none" width="8" height="13">
          <path d="M9 1L1 8l8 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Documents
      </button>

      <!-- File identity -->
      <div class="file-identity">
        <div class="file-icon-lg" :class="`ficon-${doc.file_type}`">
          <component :is="fileIconLg(doc.file_type)" />
        </div>
        <div class="file-title-block">
          <h2 class="file-title">{{ doc.title }}</h2>
          <div class="badge-row">
            <span class="type-badge" :class="`tb-${doc.file_type}`">{{ doc.file_type.toUpperCase() }}</span>
            <span class="status-badge" :class="`sb-${doc.status}`">
              <span v-if="doc.status === 'processing' || doc.status === 'pending'" class="spin-dot"></span>
              <svg v-else-if="doc.status === 'ready'" viewBox="0 0 10 10" fill="none" width="8" height="8"><path d="M2 5l2.5 2.5L8 2.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
              {{ doc.status }}
            </span>
          </div>
        </div>
      </div>

      <!-- Processing / error notice -->
      <div v-if="doc.status === 'failed'" class="notice notice-err">
        <svg viewBox="0 0 14 14" fill="none" width="14" height="14"><circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.4"/><path d="M7 4v3.5M7 9.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
        <p>{{ doc.error_message || 'Processing failed' }}</p>
      </div>
      <div v-else-if="doc.status === 'pending' || doc.status === 'processing'" class="notice notice-info">
        <div class="spinner"></div>
        <p>{{ doc.status === 'pending' ? 'Queued for processing…' : 'Extracting and indexing…' }}<br><span class="notice-sub">This panel updates automatically.</span></p>
      </div>

      <!-- Stats ── -->
      <div class="stats-grid">
        <div class="stat-item" v-if="doc.page_count">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M3 1h8a1 1 0 011 1v10a1 1 0 01-1 1H3a1 1 0 01-1-1V2a1 1 0 011-1z" stroke="currentColor" stroke-width="1.2"/><path d="M5 5h4M5 7.5h4M5 10h2" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>
          <span>{{ doc.page_count }} pages</span>
        </div>
        <div class="stat-item" v-if="doc.word_count">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 4h10M2 7h10M2 10h6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
          <span>{{ doc.word_count.toLocaleString() }} words</span>
        </div>
        <div class="stat-item">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><rect x="1" y="3" width="12" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M4 3V2M7 3V2M10 3V2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          <span>{{ formatSize(doc.file_size) }}</span>
        </div>
        <div class="stat-item" v-if="doc.chunk_count">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><rect x="1" y="1" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.2"/><rect x="8" y="1" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.2"/><rect x="1" y="8" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.2"/><rect x="8" y="8" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.2"/></svg>
          <span>{{ doc.chunk_count }} chunks</span>
        </div>
        <div class="stat-item" v-if="doc.processed_at">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.2"/><path d="M7 4.5V7l1.5 1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
          <span>{{ formatDate(doc.processed_at) }}</span>
        </div>
      </div>

      <!-- Project assign -->
      <div v-if="canReassign" class="sidebar-section">
        <p class="section-label">Project</p>
        <div class="project-select-wrap">
          <select v-model="selectedProjectId" class="project-select" @change="reassignProject">
            <option :value="null">General (no project)</option>
            <option v-for="p in accessibleProjects" :key="p.id" :value="p.id">{{ p.title }}</option>
          </select>
          <span v-if="reassigning" class="reassign-msg"><div class="spinner spinner-xs"></div> Saving…</span>
          <span v-else-if="reassigned" class="reassign-msg success">
            <svg viewBox="0 0 10 10" fill="none" width="10" height="10"><path d="M2 5l2.5 2.5L8 2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
            Saved
          </span>
        </div>
      </div>

      <!-- AI Summary -->
      <div v-if="doc.summary" class="sidebar-section">
        <p class="section-label">AI Summary</p>
        <div class="summary-card">
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13" class="summary-icon"><path d="M7 1l1.5 3 3.5.5-2.5 2.5.5 3.5L7 9l-3 1.5.5-3.5L2 4.5l3.5-.5z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
          <p>{{ doc.summary }}</p>
        </div>
      </div>

      <!-- RAG hint -->
      <div v-if="doc.status === 'ready'" class="rag-hint">
        <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.3"/><path d="M7 6.5V9.5M7 4.5v.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
        <p>Now part of your AI knowledge base — ask about it in <router-link to="/chat">AI Chat</router-link>.</p>
      </div>

      <!-- Actions -->
      <div class="sidebar-actions">
        <button class="action-btn" @click="handleReprocess" :disabled="reprocessing">
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13"><path d="M2 8a5 5 0 109.9-1.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><path d="M12 5V2l-2.5 2.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {{ reprocessing ? 'Queued…' : 'Reprocess' }}
        </button>
        <button v-if="canDelete" class="action-btn action-danger" @click="handleDelete">
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13"><path d="M1.75 3.5h10.5M5.25 3.5V2a.5.5 0 01.5-.5h2.5a.5.5 0 01.5.5v1.5M3.5 3.5l.583 7.583a.5.5 0 00.5.417h4.834a.5.5 0 00.5-.417L10.5 3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Delete
        </button>
      </div>
    </aside>

    <!-- ── RIGHT VIEWER ─────────────────────────────────────── -->
    <main class="viewer">
      <!-- Viewer toolbar -->
      <div class="viewer-toolbar">
        <span class="viewer-filename">{{ doc.original_filename }}</span>
        <a v-if="viewUrl" :href="viewUrl" target="_blank" rel="noopener" class="download-btn" title="Open in new tab">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M7 1h6v6M13 1L7 7M5 3H2a1 1 0 00-1 1v8a1 1 0 001 1h8a1 1 0 001-1v-3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Open
        </a>
      </div>

      <!-- Viewer skeleton while fetching file -->
      <div v-if="viewerLoading" class="viewer-body sk-viewer-content">
        <div v-for="n in 18" :key="n" class="sk sk-viewer-line" :style="{ width: [90,100,85,100,75,100,92,100,80,100,95,70,100,88,100,60,100,84][n-1]+'%' }"></div>
      </div>

      <!-- PDF iframe -->
      <iframe
        v-if="doc.file_type === 'pdf' && viewUrl"
        :src="viewUrl"
        class="pdf-frame"
        title="Document preview"
      />
      <!-- TXT / CSV inline viewer -->
      <div v-else-if="(doc.file_type === 'txt' || doc.file_type === 'csv') && textContent" class="viewer-body text-viewer">
        <pre class="text-pre">{{ textContent }}</pre>
      </div>
      <!-- DOCX or no URL available -->
      <div v-else class="viewer-body viewer-center viewer-unavail">
        <svg viewBox="0 0 24 24" fill="none" width="44" height="44"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <p class="unavail-title">
          <template v-if="doc.file_type === 'docx'">DOCX preview not available</template>
          <template v-else-if="doc.status === 'pending' || doc.status === 'processing'">Processing…</template>
          <template v-else>Preview unavailable</template>
        </p>
        <p class="unavail-sub">
          <template v-if="doc.file_type === 'docx'">Download the file to view it in Word or Google Docs.</template>
          <template v-else-if="viewerError">{{ viewerError }}</template>
          <template v-else-if="doc.status === 'pending' || doc.status === 'processing'">File is still being processed.</template>
          <template v-else>Could not load the file.</template>
        </p>
        <div class="unavail-actions" v-if="viewUrl">
          <a :href="viewUrl" target="_blank" rel="noopener" class="action-btn">Download file</a>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Project } from '../types'
import { useDocumentStore } from '../stores/documents'
import { useProjectStore } from '../stores/projects'
import { useAuthStore } from '../stores/auth'
import { useConfirm } from '../composables/useConfirm'
import { fetchBlob } from '../stores/client'

const route = useRoute()
const router = useRouter()
const store = useDocumentStore()
const { confirm } = useConfirm()

const docId = computed(() => route.params.id as string)
const doc = computed(() => store.current)
const auth = useAuthStore()
const projectStore = useProjectStore()

const canDelete   = computed(() => doc.value?.user_id === auth.user?.id)
const canReassign = computed(() => doc.value?.user_id === auth.user?.id)

// ── Project reassignment ─────────────────────────────────────────
const accessibleProjects = ref<Project[]>([])
const selectedProjectId  = ref<number | null>(null)
const reassigning = ref(false)
const reassigned  = ref(false)

async function reassignProject() {
  if (!doc.value) return
  reassigning.value = true
  reassigned.value  = false
  try {
    await store.updateProjectId(docId.value, selectedProjectId.value)
    reassigned.value = true
    setTimeout(() => { reassigned.value = false }, 2000)
  } finally {
    reassigning.value = false
  }
}

// ── Viewer ───────────────────────────────────────────────────────
const viewUrl       = ref<string | null>(null)   // blob URL — revoked on unmount
const viewerLoading = ref(true)
const viewerError   = ref<string | null>(null)
const textContent   = ref<string | null>(null)

async function loadViewUrl() {
  if (!doc.value) return
  viewerError.value = null
  try {
    // Use our own /file proxy: authenticated, inline Content-Disposition,
    // no S3 CORS / X-Frame-Options issues since it's same-origin.
    const blob = await fetchBlob(`/documents/${docId.value}/file`)
    viewUrl.value = URL.createObjectURL(blob)

    // Pre-load text content for TXT/CSV inline viewer
    if (doc.value.file_type === 'txt' || doc.value.file_type === 'csv') {
      textContent.value = await blob.text()
    }
  } catch (e) {
    viewerError.value = (e as Error).message
  } finally {
    viewerLoading.value = false
  }
}

// ── Reprocess / Delete ───────────────────────────────────────────
const reprocessing = ref(false)

async function handleReprocess() {
  reprocessing.value = true
  await store.reprocess(docId.value)
  reprocessing.value = false
  schedulePoll()
}

async function handleDelete() {
  const d = store.documents.find(x => x.uuid === docId.value)
  const ok = await confirm({
    title: 'Delete document?',
    message: d?.original_filename ? `"${d.original_filename}" will be permanently removed.` : 'This document will be permanently removed.',
    consequences: ['All indexed content and search data will be deleted', 'The AI will no longer have access to this file'],
    confirmLabel: 'Delete document',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  await store.remove(docId.value)
  router.push('/documents')
}

// ── Polling ──────────────────────────────────────────────────────
let pollTimer: ReturnType<typeof setTimeout> | null = null

function schedulePoll() {
  pollTimer = setTimeout(async () => {
    await store.fetchOne(docId.value)
    if (doc.value?.status === 'pending' || doc.value?.status === 'processing') {
      schedulePoll()
    }
  }, 4000)
}

onMounted(async () => {
  await store.fetchOne(docId.value)
  if (doc.value?.status === 'pending' || doc.value?.status === 'processing') schedulePoll()
  if (projectStore.projects.length === 0) await projectStore.fetchAll()
  accessibleProjects.value = projectStore.projects
  selectedProjectId.value  = doc.value?.project_id ?? null
  await loadViewUrl()
})

onUnmounted(() => {
  if (pollTimer) clearTimeout(pollTimer)
  if (viewUrl.value) URL.revokeObjectURL(viewUrl.value)
})

// ── Helpers ──────────────────────────────────────────────────────
function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

// Larger file type icon SVGs for sidebar
const PdfIconLg = () => h('svg', { viewBox: '0 0 28 34', fill: 'none', width: 36, height: 44 }, [
  h('path', { d: 'M5 0h15l8 8v26H5V0z', fill: '#FEE2E2', stroke: '#FECACA', 'stroke-width': '0.5' }),
  h('path', { d: 'M20 0v8h8', fill: 'none', stroke: '#FECACA', 'stroke-width': '0.5' }),
  h('rect', { x: '3', y: '16', width: '22', height: '10', rx: '2', fill: '#DC2626' }),
  h('text', { x: '14', y: '23.5', 'text-anchor': 'middle', 'font-size': '7', 'font-weight': '800', fill: '#fff', 'font-family': 'system-ui' }, 'PDF'),
])
const DocxIconLg = () => h('svg', { viewBox: '0 0 28 34', fill: 'none', width: 36, height: 44 }, [
  h('path', { d: 'M5 0h15l8 8v26H5V0z', fill: '#DBEAFE', stroke: '#BFDBFE', 'stroke-width': '0.5' }),
  h('path', { d: 'M20 0v8h8', fill: 'none', stroke: '#BFDBFE', 'stroke-width': '0.5' }),
  h('rect', { x: '3', y: '16', width: '22', height: '10', rx: '2', fill: '#2563EB' }),
  h('text', { x: '14', y: '23.5', 'text-anchor': 'middle', 'font-size': '6', 'font-weight': '800', fill: '#fff', 'font-family': 'system-ui' }, 'DOC'),
])
const TxtIconLg = () => h('svg', { viewBox: '0 0 28 34', fill: 'none', width: 36, height: 44 }, [
  h('path', { d: 'M5 0h15l8 8v26H5V0z', fill: '#F3F4F6', stroke: '#E5E7EB', 'stroke-width': '0.5' }),
  h('path', { d: 'M20 0v8h8', fill: 'none', stroke: '#E5E7EB', 'stroke-width': '0.5' }),
  h('rect', { x: '3', y: '16', width: '22', height: '10', rx: '2', fill: '#6B7280' }),
  h('text', { x: '14', y: '23.5', 'text-anchor': 'middle', 'font-size': '7', 'font-weight': '800', fill: '#fff', 'font-family': 'system-ui' }, 'TXT'),
])
const CsvIconLg = () => h('svg', { viewBox: '0 0 28 34', fill: 'none', width: 36, height: 44 }, [
  h('path', { d: 'M5 0h15l8 8v26H5V0z', fill: '#DCFCE7', stroke: '#BBF7D0', 'stroke-width': '0.5' }),
  h('path', { d: 'M20 0v8h8', fill: 'none', stroke: '#BBF7D0', 'stroke-width': '0.5' }),
  h('rect', { x: '3', y: '16', width: '22', height: '10', rx: '2', fill: '#16A34A' }),
  h('text', { x: '14', y: '23.5', 'text-anchor': 'middle', 'font-size': '7', 'font-weight': '800', fill: '#fff', 'font-family': 'system-ui' }, 'CSV'),
])

function fileIconLg(type: string) {
  return { pdf: PdfIconLg, docx: DocxIconLg, txt: TxtIconLg, csv: CsvIconLg }[type] ?? TxtIconLg
}
</script>

<style scoped>
/* ── Layout ── */
.detail-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  height: calc(100vh - 64px); /* 64px = AppHeader height */
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow-y: auto;
  border-right: 1.5px solid var(--border);
  background: #fff;
  padding: 20px 20px 80px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  background: none;
  border: none;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  margin-bottom: 16px;
  transition: color 0.12s;
}
.back-btn:hover { color: var(--text); }

/* File identity */
.file-identity {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
}
.file-icon-lg { flex-shrink: 0; }
.file-title-block { flex: 1; min-width: 0; }
.file-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.35;
  word-break: break-word;
  margin-bottom: 6px;
}
.badge-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.type-badge {
  font-size: 9.5px; font-weight: 800; letter-spacing: 0.6px;
  padding: 2px 7px; border-radius: var(--radius-full); border: 1px solid;
}
.tb-pdf  { background: #FFF1F2; color: #BE123C; border-color: #FECDD3; }
.tb-docx { background: #EFF6FF; color: #1D4ED8; border-color: #BFDBFE; }
.tb-txt  { background: var(--bg); color: var(--text-light); border-color: var(--border); }
.tb-csv  { background: #F0FDF4; color: #15803D; border-color: #BBF7D0; }
.status-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10.5px; font-weight: 700; text-transform: capitalize; letter-spacing: 0.3px;
  padding: 2px 9px; border-radius: var(--radius-full); border: 1px solid;
}
.sb-ready      { background: #ECFDF5; color: #047857; border-color: #A7F3D0; }
.sb-failed     { background: #FFF5F5; color: var(--danger); border-color: #FECDD3; }
.sb-processing,
.sb-pending    { background: var(--primary-light); color: var(--primary); border-color: var(--primary-border); }

.spin-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: currentColor;
  animation: pulse 1s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.7)} }

/* Notices */
.notice {
  display: flex; align-items: flex-start; gap: 9px;
  padding: 12px 13px; border-radius: var(--radius-sm);
  margin-bottom: 16px; font-size: 12.5px; line-height: 1.5;
}
.notice-info { background: var(--primary-light); color: var(--primary); border: 1px solid var(--primary-border); }
.notice-err  { background: #FFF5F5; color: var(--danger); border: 1px solid #FECDD3; }
.notice-sub  { font-size: 11.5px; opacity: 0.8; }

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 20px;
}
.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
}
.stat-item svg { flex-shrink: 0; color: var(--text-light); }

/* Sections */
.sidebar-section { margin-bottom: 20px; }
.section-label {
  font-size: 10.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.7px;
  color: var(--text-light);
  margin-bottom: 8px;
}

/* Project select */
.project-select-wrap { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.project-select {
  flex: 1;
  min-width: 0;
  padding: 7px 10px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 12.5px;
  font-family: inherit;
  background: var(--bg);
  color: var(--text);
  outline: none;
  transition: border-color 0.13s;
}
.project-select:focus { border-color: var(--primary); }
.reassign-msg {
  display: flex; align-items: center; gap: 5px;
  font-size: 12px; color: var(--text-muted); white-space: nowrap;
}
.reassign-msg.success { color: var(--success); }

/* Summary */
.summary-card {
  display: flex; align-items: flex-start; gap: 10px;
  background: var(--primary-muted);
  border: 1px solid var(--primary-border);
  border-radius: var(--radius-sm);
  padding: 12px 13px;
}
.summary-icon { flex-shrink: 0; color: var(--primary); margin-top: 2px; }
.summary-card p { font-size: 12.5px; color: var(--text); line-height: 1.6; }


/* RAG hint */
.rag-hint {
  display: flex; align-items: flex-start; gap: 8px;
  background: var(--primary-muted); border: 1px solid var(--primary-border);
  border-radius: var(--radius-sm); padding: 10px 12px;
  color: var(--primary); font-size: 12px; line-height: 1.5;
  margin-bottom: 20px;
}
.rag-hint a { color: var(--primary); font-weight: 700; text-decoration: underline; }

/* Sidebar actions */
.sidebar-actions {
  display: flex;
  gap: 8px;
  padding-top: 4px;
  margin-top: auto;
  flex-wrap: wrap;
}
.action-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 12.5px; font-weight: 600; font-family: inherit;
  background: var(--bg); color: var(--text);
  cursor: pointer; transition: background 0.12s, border-color 0.12s;
  text-decoration: none;
}
.action-btn:hover { background: var(--surface); border-color: var(--border-strong); }
.action-danger { color: var(--danger); }
.action-danger:hover { background: #FFF5F5; border-color: #FECDD3; }

/* ── Viewer ── */
.viewer {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
}
.viewer-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1.5px solid var(--border);
  background: #fff;
  flex-shrink: 0;
}
.viewer-filename {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 260px;
}
.viewer-tabs {
  display: flex;
  gap: 2px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 7px;
  padding: 2px;
  flex-shrink: 0;
}
.vtab {
  padding: 5px 12px;
  border: none; background: transparent;
  border-radius: 5px;
  font-size: 12.5px; font-weight: 600; font-family: inherit;
  color: var(--text-muted); cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.vtab:hover { background: var(--surface); color: var(--text); }
.vtab.active { background: #fff; color: var(--text); box-shadow: var(--shadow-xs); }
.download-btn {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 5px 12px;
  border: 1.5px solid var(--border);
  border-radius: 7px;
  font-size: 12.5px; font-weight: 600;
  color: var(--text-muted); text-decoration: none;
  margin-left: auto; flex-shrink: 0;
  transition: background 0.12s, border-color 0.12s, color 0.12s;
}
.download-btn:hover { background: var(--bg); border-color: var(--border-strong); color: var(--text); text-decoration: none; }

/* Viewer body areas */
.viewer-body {
  flex: 1;
  overflow: auto;
  min-height: 0;
}
.viewer-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 100%;
  color: var(--text-muted);
}
.viewer-hint { font-size: 13px; color: var(--text-light); }

/* PDF iframe */
.pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
  flex: 1;
  min-height: 0;
}

/* Unavailable state */
.viewer-unavail { background: #fff; }
.unavail-title { font-size: 15px; font-weight: 700; color: var(--text); }
.unavail-sub { font-size: 13px; color: var(--text-muted); text-align: center; max-width: 320px; line-height: 1.6; }
.unavail-actions { display: flex; gap: 8px; margin-top: 4px; }

/* Text / chunks viewer */
.text-viewer {
  background: #fff;
  overflow-y: auto;
}
.text-pre {
  padding: 24px 28px;
  font-family: 'Fira Mono', 'Courier New', monospace;
  font-size: 12.5px;
  line-height: 1.7;
  color: var(--text);
  white-space: pre-wrap;
  word-break: break-word;
}

/* Spinners */
.spinner {
  display: inline-block;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
.spinner { width: 18px; height: 18px; }
.spinner-xs { width: 13px; height: 13px; border-width: 2px; }
.spinner-sm { width: 14px; height: 14px; border-width: 2px; }
.spinner-lg { width: 28px; height: 28px; border-width: 3px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Skeleton ── */
@keyframes sk-shimmer { 0%{background-position:-600px 0} 100%{background-position:600px 0} }
.sk {
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 600px 100%;
  animation: sk-shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
  flex-shrink: 0;
}
.sk-detail-layout { pointer-events: none; }
.sk-sidebar-wrap {
  display: flex; flex-direction: column; gap: 16px;
  padding: 20px 20px 40px;
  border-right: 1.5px solid var(--border);
  background: var(--surface);
  overflow: hidden;
}
.sk-back-btn    { height: 24px; width: 100px; border-radius: 99px; }
.sk-identity    { display: flex; align-items: flex-start; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--border); }
.sk-file-icon   { width: 36px; height: 44px; border-radius: 4px; }
.sk-title-col   { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.sk-doc-title   { height: 16px; width: 90%; }
.sk-doc-title-short { width: 60%; }
.sk-badge-row   { display: flex; gap: 6px; }
.sk-badge       { height: 18px; width: 54px; border-radius: 99px; }
.sk-stats-g     { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.sk-stat        { height: 42px; border-radius: 8px; }
.sk-section-blk { display: flex; flex-direction: column; gap: 8px; }
.sk-section-lbl { height: 10px; width: 80px; }
.sk-summary-block { height: 72px; border-radius: 8px; }
.sk-viewer-wrap {
  display: flex; flex-direction: column;
  background: var(--bg); overflow: hidden;
}
.sk-toolbar-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1.5px solid var(--border);
  background: var(--surface);
}
.sk-filename  { height: 13px; width: 200px; }
.sk-open-btn  { height: 26px; width: 64px; border-radius: 7px; }
.sk-viewer-body { flex: 1; background: #fff; }
.sk-viewer-content {
  padding: 28px 32px;
  display: flex; flex-direction: column; gap: 10px;
  background: #fff; overflow: hidden;
}
.sk-viewer-line { height: 13px; }

/* Full page states */
.not-found {
  display: flex; flex-direction: column; align-items: center;
  gap: 14px; padding: 80px;
  text-align: center; color: var(--text-muted);
}
.btn-back {
  padding: 9px 18px;
  background: var(--primary); color: #fff;
  border: none; border-radius: var(--radius-sm);
  font-size: 13.5px; font-weight: 600; font-family: inherit;
  cursor: pointer; margin-top: 8px;
}

@media (max-width: 768px) {
  .detail-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    height: auto;
    min-height: calc(100vh - 64px);
    overflow: visible;
  }
  .sidebar {
    max-height: 55vh;
    overflow-y: auto;
    border-right: none;
    border-bottom: 1.5px solid var(--border);
  }
  .viewer { height: 65vh; min-height: 400px; }
}

/* ══════════════════════════════════════════════════════════
   DARK MODE
══════════════════════════════════════════════════════════ */

/* Sidebar */
[data-theme="dark"] .sidebar {
  background: #1E2732;
  border-right-color: #38444D;
}

/* File type badges — hardcoded light colours */
[data-theme="dark"] .tb-pdf {
  background: rgba(220,38,38,0.15);
  color: #FF8896;
  border-color: rgba(220,38,38,0.3);
}
[data-theme="dark"] .tb-docx {
  background: rgba(37,99,235,0.15);
  color: #60A5FA;
  border-color: rgba(37,99,235,0.3);
}
[data-theme="dark"] .tb-txt {
  background: #253341;
  color: var(--text-muted);
  border-color: #38444D;
}
[data-theme="dark"] .tb-csv {
  background: rgba(22,163,74,0.15);
  color: #4ADE80;
  border-color: rgba(22,163,74,0.3);
}

/* Status badges */
[data-theme="dark"] .sb-ready {
  background: rgba(0,186,124,0.15);
  color: #00BA7C;
  border-color: rgba(0,186,124,0.3);
}
[data-theme="dark"] .sb-failed {
  background: rgba(255,107,120,0.15);
  border-color: rgba(255,107,120,0.3);
}

/* Notices */
[data-theme="dark"] .notice-err {
  background: rgba(255,107,120,0.12);
  border-color: rgba(255,107,120,0.3);
  color: var(--danger);
}

/* Stats tiles */
[data-theme="dark"] .stat-item {
  background: #253341;
  border-color: #38444D;
}

/* Project select */
[data-theme="dark"] .project-select {
  background: #253341;
  border-color: #38444D;
  color: var(--text);
}
[data-theme="dark"] .project-select:focus { border-color: var(--primary); }

/* Summary card */
[data-theme="dark"] .summary-card {
  background: rgba(91,155,255,0.1);
  border-color: rgba(91,155,255,0.25);
}


/* Action buttons */
[data-theme="dark"] .action-btn {
  background: #253341;
  border-color: #38444D;
  color: var(--text);
}
[data-theme="dark"] .action-btn:hover {
  background: #2D3E50;
  border-color: #536471;
}
[data-theme="dark"] .action-danger { color: var(--danger); }
[data-theme="dark"] .action-danger:hover {
  background: rgba(255,107,120,0.15);
  border-color: rgba(255,107,120,0.3);
}

/* Viewer toolbar */
[data-theme="dark"] .viewer-toolbar {
  background: #1E2732;
  border-bottom-color: #38444D;
}

/* Download/open link */
[data-theme="dark"] .download-btn {
  border-color: #38444D;
  color: var(--text-muted);
}
[data-theme="dark"] .download-btn:hover {
  background: #253341;
  border-color: #536471;
  color: var(--text);
}

/* Viewer unavailable / text viewer backgrounds */
[data-theme="dark"] .viewer-unavail,
[data-theme="dark"] .text-viewer {
  background: #1E2732;
}
[data-theme="dark"] .text-pre {
  color: var(--text);
}

/* Spinners inherit --border which is already overridden by dark vars ✓ */

/* Not-found page */
[data-theme="dark"] .not-found {
  color: var(--text-muted);
}
</style>
