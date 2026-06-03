<template>
  <div class="team-hub">
    <div class="page-head">
      <div class="page-head-text">
        <h2>Team</h2>
        <p>Manage members and roles across your workspaces.</p>
      </div>
    </div>

    <!-- Skeleton table while loading -->
    <template v-if="loading">
      <div class="ws-table">
        <div class="ws-table-head">
          <span class="th th-workspace">Workspace</span>
          <span class="th th-created">Created</span>
          <span class="th th-role">Your role</span>
          <span class="th th-actions"></span>
        </div>
        <div class="ws-table-body">
          <div v-for="n in 4" :key="n" class="ws-row sk-row">
            <div class="td td-workspace">
              <div class="sk sk-avatar"></div>
              <div class="sk-info-col">
                <div class="sk sk-ws-name"></div>
                <div class="sk sk-ws-desc"></div>
              </div>
            </div>
            <div class="td td-created"><div class="sk sk-date"></div></div>
            <div class="td td-role"><div class="sk sk-role"></div></div>
            <div class="td td-actions">
              <div class="sk sk-btn"></div>
              <div class="sk sk-btn sk-btn-wide"></div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div v-if="workspaces.length === 0" class="empty-state">
        <div class="empty-icon">
          <font-awesome-icon :icon="['fas', 'users']" />
        </div>
        <h3>No workspaces yet</h3>
        <p>Create a workspace to start building your team.</p>
        <button class="btn btn-primary" @click="$router.push('/workspaces')">Create workspace</button>
      </div>

      <template v-else>
        <!-- Workspace table -->
        <div class="ws-table">
          <div class="ws-table-head">
            <span class="th th-workspace">Workspace</span>
            <span class="th th-created">Created</span>
            <span class="th th-role">Your role</span>
            <span class="th th-actions"></span>
          </div>
          <div class="ws-table-body">
            <div
              v-for="ws in workspaces"
              :key="ws.id"
              class="ws-row"
              @click="$router.push(`/team/${ws.uuid}`)"
            >
              <div class="td td-workspace">
                <div class="ws-avatar" :style="avatarStyle(ws.id)">
                  {{ ws.title.charAt(0).toUpperCase() }}
                </div>
                <div class="ws-info">
                  <span class="ws-name">{{ ws.title }}</span>
                  <span v-if="ws.description" class="ws-desc">{{ ws.description }}</span>
                </div>
              </div>
              <div class="td td-created">{{ formatDate(ws.created_at) }}</div>
              <div class="td td-role">
                <span class="role-chip" :class="ws.user_id === auth.user?.id ? 'role-owner' : 'role-member'">
                  {{ ws.user_id === auth.user?.id ? 'Owner' : 'Member' }}
                </span>
              </div>
              <div class="td td-actions" @click.stop>
                <button class="row-btn" @click="$router.push(`/workspaces/${ws.uuid}`)">Open</button>
                <button class="row-btn row-btn-primary" @click="$router.push(`/team/${ws.uuid}`)">
                  <font-awesome-icon :icon="['fas', 'users']" />
                  Manage team
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tip -->
        <div v-if="hasOwnedWorkspaces" class="tip-card">
          <div class="tip-icon-wrap">
            <font-awesome-icon :icon="['fas', 'lightbulb']" />
          </div>
          <p>
            <strong>Invite teammates</strong> — click "Manage team" on any workspace you own to invite
            people by email. They'll receive an invite link and can join even without an existing account.
          </p>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useWorkspaceStore } from '../stores/workspaces'
import { useAuthStore } from '../stores/auth'

const workspaceStore = useWorkspaceStore()
const auth = useAuthStore()
const loading = ref(true)

onMounted(async () => {
  try { await workspaceStore.fetchAll() } finally { loading.value = false }
})

const workspaces = computed(() => workspaceStore.workspaces)
const hasOwnedWorkspaces = computed(() => workspaces.value.some(ws => ws.user_id === auth.user?.id))

const AVATAR_COLORS = [
  ['#0052FF','#003CBF'], ['#7C3AED','#5B21B6'], ['#059669','#047857'],
  ['#DC2626','#B91C1C'], ['#D97706','#B45309'], ['#0891B2','#0E7490'],
]
function avatarStyle(id: number) {
  const [a, b] = AVATAR_COLORS[id % AVATAR_COLORS.length]
  return { background: `linear-gradient(135deg, ${a}, ${b})` }
}
function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.team-hub {
  padding: 36px 40px 80px;
}

