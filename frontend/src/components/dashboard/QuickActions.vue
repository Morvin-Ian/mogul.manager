<template>
  <div class="panel">
    <div class="panel-hdr">
      <span class="panel-title">Quick Actions</span>
    </div>
    <div class="qa-list">
      <button class="qa-card qa-card--blue" @click="$emit('create-project')">
        <div class="qa-icon qa-icon--blue">
          <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
            <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 11v6M9 14h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="qa-text">
          <span class="qa-title">New Project</span>
          <span class="qa-desc">Organize work into projects</span>
        </div>
        <svg class="qa-arrow" viewBox="0 0 16 16" fill="none" width="14" height="14">
          <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <button class="qa-card qa-card--teal" @click="router.push('/chat')">
        <div class="qa-icon qa-icon--teal">
          <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 10h8M8 14h5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="qa-text">
          <span class="qa-title">AI Chat</span>
          <span class="qa-desc">Get instant AI assistance</span>
        </div>
        <svg class="qa-arrow" viewBox="0 0 16 16" fill="none" width="14" height="14">
          <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <button class="qa-card qa-card--green" @click="$emit('create-workspace')">
        <div class="qa-icon qa-icon--green">
          <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
            <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="qa-text">
          <span class="qa-title">New Workspace</span>
          <span class="qa-desc">Create a new workspace</span>
        </div>
        <svg class="qa-arrow" viewBox="0 0 16 16" fill="none" width="14" height="14">
          <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <button class="qa-card qa-card--orange" @click="router.push('/documents')">
        <div class="qa-icon qa-icon--orange">
          <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="qa-text">
          <span class="qa-title">Documents</span>
          <span class="qa-desc">Browse files and resources</span>
        </div>
        <svg class="qa-arrow" viewBox="0 0 16 16" fill="none" width="14" height="14">
          <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

defineEmits<{ 'create-project': []; 'create-workspace': [] }>()

const router = useRouter()
</script>

<style scoped>
/* ── Quick Actions Panel ────────────── */
.qa-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.qa-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border: 1.5px solid transparent;
  border-radius: 14px;
  background: #ffffff;
  cursor: pointer;
  text-align: left;
  transition: box-shadow 0.14s, transform 0.12s;
  width: 100%;
}
.qa-card:hover {
  box-shadow: 0 4px 16px rgba(10,11,13,0.10);
  transform: translateX(2px);
}

.qa-card--blue   { background: #D5EDF0; border-color: #80C4C0; }
.qa-card--teal   { background: #DBEAFE; border-color: #93C5FD; }
.qa-card--green  { background: #D8F0D8; border-color: #70C878; }
.qa-card--orange { background: #F2E0CC; border-color: #CFA070; }

.qa-icon {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}

.qa-icon--blue   { background: #80C8C4; color: #1A7068; }
.qa-icon--teal   { background: #3B82F6; color: #fff; }
.qa-icon--green  { background: #68CC80; color: #1A5820; }
.qa-icon--orange { background: #D4A878; color: #7A3410; }

.qa-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.qa-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
}

.qa-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.4;
}

.qa-arrow {
  color: var(--text-light);
  flex-shrink: 0;
  transition: transform 0.12s, color 0.12s;
}
.qa-card:hover .qa-arrow {
  transform: translateX(3px);
  color: var(--text-muted);
}
</style>
