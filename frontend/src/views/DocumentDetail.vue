<template>
  <div class="doc-detail" v-if="doc">
    <!-- Header -->
    <div class="detail-header">
      <div class="detail-header-left">
        <button class="btn btn-sm btn-ghost back-btn" @click="router.push('/documents')">
          <font-awesome-icon :icon="['fas', 'chevron-left']" />
          Documents
        </button>
        <div class="doc-title-row">
          <h2>{{ doc.title }}</h2>
          <span class="file-badge" :class="`badge-${doc.file_type}`">{{ doc.file_type.toUpperCase() }}</span>
          <span class="status-badge" :class="`sbadge-${doc.status}`">
            <span v-if="doc.status === 'processing' || doc.status === 'pending'" class="spin-dot"></span>
            {{ doc.status }}
          </span>
        </div>
      </div>
      <div class="detail-actions">
        <button class="btn btn-sm" @click="handleReprocess" :disabled="reprocessing">
          <font-awesome-icon :icon="['fas', 'rotate-right']" />
          {{ reprocessing ? 'Queued…' : 'Reprocess' }}
        </button>
        <button v-if="canDelete" class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
      </div>
    </div>

    <!-- Stats bar -->
    <div class="stats-bar">
      <div class="stat-item" v-if="doc.word_count">
        <font-awesome-icon :icon="['fas', 'align-left']" />
        {{ doc.word_count.toLocaleString() }} words
      </div>
      <div class="stat-item" v-if="doc.page_count">
        <font-awesome-icon :icon="['far', 'file']" />
        {{ doc.page_count }} pages
      </div>
      <div class="stat-item" v-if="doc.chunk_count">
        <font-awesome-icon :icon="['fas', 'table-cells']" />
        {{ doc.chunk_count }} chunks indexed
      </div>
      <div class="stat-item">
        <font-awesome-icon :icon="['fas', 'hard-drive']" />
        {{ formatSize(doc.file_size) }}
      </div>
      <div class="stat-item" v-if="doc.processed_at">
        Processed {{ formatDate(doc.processed_at) }}
      </div>
    </div>

    <!-- Project assignment (visible to uploader or admin/owner) -->
    <div v-if="canReassign" class="section">
      <h3 class="section-title">Project</h3>
      <div class="project-assign-row">
        <select v-model="selectedProjectId" class="project-select" @change="reassignProject">
          <option :value="null">General — not linked to a project</option>
          <option v-for="p in accessibleProjects" :key="p.id" :value="p.id">{{ p.title }}</option>
        </select>
        <span v-if="reassigning" class="reassign-state">
          <font-awesome-icon :icon="['fas', 'spinner']" spin /> Saving…
        </span>
        <span v-else-if="reassigned" class="reassign-state success">
          <font-awesome-icon :icon="['fas', 'circle-check']" /> Saved
        </span>
      </div>
    </div>
    <div v-else-if="doc.project_id" class="section">
      <h3 class="section-title">Project</h3>
      <p class="project-label">
        <font-awesome-icon :icon="['fas', 'folder']" />
        {{ projectTitle }}
      </p>
    </div>

    <!-- Error -->
    <div v-if="doc.status === 'failed'" class="error-box">
      <font-awesome-icon :icon="['fas', 'circle-exclamation']" />
      <div>
        <p class="error-title">Processing failed</p>
        <p class="error-msg">{{ doc.error_message }}</p>
      </div>
    </div>

    <!-- Processing indicator -->
    <div v-else-if="doc.status === 'pending' || doc.status === 'processing'" class="processing-box">
      <div class="spinner"></div>
      <div>
        <p class="processing-title">{{ doc.status === 'pending' ? 'Queued for processing…' : 'Extracting and indexing…' }}</p>
        <p class="processing-sub">This page will update automatically when done.</p>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="doc.summary" class="section">
      <h3 class="section-title">AI Summary</h3>
      <div class="summary-card">
        <font-awesome-icon :icon="['fas', 'wand-magic-sparkles']" class="summary-icon" />
        <p>{{ doc.summary }}</p>
      </div>
    </div>

    <!-- Semantic search -->
    <div v-if="doc.status === 'ready'" class="section">
      <h3 class="section-title">Search this document</h3>
      <div class="search-row">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Ask a question or search for a topic…"
          class="search-input"
          @keydown.enter="doSearch"
        />
        <button class="btn btn-primary btn-sm" @click="doSearch" :disabled="searching">
          <span v-if="searching" class="spinner spinner-white"></span>
          {{ searching ? '' : 'Search' }}
        </button>
      </div>

      <div v-if="searchResults.length" class="search-results">
        <div v-for="(hit, i) in searchResults" :key="i" class="hit-card">
          <div class="hit-head">
            <span class="hit-chunk">Chunk {{ hit.chunk_index + 1 }}</span>
            <span class="hit-score">{{ Math.round(hit.similarity * 100) }}% match</span>
          </div>
          <p class="hit-content">{{ hit.content }}</p>
        </div>
      </div>
      <p v-else-if="searchRan" class="no-results">No relevant excerpts found for that query.</p>
    </div>

    <!-- RAG hint -->
    <div v-if="doc.status === 'ready'" class="rag-hint">
      <font-awesome-icon :icon="['fas', 'circle-info']" />
      <p>This document is now part of your AI's knowledge base. Ask about it in <router-link to="/chat" class="rag-link">AI Chat</router-link>.</p>
    </div>
  </div>

  <div v-else-if="store.loading" class="loading-state">
    <div class="spinner spinner-lg"></div>
  </div>

  <div v-else class="empty-state">Document not found.</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { SearchHit, Project } from '../types'
