<template>
  <div class="explainer-callout">
    <button class="explainer-dismiss" @click="$emit('dismiss')">×</button>
    <div class="explainer-body">
      <div class="explainer-col">
        <div class="explainer-icon explainer-icon--upload">
          <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
            <path d="M3 15h14M10 3v8M6 7l4-4 4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <p class="explainer-label">1. Upload &amp; attach</p>
          <p class="explainer-text">Upload PDFs, Word docs, text files, or CSVs. Attach them to a workspace or project so the AI grounds its answers in that context.</p>
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
          <p class="explainer-text">The AI extracts the content, chunks it intelligently, and builds a searchable knowledge base from your files.</p>
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
          <p class="explainer-text">Head to AI Chat and ask away. Relevant excerpts are injected automatically into every response.</p>
        </div>
      </div>
    </div>
    <p class="explainer-tip">
      <svg viewBox="0 0 16 16" fill="none" width="13" height="13" style="flex-shrink:0"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.3"/><path d="M8 7v4M8 5.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
      <span><strong>Tip:</strong> Attach files to a project and the AI automatically uses them as context when you chat in that project. Global files are available anywhere.</span>
    </p>
  </div>
</template>

<script setup lang="ts">
defineEmits<{ dismiss: [] }>()
</script>

<style scoped>
.explainer-callout {
  position: relative;
  background: #EDE9FE;
  border: 1.5px solid #C4B5FD;
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
.explainer-dismiss:hover { color: var(--text); background: #C4B5FD; }

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
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.explainer-icon--upload  { background: #E5E2FF; border: 1px solid #B0A8E8; color: #3830A0; }
.explainer-icon--process { background: #D8F0D8; border: 1px solid #70C878; color: #1A5820; }
.explainer-icon--chat    { background: #F2E0CC; border: 1px solid #CFA070; color: #7A3410; }

.explainer-label { font-size: 13px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.explainer-text  { font-size: 13px; color: var(--text); line-height: 1.55; margin-bottom: 6px; opacity: 0.8; }

.explainer-tip {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  font-size: 12px;
  color: var(--text);
  background: rgba(255,255,255,0.5);
  border: 1px solid #C4B5FD;
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  line-height: 1.55;
  margin-top: 14px;
}
.explainer-tip svg { margin-top: 1px; color: #7C3AED; }
</style>
