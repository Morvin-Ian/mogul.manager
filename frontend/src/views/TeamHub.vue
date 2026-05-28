<template>
  <div class="team-hub">
    <div class="page-head">
      <div>
        <h2>Team</h2>
        <p class="page-subtitle">Manage your workspace teams, invite members, and assign roles.</p>
      </div>
    </div>

    <Loading v-if="loading" label="Loading workspaces…" />

    <template v-else>
      <div v-if="workspaces.length === 0" class="empty-state">
        <div class="empty-icon">
          <font-awesome-icon :icon="['fas', 'users']" />
        </div>
        <h3>No workspaces yet</h3>
        <p>Create a workspace to start building a team.</p>
        <button class="btn btn-primary" @click="$router.push('/workspaces')">
          Create workspace
        </button>
      </div>

      <div v-else class="workspace-list">
        <div
          v-for="ws in workspaces"
          :key="ws.id"
          class="workspace-card"
        >
          <div class="ws-card-left">
            <div class="ws-avatar" :style="avatarColor(ws.id)">
              {{ ws.title.charAt(0).toUpperCase() }}
            </div>
            <div class="ws-info">
              <div class="ws-title-row">
                <span class="ws-title">{{ ws.title }}</span>
                <span class="role-tag" :class="ws.user_id === auth.user?.id ? 'role-owner' : 'role-member'">
                  {{ ws.user_id === auth.user?.id ? 'Owner' : 'Member' }}
                </span>
              </div>
              <p v-if="ws.description" class="ws-desc">{{ ws.description }}</p>
              <div class="ws-meta">
                <span class="meta-item">
                  <font-awesome-icon :icon="['fas', 'calendar']" />
                  Created {{ formatDate(ws.created_at) }}
                </span>
              </div>
            </div>
          </div>

          <div class="ws-card-actions">
            <button
              class="btn btn-sm"
              @click="$router.push(`/workspaces/${ws.id}`)"
              title="Open workspace"
            >
              Open
            </button>
            <button
              class="btn btn-sm btn-primary"
              @click="$router.push(`/team/${ws.id}`)"
              title="Manage team"
            >
              <font-awesome-icon :icon="['fas', 'users']" />
              Manage Team
            </button>
          </div>
        </div>
      </div>

      <!-- Invite hint for owners -->
      <div v-if="hasOwnedWorkspaces" class="tip-card">
        <font-awesome-icon :icon="['fas', 'lightbulb']" class="tip-icon" />
        <div>
          <strong>Invite teammates</strong> — Click "Manage Team" on any workspace you own to invite
          people by email. They'll receive an invite link; if they don't have an account yet, they
          can sign up and the workspace will be waiting for them.
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useWorkspaceStore } from '../stores/workspaces'
import { useAuthStore } from '../stores/auth'
import Loading from '../components/common/Loading.vue'

const workspaceStore = useWorkspaceStore()
const auth = useAuthStore()

const loading = ref(true)

onMounted(async () => {
  try {
    await workspaceStore.fetchAll()
  } finally {
    loading.value = false
  }
})

const workspaces = computed(() => workspaceStore.workspaces)
const hasOwnedWorkspaces = computed(() =>
  workspaces.value.some((ws) => ws.user_id === auth.user?.id)
)

const AVATAR_COLORS = [
  ['#0052FF', '#003CBF'],
  ['#7C3AED', '#5B21B6'],
  ['#059669', '#047857'],
  ['#DC2626', '#B91C1C'],
  ['#D97706', '#B45309'],
  ['#0891B2', '#0E7490'],
]

function avatarColor(id: number) {
  const [from, to] = AVATAR_COLORS[id % AVATAR_COLORS.length]
  return { background: `linear-gradient(135deg, ${from}, ${to})` }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.team-hub {
  padding: 36px 36px 80px;
  max-width: 860px;
}

.page-head {
  margin-bottom: 32px;
}

.page-head h2 {
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.7px;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 13.5px;
  color: var(--text-muted);
  line-height: 1.5;
}

/* ── Empty state ── */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 13.5px;
  margin-bottom: 20px;
}

/* ── Workspace list ── */
.workspace-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 24px;
}

.workspace-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.workspace-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 2px 12px rgba(10,11,13,0.07);
}

.ws-card-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
  flex: 1;
}

.ws-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
  color: #fff;
  flex-shrink: 0;
}

.ws-info {
  min-width: 0;
  flex: 1;
}

.ws-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 3px;
}

.ws-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.role-tag {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  text-transform: capitalize;
  flex-shrink: 0;
}

.role-owner  { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
.role-admin  { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
.role-member { background: #F0F2F5; color: #374151; border: 1px solid #E2E8F0; }

.ws-desc {
  font-size: 12.5px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.ws-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  color: var(--text-light);
}

.ws-card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* ── Tip card ── */
.tip-card {
  background: var(--primary-light);
  border: 1.5px solid var(--primary-border);
  border-radius: var(--radius);
  padding: 14px 18px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  font-size: 13px;
  color: var(--text);
  line-height: 1.55;
}

.tip-icon {
  color: var(--primary);
  font-size: 15px;
  flex-shrink: 0;
  margin-top: 2px;
}

/* ── Dark mode ── */
:global([data-theme="dark"]) .workspace-card {
  background: rgba(30, 39, 50, 0.8);
}

:global([data-theme="dark"]) .tip-card {
  background: rgba(0, 82, 255, 0.1);
  border-color: rgba(0, 82, 255, 0.25);
}
</style>