import { useDocumentStore } from '../stores/documents'
import { useProjectStore } from '../stores/projects'
import { useAuthStore } from '../stores/auth'
import { useConfirm } from '../composables/useConfirm'

const route = useRoute()
const router = useRouter()
const store = useDocumentStore()
const { confirm } = useConfirm()

const docId = computed(() => route.params.id as string)
const doc = computed(() => store.current)
const auth = useAuthStore()
const projectStore = useProjectStore()

// Rights: uploader can always delete/reassign; admin/owner via membership check
const canDelete = computed(() => {
  if (!doc.value) return false
  return doc.value.user_id === auth.user?.id
})

const canReassign = computed(() => {
  if (!doc.value) return false
  return doc.value.user_id === auth.user?.id
})

// Project reassignment
const accessibleProjects = ref<Project[]>([])
const selectedProjectId = ref<number | null>(null)
const reassigning = ref(false)
const reassigned = ref(false)

const projectTitle = computed(() => {
  if (!doc.value?.project_id) return null
  return accessibleProjects.value.find(p => p.id === doc.value!.project_id)?.title ?? `Project ${doc.value.project_id}`
})

async function reassignProject() {
  if (!doc.value) return
  reassigning.value = true
  reassigned.value = false
  try {
    await store.updateProjectId(docId.value, selectedProjectId.value)
    reassigned.value = true
    setTimeout(() => { reassigned.value = false }, 2000)
  } finally {
    reassigning.value = false
  }
}

const reprocessing = ref(false)
const searchQuery = ref('')
const searching = ref(false)
const searchResults = ref<SearchHit[]>([])
const searchRan = ref(false)

let pollTimer: ReturnType<typeof setTimeout> | null = null

onMounted(async () => {
  await store.fetchOne(docId.value)
  if (doc.value?.status === 'pending' || doc.value?.status === 'processing') {
    schedulePoll()
  }
  // Load all accessible projects for reassignment dropdown
  if (projectStore.projects.length === 0) await projectStore.fetchAll()
  accessibleProjects.value = projectStore.projects
  selectedProjectId.value = doc.value?.project_id ?? null
})

onUnmounted(() => { if (pollTimer) clearTimeout(pollTimer) })

function schedulePoll() {
  pollTimer = setTimeout(async () => {
    await store.fetchOne(docId.value)
    if (doc.value?.status === 'pending' || doc.value?.status === 'processing') {
      schedulePoll()
    }
  }, 4000)
}

async function handleReprocess() {
  reprocessing.value = true
  await store.reprocess(docId.value)
  reprocessing.value = false
  schedulePoll()
}

