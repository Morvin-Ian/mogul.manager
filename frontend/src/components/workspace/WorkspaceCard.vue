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