/* ── Header ── */
.page-head { margin-bottom: 28px; }
.page-head h2 {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.6px;
  margin-bottom: 4px;
}
.page-head p { font-size: 13.5px; color: var(--text-muted); }

/* ── Table ── */
.ws-table {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 20px;
}
.ws-table-head {
  display: grid;
  grid-template-columns: 1fr 160px 130px 220px;
  padding: 11px 20px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
}
.th {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.ws-row {
  display: grid;
  grid-template-columns: 1fr 160px 130px 220px;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.12s;
}
.ws-row:last-child { border-bottom: none; }
.ws-row:hover { background: var(--bg); }

.td { display: flex; align-items: center; }
.td-workspace { gap: 13px; }

.ws-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 800;
  color: #fff;
  flex-shrink: 0;
}
.ws-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.ws-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ws-desc {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 280px;
}
.td-created { font-size: 12.5px; color: var(--text-muted); }

.role-chip {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  text-transform: capitalize;
  letter-spacing: 0.1px;
  border: 1px solid;
}
.role-owner  { background: #FEF3C7; color: #92400E; border-color: #FDE68A; }
.role-member { background: var(--bg); color: var(--text-muted); border-color: var(--border); }

.td-actions { gap: 7px; justify-content: flex-end; }
.row-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  font-size: 12.5px;
  font-weight: 600;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, border-color 0.12s, color 0.12s;
  white-space: nowrap;
}
.row-btn:hover { background: var(--bg); color: var(--text); border-color: var(--border-strong); }
.row-btn-primary { background: #1c1c1e; border-color: #1c1c1e; color: #fff; }
.row-btn-primary:hover { background: #2e2e30; border-color: #2e2e30; color: #fff; }

/* ── Tip ── */
.tip-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: var(--primary-light, #EEF3FF);
  border: 1.5px solid var(--primary-border, #C0D0FF);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
}
.tip-icon-wrap {
  width: 32px; height: 32px;
  border-radius: 8px;
  background: var(--primary);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; flex-shrink: 0;
}
.tip-card p { font-size: 13px; color: var(--text); line-height: 1.6; margin: 3px 0 0; }

/* ── Empty ── */
.empty-state {
  text-align: center; padding: 80px 20px;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.empty-icon { font-size: 36px; color: var(--text-light); }
.empty-state h3 { font-size: 17px; font-weight: 700; color: var(--text); }
.empty-state p { font-size: 13.5px; color: var(--text-muted); }

/* ── Dark mode ── */
:global([data-theme="dark"]) .ws-table { background: rgba(30,39,50,0.8); }
:global([data-theme="dark"]) .ws-row:hover { background: rgba(255,255,255,0.04); }
:global([data-theme="dark"]) .ws-table-head { background: rgba(255,255,255,0.03); }
:global([data-theme="dark"]) .row-btn-primary { background: #F7F9F9; border-color: #F7F9F9; color: #15202B; }
:global([data-theme="dark"]) .row-btn-primary:hover { background: #e8eaeb; }
:global([data-theme="dark"]) .role-member { background: rgba(255,255,255,0.06); color: var(--text-muted); border-color: var(--border); }
:global([data-theme="dark"]) .tip-card { background: rgba(0,82,255,0.1); border-color: rgba(0,82,255,0.25); }

@media (max-width: 768px) {
  .team-hub { padding: 20px 16px 60px; }
  .ws-table-head { display: none; }
  .ws-row { grid-template-columns: 1fr; gap: 10px; }
  .td-created { display: none; }
}

/* ── Skeleton ── */
@keyframes sk-shimmer { 0%{background-position:-600px 0} 100%{background-position:600px 0} }
.sk {
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 600px 100%;
  animation: sk-shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
}
.sk-row { pointer-events: none; cursor: default; }
.sk-avatar    { width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0; }
.sk-info-col  { display: flex; flex-direction: column; gap: 5px; flex: 1; }
.sk-ws-name   { height: 14px; width: 140px; }
.sk-ws-desc   { height: 11px; width: 90px; }
.sk-date      { height: 12px; width: 70px; }
.sk-role      { height: 20px; width: 64px; border-radius: 99px; }
.sk-btn       { height: 28px; width: 56px; border-radius: 8px; }
.sk-btn-wide  { width: 110px; }
</style>
