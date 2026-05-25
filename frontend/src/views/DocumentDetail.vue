<template>
  <div class="doc-detail" v-if="doc">
    <!-- Header -->
    <div class="detail-header">
      <div class="detail-header-left">
        <button class="btn btn-sm btn-ghost back-btn" @click="router.push('/documents')">
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M8.5 2.5L4 7l4.5 4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
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
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 7A5 5 0 0112 7M12 4v3h-3M2 10v-3h3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {{ reprocessing ? 'Queued…' : 'Reprocess' }}
        </button>
        <button class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
      </div>
    </div>

    <!-- Stats bar -->
    <div class="stats-bar">
      <div class="stat-item" v-if="doc.word_count">
        <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M2 4h10M2 7h7M2 10h5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
        {{ doc.word_count.toLocaleString() }} words
      </div>
      <div class="stat-item" v-if="doc.page_count">
        <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M3 2h8l1 1v9H3V2zM5 5h4M5 7.5h4M5 10h2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
        {{ doc.page_count }} pages
      </div>
      <div class="stat-item" v-if="doc.chunk_count">
        <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><rect x="2" y="2" width="4" height="4" rx="0.5" stroke="currentColor" stroke-width="1.2"/><rect x="8" y="2" width="4" height="4" rx="0.5" stroke="currentColor" stroke-width="1.2"/><rect x="2" y="8" width="4" height="4" rx="0.5" stroke="currentColor" stroke-width="1.2"/><rect x="8" y="8" width="4" height="4" rx="0.5" stroke="currentColor" stroke-width="1.2"/></svg>
        {{ doc.chunk_count }} chunks indexed
      </div>
      <div class="stat-item">
        <svg viewBox="0 0 14 14" fill="none" width="12" height="12"><path d="M7 2v5l3 2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.2"/></svg>
        {{ formatSize(doc.file_size) }}
      </div>
      <div class="stat-item" v-if="doc.processed_at">
        Processed {{ formatDate(doc.processed_at) }}
      </div>
    </div>

    <!-- Error -->
    <div v-if="doc.status === 'failed'" class="error-box">
      <svg viewBox="0 0 16 16" fill="none" width="15" height="15"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.3"/><path d="M8 5v4M8 10.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
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
        <svg viewBox="0 0 16 16" fill="none" width="14" height="14" class="summary-icon"><path d="M8 2l1.5 3.5H13l-2.8 2 1 3.5L8 9l-3.2 2 1-3.5L3 5.5h3.5L8 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>
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
      <svg viewBox="0 0 16 16" fill="none" width="14" height="14"><path fill-rule="evenodd" d="M14 8c0 3.314-2.686 6-6 6S2 11.314 2 8s2.686-6 6-6 6 2.686 6 6zM7 5v2H5v2h2v2h2V9h2V7H9V5H7z" fill="currentColor" clip-rule="evenodd"/></svg>
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
import type { SearchHit } from '../types'
import { useDocumentStore } from '../stores/documents'

const route = useRoute()
const router = useRouter()
const store = useDocumentStore()

const docId = computed(() => Number(route.params.id))
const doc = computed(() => store.current)

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
  if (!confirm('Delete this document and all its indexed data?')) return
  await store.remove(docId.value)
  router.push('/documents')
}

async function doSearch() {
  if (!searchQuery.value.trim()) return
  searching.value = true
  searchRan.value = false
  try {
    const hits = await store.search(searchQuery.value, 6)
    searchResults.value = hits.filter((h) => h.document_id === docId.value)
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
  padding: 32px 32px 80px;
  max-width: 800px;
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
