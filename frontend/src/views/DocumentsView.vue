<template>
  <div class="docs-page">
    <div class="page-head">
      <div>
        <h2>Documents</h2>
        <p>Upload files and ask the AI anything about them — instantly grounded answers.</p>
      </div>
      <div class="page-actions">
        <label class="btn btn-primary upload-btn" :class="{ 'btn-loading': uploading }">
          <svg v-if="!uploading" viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          <span v-if="uploading" class="spinner spinner-white"></span>
          {{ uploading ? 'Uploading…' : 'Upload file' }}
          <input
            type="file"
            accept=".pdf,.docx,.txt,.csv"
            class="file-input"
            @change="handleFileInput"
            :disabled="uploading"
          />
        </label>
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
            <p class="explainer-label">1. Upload</p>
            <p class="explainer-text">Upload any PDF, Word doc, plain text, or CSV file. Up to 20 MB.</p>
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
        Try: <em>"What are the key findings in my research PDF?"</em> or <em>"Summarise the CSV report for Q2."</em>
      </p>
    </div>

    <!-- Drop zone -->
    <div
      class="dropzone"
      :class="{ 'dropzone-over': dragging }"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="handleDrop"
    >
      <svg viewBox="0 0 24 24" fill="none" width="28" height="28"><path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M12 4v12M8 8l4-4 4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <p>Drop a file here, or use the button above</p>
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
        v-for="doc in store.documents"
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

        <div class="doc-meta">
          <span v-if="doc.word_count" class="meta-chip">{{ doc.word_count.toLocaleString() }} words</span>
          <span v-if="doc.page_count" class="meta-chip">{{ doc.page_count }} pages</span>
          <span v-if="doc.chunk_count" class="meta-chip">{{ doc.chunk_count }} chunks</span>
          <span class="meta-chip meta-size">{{ formatSize(doc.file_size) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '../stores/documents'

const store = useDocumentStore()
const router = useRouter()

const uploading = ref(false)
const uploadError = ref<string | null>(null)
const dragging = ref(false)
const dismissedExplainer = ref(localStorage.getItem('docs_explainer_dismissed') === '1')

function dismissExplainer() {
  dismissedExplainer.value = true
  localStorage.setItem('docs_explainer_dismissed', '1')
}

onMounted(() => store.fetchAll())

async function doUpload(file: File) {
  uploadError.value = null
  uploading.value = true
  try {
    await store.upload(file)
  } catch (e) {
    uploadError.value = (e as Error).message
  } finally {
    uploading.value = false
  }
}

function handleFileInput(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) doUpload(file)
  ;(e.target as HTMLInputElement).value = ''
}

function handleDrop(e: DragEvent) {
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) doUpload(file)
}

async function handleDelete(id: number) {
  if (!confirm('Delete this document and all its data?')) return
  await store.remove(id)
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
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
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--text-light);
  margin-bottom: 24px;
  transition: border-color 0.15s, background 0.15s;
  cursor: default;
}
.dropzone p { font-size: 13px; margin: 0; }
.dropzone-hint { font-size: 11px !important; }
.dropzone-over {
  border-color: var(--primary);
  background: var(--primary-light);
  color: var(--primary);
}

.upload-btn { position: relative; cursor: pointer; }
.file-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}

.upload-error {
  color: var(--danger);
  font-size: 13px;
  margin-bottom: 16px;
}

/* Explainer */
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
.explainer-icon--upload  { background: var(--primary-light); border: 1px solid var(--primary-border); color: var(--primary); }
.explainer-icon--process { background: #F0FDF4; border: 1px solid #BBF7D0; color: #15803D; }
.explainer-icon--chat    { background: #FFF7ED; border: 1px solid #FED7AA; color: #C2410C; }
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

/* Grid */
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
.status-ready      { color: var(--success, #15803D); }
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

/* Spinner */
.spinner { display: inline-block; width: 12px; height: 12px; border: 2px solid rgba(0,0,0,.1); border-top-color: var(--primary); border-radius: 50%; animation: spin .65s linear infinite; }
.spinner-white { border-color: rgba(255,255,255,.3); border-top-color: #fff; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 600px) { .docs-page { padding: 24px 16px 60px; } }
</style>