async function handleDelete() {
  const doc = store.documents.find((d) => d.uuid === docId.value)
  const ok = await confirm({
    title: 'Delete document?',
    message: doc?.original_filename ? `"${doc.original_filename}" will be permanently removed.` : 'This document will be permanently removed.',
    consequences: ['All indexed content and search data will be deleted', 'The AI will no longer have access to this file'],
    confirmLabel: 'Delete document',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  await store.remove(docId.value)
  router.push('/documents')
}

async function doSearch() {
  if (!searchQuery.value.trim()) return
  searching.value = true
  searchRan.value = false
  try {
    const hits = await store.search(searchQuery.value, 6)
    searchResults.value = hits.filter((h) => h.document_id === doc.value?.id)
    searchRan.value = true
  } finally {
    searching.value = false
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.doc-detail {
  padding: 36px 40px 80px;
}

/* Header */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}
.detail-header-left { flex: 1; min-width: 0; }
.back-btn { margin-bottom: 12px; color: var(--text-muted); padding-left: 6px; }

.doc-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.doc-title-row h2 {
  font-size: 22px; font-weight: 800; letter-spacing: -0.5px;
  color: var(--text); line-height: 1.2;
}

.file-badge {
  font-size: 9.5px; font-weight: 800; letter-spacing: 0.5px;
  padding: 3px 8px; border-radius: var(--radius-full); border: 1px solid;
}
.badge-pdf  { background: #FFF1F2; color: #BE123C; border-color: #FECDD3; }
.badge-docx { background: #EFF6FF; color: #1D4ED8; border-color: #BFDBFE; }
.badge-txt  { background: var(--bg); color: var(--text-light); border-color: var(--border); }
.badge-csv  { background: #F0FDF4; color: #15803D; border-color: #BBF7D0; }

.status-badge {
  font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
  padding: 3px 10px; border-radius: var(--radius-full); border: 1px solid;
  display: flex; align-items: center; gap: 5px;
}
.sbadge-ready      { background: #ECFDF5; color: #047857; border-color: #A7F3D0; }
.sbadge-failed     { background: var(--danger-bg); color: var(--danger); border-color: var(--danger-border); }
.sbadge-processing,
.sbadge-pending    { background: var(--primary-light); color: var(--primary); border-color: var(--primary-border); }

.spin-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--primary);
  animation: pulse 1s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.7)} }

.detail-actions { display: flex; gap: 8px; flex-shrink: 0; align-items: flex-start; padding-top: 36px; }

/* Stats bar */
.stats-bar {
  display: flex; gap: 20px; flex-wrap: wrap;
  padding: 14px 18px; background: var(--bg);
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  margin-bottom: 28px;
}
.stat-item {
  display: flex; align-items: center; gap: 5px;
  font-size: 12.5px; color: var(--text-muted);
}

/* Error / processing */
.error-box, .processing-box {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 14px 16px; border-radius: var(--radius-lg);
  margin-bottom: 24px;
}
.error-box { background: var(--danger-bg); border: 1px solid var(--danger-border); color: var(--danger); }
.processing-box { background: var(--primary-light); border: 1px solid var(--primary-border); color: var(--primary); }
.error-title, .processing-title { font-size: 13.5px; font-weight: 600; }
.error-msg, .processing-sub { font-size: 12.5px; margin-top: 2px; opacity: 0.8; }

/* Section */
.section { margin-bottom: 32px; }
.section-title {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.8px; color: var(--text-light); margin-bottom: 12px;
}

/* Summary */
.summary-card {
  display: flex; align-items: flex-start; gap: 12px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 16px 18px;
}
.summary-icon { flex-shrink: 0; color: var(--primary); margin-top: 2px; }
.summary-card p { font-size: 14px; color: var(--text); line-height: 1.65; }

/* Search */
.search-row { display: flex; gap: 8px; margin-bottom: 16px; }
.search-input {
  flex: 1; height: 36px; border: 1.5px solid var(--border);
  border-radius: var(--radius-sm); padding: 0 12px;
  font-size: 13.5px; background: var(--surface); color: var(--text);
  outline: none; transition: border-color 0.15s;
}
.search-input:focus { border-color: var(--primary); }

.search-results { display: flex; flex-direction: column; gap: 10px; }
.hit-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 12px 16px;
}
.hit-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 8px;
}
.hit-chunk { font-size: 11px; font-weight: 700; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.4px; }
.hit-score {
  font-size: 11px; font-weight: 700; color: var(--primary);
  background: var(--primary-light); border: 1px solid var(--primary-border);
  padding: 1px 8px; border-radius: var(--radius-full);
}
.hit-content { font-size: 13px; color: var(--text-muted); line-height: 1.6; }
.no-results { font-size: 13px; color: var(--text-light); font-style: italic; }

/* RAG hint */
.rag-hint {
  display: flex; align-items: flex-start; gap: 10px;
  background: var(--primary-light); border: 1px solid var(--primary-border);
  border-radius: var(--radius-lg); padding: 14px 16px;
  color: var(--primary);
}
.rag-hint p { font-size: 13px; line-height: 1.5; }
.rag-link { color: var(--primary); font-weight: 600; text-decoration: underline; }

/* Project assignment */
.project-assign-row {
  display: flex; align-items: center; gap: 10px;
}
.project-select {
  flex: 1; padding: 8px 12px; border: 1.5px solid var(--border);
  border-radius: var(--radius-sm); font-size: 13.5px; font-family: inherit;
  background: var(--bg); color: var(--text); outline: none;
  transition: border-color 0.15s;
}
.project-select:focus { border-color: var(--primary); }
.reassign-state { font-size: 12.5px; color: var(--text-muted); display: flex; align-items: center; gap: 5px; white-space: nowrap; }
.reassign-state.success { color: var(--success); }
.project-label { font-size: 13.5px; color: var(--text); display: flex; align-items: center; gap: 7px; }

/* Loading */
.loading-state { display: flex; justify-content: center; padding: 80px; }
.empty-state { text-align: center; padding: 80px; color: var(--text-muted); }
.spinner { display: inline-block; width: 22px; height: 22px; border: 3px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }
.spinner-white { border-color: rgba(255,255,255,.3); border-top-color: #fff; }
.spinner-lg { width: 28px; height: 28px; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 600px) {
  .doc-detail { padding: 20px 16px 60px; }
  .detail-header { flex-direction: column; }
  .detail-actions { padding-top: 0; }
}
</style>
