<template>
  <div class="card workspace-card" @click="$router.push(`/workspaces/${workspace.id}`)">
    <h3>{{ workspace.title }}</h3>
    <p v-if="workspace.description" class="card-desc">{{ workspace.description }}</p>
    <div class="card-meta">
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
  return new Date(d).toLocaleDateString()
}
</script>

<style scoped>
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s, transform 0.15s;
}

.card:hover {
  box-shadow: var(--shadow);
  border-color: var(--border-strong);
  transform: translateY(-2px);
}

.card h3 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 7px;
  color: var(--text);
  letter-spacing: -0.2px;
}

.card-desc {
  color: var(--text-muted);
  font-size: 13.5px;
  margin-bottom: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
