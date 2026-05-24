<template>
  <div class="workspace-card" @click="$router.push(`/workspaces/${workspace.id}`)">
    <div class="card-body">
      <h3>{{ workspace.title }}</h3>
      <p v-if="workspace.description" class="card-desc">{{ workspace.description }}</p>
    </div>
    <div class="card-footer">
      <span class="badge" :class="workspace.is_archived ? 'badge-danger' : 'badge-success'">
        {{ workspace.is_archived ? 'Archived' : 'Active' }}
      </span>
      <span class="date">{{ formatDate(workspace.created_at) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Workspace } from '../../types'

defineProps<{
  workspace: Workspace
}>()

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.workspace-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 22px 24px 20px;
  cursor: pointer;
  transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.workspace-card:hover {
  box-shadow: var(--shadow);
  border-color: var(--primary-border);
  transform: translateY(-2px);
}

.card-body {
  flex: 1;
}

h3 {
  font-size: 15.5px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
  margin-bottom: 7px;
  line-height: 1.3;
}

.card-desc {
  color: var(--text-muted);
  font-size: 13.5px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
</style>
