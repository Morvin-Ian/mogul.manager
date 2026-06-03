<template>
  <div class="team-page">
    <!-- Skeleton while loading -->
    <template v-if="loading">
      <div class="member-table">
        <div class="table-head">
          <span class="th th-member">Member</span>
          <span class="th th-joined">Date joined</span>
          <span class="th th-role">Role</span>
          <span class="th th-actions"></span>
        </div>
        <div class="table-body">
          <div v-for="n in 5" :key="n" class="table-row sk-row">
            <div class="td td-member">
              <div class="sk sk-avatar"></div>
              <div class="sk-member-col">
                <div class="sk sk-name"></div>
                <div class="sk sk-email"></div>
              </div>
            </div>
            <div class="td td-joined"><div class="sk sk-date"></div></div>
            <div class="td td-role"><div class="sk sk-role"></div></div>
            <div class="td td-actions"><div class="sk sk-action-btn"></div></div>
          </div>
        </div>
      </div>
    </template>

    <template v-else-if="workspace">
      <!-- Header -->
      <div class="page-head">
        <div class="page-head-left">
          <button class="back-pill" @click="$router.push(`/workspaces/${workspace.uuid}`)">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M8.5 2.5L4 7l4.5 4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ workspace.title }}
          </button>
          <div class="page-title-row">
            <h2>Manage Team</h2>
            <span class="member-count-badge">{{ members.length }} member{{ members.length !== 1 ? 's' : '' }}</span>
          </div>
          <p class="page-subtitle">Manage your members, invite people, and assign roles.</p>
        </div>
        <button v-if="isAdmin" class="invite-btn" @click="showInviteModal = true">
          <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
            <path d="M10.5 8a3 3 0 100-6 3 3 0 000 6zM14.5 13.5c0-2.21-1.79-4-4-4h-1M6 11l1.5 1.5L10 9" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Invite member
        </button>
      </div>

      <AiNudge
        storage-key="team"
        label="✨ AI can help you manage your team"
        :prompts="[
          'Who has the most tasks assigned to them?',
          'Which team member has overdue tasks?',
          'Reassign all tasks from one member to another',
          'Show me all tasks with no assignee',
        ]"
      />

      <!-- Search + filter bar -->
      <div class="controls-bar">
        <div class="search-wrap">
          <svg class="search-icon" viewBox="0 0 16 16" fill="none" width="14" height="14">
            <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.4"/>
            <path d="M11 11l3 3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          <input
            v-model="search"
            class="search-input"
            placeholder="Search members…"
            type="text"
          />
          <button v-if="search" class="search-clear" @click="search = ''">×</button>
        </div>
        <div class="filter-tabs">
          <button
            v-for="tab in roleTabs"
            :key="tab.value"
            class="filter-tab"
            :class="{ active: roleFilter === tab.value }"
            @click="roleFilter = tab.value"
          >
            {{ tab.label }}
            <span class="tab-count">{{ tabCount(tab.value) }}</span>
          </button>
        </div>
      </div>

      <!-- Members table -->
      <div class="member-table">
        <div class="table-head">
          <span class="th th-member">Member</span>
          <span class="th th-joined">Date joined</span>
          <span class="th th-role">Role</span>
          <span class="th th-actions"></span>
        </div>

        <div class="table-body">
          <div v-if="filteredMembers.length === 0" class="table-empty">
            No members match your search.
          </div>
          <div
            v-for="m in filteredMembers"
            :key="m.user_id"
            class="table-row"
          >
            <!-- Member col -->
            <div class="td td-member">
              <div
                class="member-avatar"
                :style="m.user?.profile_path ? {} : { background: avatarGradient(m.user?.username || '') }"
              >
                <img v-if="m.user?.profile_path" :src="m.user.profile_path" :alt="m.user?.username" />
                <template v-else>{{ (m.user?.username || '?').charAt(0).toUpperCase() }}</template>
              </div>
              <div class="member-info">
                <div class="member-name-row">
                  <span class="member-name">{{ m.user?.username }}</span>
                  <span v-if="m.user_id === auth.user?.id" class="you-chip">You</span>
                </div>
                <span class="member-email">{{ m.user?.email }}</span>
              </div>
            </div>

            <!-- Joined col -->
            <div class="td td-joined">
              <span class="joined-date">{{ shortDate(m.joined_at) }}</span>
              <span v-if="m.last_seen_at" class="last-seen">Active {{ timeAgo(m.last_seen_at) }}</span>
            </div>

            <!-- Role col -->
            <div class="td td-role">
              <span class="role-chip" :class="`role-${m.role}`">{{ m.role }}</span>
            </div>

            <!-- Actions col -->
            <div class="td td-actions">
              <template v-if="isAdmin && m.role !== 'owner'">
                <select
                  :value="m.role"
                  class="role-select"
                  @change="handleRoleChange(m.user_id, ($event.target as HTMLSelectElement).value)"
                >
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                </select>
                <button
                  v-if="m.user_id !== auth.user?.id"
                  class="remove-btn"
                  @click="handleRemove(m.user_id)"
                  title="Remove member"
                >
                  <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
                    <path d="M2 3.5h10M5.5 3.5V2.5a1 1 0 011-1h1a1 1 0 011 1v1M3 3.5l.7 7a1 1 0 001 .9h4.6a1 1 0 001-.9l.7-7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending invitations -->
      <div v-if="isAdmin" class="invitations-section">
        <div class="inv-section-head">
          <h3>Pending invitations</h3>
          <span class="count-chip">{{ invitations.length }}</span>
        </div>

        <div v-if="invitations.length === 0" class="inv-empty">
          No pending invitations.
        </div>
        <div v-else class="inv-table">
          <div class="inv-table-head">
            <span class="th">Email</span>
            <span class="th">Role</span>
            <span class="th">Status</span>
            <span class="th"></span>
          </div>
          <div v-for="inv in invitations" :key="inv.id" class="inv-row">
            <div class="inv-email-cell">
              <div class="inv-avatar">
                {{ inv.email.charAt(0).toUpperCase() }}
              </div>
              <span class="inv-email">{{ inv.email }}</span>
            </div>
            <span class="role-chip" :class="`role-${inv.role}`">{{ inv.role }}</span>
            <span class="inv-status-chip" :class="`inv-${inv.status}`">{{ inv.status }}</span>
            <button class="revoke-btn" @click="handleRevoke(inv.id)">Revoke</button>
          </div>
        </div>
      </div>
    </template>

    <!-- Invite modal -->
    <div v-if="showInviteModal" class="modal-overlay" @click.self="showInviteModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Invite member</h2>
          <button class="modal-close" @click="showInviteModal = false">×</button>
        </div>
        <p class="modal-hint">They'll receive an email invite. If they don't have an account yet, they can sign up and the workspace will be waiting.</p>
        <div class="form-group">
          <label>Email address</label>
          <input
            v-model="inviteEmail"
            type="email"
            placeholder="colleague@company.com"
            class="form-input"
            @keyup.enter="handleInvite"
            autofocus
          />
        </div>
        <div class="form-group">
          <label>Role</label>
          <div class="role-picker">
            <button
              class="role-option"
              :class="{ selected: inviteRole === 'member' }"
              @click="inviteRole = 'member'"
            >
              <strong>Member</strong>
              <span>Can view and create tasks</span>
            </button>
            <button
              class="role-option"
              :class="{ selected: inviteRole === 'admin' }"
              @click="inviteRole = 'admin'"
            >
              <strong>Admin</strong>
              <span>Can manage projects and members</span>
            </button>
          </div>
        </div>
        <p v-if="inviteErr" class="form-error">{{ inviteErr }}</p>
        <div class="form-actions">
          <button class="btn" @click="showInviteModal = false">Cancel</button>
          <button class="btn btn-primary" @click="handleInvite" :disabled="inviting || !inviteEmail.trim()">
            <span v-if="inviting" class="spinner spinner-white"></span>
            {{ inviting ? 'Sending…' : 'Send invite' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWorkspaceStore } from '../stores/workspaces'
import { useMembersStore } from '../stores/members'
import { useAuthStore } from '../stores/auth'
import { useConfirm } from '../composables/useConfirm'
import type { MemberRole } from '../types'
import AiNudge from '../components/common/AiNudge.vue'

const route = useRoute()
const router = useRouter()
const workspaceStore = useWorkspaceStore()
const membersStore = useMembersStore()
const auth = useAuthStore()
const { confirm } = useConfirm()

const workspaceId = computed(() => route.params.id as string)
const workspace = computed(() => workspaceStore.current)
const members = computed(() => membersStore.members)
const invitations = computed(() => membersStore.invitations)
const membership = computed(() => membersStore.myMembership)
const isAdmin = computed(() => membership.value?.role === 'admin' || membership.value?.role === 'owner')

const loading = ref(true)
const search = ref('')
const roleFilter = ref('all')
const showInviteModal = ref(false)
const inviteEmail = ref('')
const inviteRole = ref<MemberRole>('member')
const inviting = ref(false)
const inviteErr = ref<string | null>(null)

const roleTabs = [
  { label: 'All', value: 'all' },
  { label: 'Owner', value: 'owner' },
  { label: 'Admin', value: 'admin' },
  { label: 'Member', value: 'member' },
]

const filteredMembers = computed(() => {
  const q = search.value.toLowerCase()
  return members.value.filter(m => {
    const matchSearch = !q ||
      (m.user?.username || '').toLowerCase().includes(q) ||
      (m.user?.email || '').toLowerCase().includes(q)
    const matchRole = roleFilter.value === 'all' || m.role === roleFilter.value
    return matchSearch && matchRole
  })
})

function tabCount(role: string): number {
  if (role === 'all') return members.value.length
  return members.value.filter(m => m.role === role).length
}

onMounted(async () => {
  try {
    await workspaceStore.fetchOne(workspaceId.value)
    await membersStore.fetchMyMembership(workspaceId.value)
    await membersStore.fetchMembers(workspaceId.value)
    if (isAdmin.value) await membersStore.fetchInvitations(workspaceId.value)
  } catch { router.push('/') }
  finally { loading.value = false }
})

async function handleInvite() {
  if (!inviteEmail.value.trim()) return
  inviting.value = true
  inviteErr.value = null
  try {
    await membersStore.invite(workspaceId.value, inviteEmail.value, inviteRole.value)
    inviteEmail.value = ''
    showInviteModal.value = false
  } catch (e) {
    inviteErr.value = (e as Error).message
  } finally { inviting.value = false }
}

const AVATAR_GRADIENTS = [
  'linear-gradient(135deg,#6366F1,#8B5CF6)',
  'linear-gradient(135deg,#0EA5E9,#2563EB)',
  'linear-gradient(135deg,#10B981,#059669)',
  'linear-gradient(135deg,#F59E0B,#D97706)',
  'linear-gradient(135deg,#EF4444,#DC2626)',
  'linear-gradient(135deg,#0D9488,#0891B2)',
]
function avatarGradient(name: string): string {
  let hash = 0
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) & 0xffffffff
  return AVATAR_GRADIENTS[Math.abs(hash) % AVATAR_GRADIENTS.length]
}
function shortDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
function timeAgo(iso: string) {
  const s = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (s < 60) return 'just now'
  if (s < 3600) return `${Math.floor(s/60)}m ago`
  if (s < 86400) return `${Math.floor(s/3600)}h ago`
  return `${Math.floor(s/86400)}d ago`
}
async function handleRoleChange(userId: number, role: string) {
  await membersStore.updateRole(workspaceId.value, userId, role as MemberRole)
}
async function handleRemove(userId: number) {
  const member = members.value.find(m => m.user_id === userId)
  const ok = await confirm({
    title: 'Remove member?',
    message: `${member?.user?.username || 'This member'} will lose access to this workspace and all its projects.`,
    confirmLabel: 'Remove member',
    cancelLabel: 'Cancel',
    danger: true,
  })
  if (!ok) return
  await membersStore.removeMember(workspaceId.value, userId)
}
async function handleRevoke(invitationId: number) {
  const inv = invitations.value.find(i => i.id === invitationId)
  const ok = await confirm({
    title: 'Revoke invitation?',
    message: `The invite sent to ${inv?.email || 'this address'} will be cancelled.`,
    confirmLabel: 'Revoke invite',
    cancelLabel: 'Keep it',
    danger: false,
  })
  if (!ok) return
  await membersStore.revokeInvitation(workspaceId.value, invitationId)
}
</script>

<style scoped>
.team-page {
  padding: 36px 40px 80px;
}

/* ── Header ── */
.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}
.page-head-left { flex: 1; min-width: 0; }
.back-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: inherit;
  margin-bottom: 12px;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.back-pill:hover { background: var(--bg); color: var(--text); border-color: var(--border-strong); }

.page-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 5px;
}
.page-title-row h2 {
  font-size: 24px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.6px;
}
.member-count-badge {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg);
  border: 1.5px solid var(--border);
  padding: 3px 10px;
  border-radius: var(--radius-full);
}
.page-subtitle { font-size: 13.5px; color: var(--text-muted); }

.invite-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 18px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  white-space: nowrap;
  flex-shrink: 0;
  transition: opacity 0.15s, transform 0.1s;
}
.invite-btn:hover { opacity: 0.82; }
.invite-btn:active { transform: scale(0.97); }

/* ── Controls bar ── */
.controls-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 200px;
  max-width: 320px;
}
.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-light);
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 9px 12px 9px 34px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-full);
  font-size: 13.5px;
  font-family: inherit;
  background: var(--surface);
  color: var(--text);
  transition: border-color 0.15s;
}
.search-input:focus { outline: none; border-color: var(--primary); }
.search-input::placeholder { color: var(--text-light); }
.search-clear {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: var(--text-light);
  line-height: 1;
  padding: 2px 4px;
}
.filter-tabs {
  display: flex;
  gap: 4px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-full);
  padding: 3px;
}
.filter-tab {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 13px;
  border-radius: var(--radius-full);
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-muted);
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, color 0.12s;
}
.filter-tab:hover { color: var(--text); }
.filter-tab.active { background: var(--surface); color: var(--text); box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.tab-count {
  font-size: 10.5px;
  font-weight: 700;
  color: var(--text-light);
  background: var(--border);
  padding: 1px 5px;
  border-radius: 999px;
}
.filter-tab.active .tab-count { background: var(--bg); }

/* ── Member table ── */
.member-table {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 20px;
}
.table-head {
  display: grid;
  grid-template-columns: 1fr 200px 130px 160px;
  padding: 11px 20px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
}
.th {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}
.table-empty {
  padding: 40px;
  text-align: center;
  font-size: 13.5px;
  color: var(--text-muted);
}
.table-row {
  display: grid;
  grid-template-columns: 1fr 200px 130px 160px;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.table-row:last-child { border-bottom: none; }
.table-row:hover { background: var(--bg); }

.td { display: flex; align-items: center; }
.td-member { gap: 12px; }

.member-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 800;
  color: #fff;
  flex-shrink: 0;
  overflow: hidden;
  letter-spacing: -0.3px;
}
.member-avatar img {
  width: 100%; height: 100%; object-fit: cover;
}
.member-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.member-name-row { display: flex; align-items: center; gap: 6px; }
.member-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.member-email { font-size: 12px; color: var(--text-muted); }
.you-chip {
  font-size: 9.5px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 999px;
  background: var(--primary-light, #EEF3FF);
  color: var(--primary);
  border: 1px solid var(--primary-border, #C0D0FF);
  letter-spacing: 0.2px;
  flex-shrink: 0;
}

.td-joined {
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: flex-start;
}
.joined-date { font-size: 12.5px; color: var(--text-muted); }
.last-seen { font-size: 11px; color: var(--text-light); }

.role-chip {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  text-transform: capitalize;
  border: 1px solid;
}
.role-owner  { background: #FEF3C7; color: #92400E; border-color: #FDE68A; }
.role-admin  { background: #DBEAFE; color: #1E40AF; border-color: #BFDBFE; }
.role-member { background: var(--bg); color: var(--text-muted); border-color: var(--border); }

.td-actions { gap: 6px; justify-content: flex-end; }
.role-select {
  font-size: 12px;
  padding: 5px 8px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--text);
  font-family: inherit;
  cursor: pointer;
}
.remove-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-light);
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.remove-btn:hover {
  background: var(--danger-bg);
  color: var(--danger);
  border-color: var(--danger-border);
}

/* ── Invitations section ── */
.invitations-section {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.inv-section-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg);
}
.inv-section-head h3 {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.count-chip {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-light);
  background: var(--border);
  padding: 2px 7px;
  border-radius: 999px;
}
.inv-empty {
  padding: 28px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}
.inv-table-head {
  display: grid;
  grid-template-columns: 1fr 130px 130px 100px;
  padding: 9px 20px;
  border-bottom: 1px solid var(--border);
}
.inv-row {
  display: grid;
  grid-template-columns: 1fr 130px 130px 100px;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.inv-row:last-child { border-bottom: none; }
.inv-row:hover { background: var(--bg); }
.inv-email-cell { display: flex; align-items: center; gap: 10px; }
.inv-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--border);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}
.inv-email { font-size: 13.5px; color: var(--text); }
.inv-status-chip {
  display: inline-flex;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: var(--radius-full);
  text-transform: capitalize;
  border: 1px solid;
}
.inv-pending  { background: #FFFBEB; color: #92400E; border-color: #FDE68A; }
.inv-accepted { background: #ECFDF5; color: #065F46; border-color: #A7F3D0; }
.inv-expired  { background: var(--bg); color: var(--text-light); border-color: var(--border); }
.inv-revoked  { background: #FFF1F2; color: #BE123C; border-color: #FECDD3; }
.revoke-btn {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 600;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--border);
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.revoke-btn:hover {
  background: var(--danger-bg);
  color: var(--danger);
  border-color: var(--danger-border);
}

/* ── Invite modal ── */
.role-picker {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.role-option {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 14px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  transition: border-color 0.12s, background 0.12s;
}
.role-option strong { font-size: 13.5px; color: var(--text); font-weight: 700; }
.role-option span { font-size: 12px; color: var(--text-muted); line-height: 1.4; }
.role-option:hover { border-color: var(--border-strong); }
.role-option.selected { border-color: var(--primary); background: var(--primary-light, #EEF3FF); }
.role-option.selected strong { color: var(--primary); }

.spinner { display: inline-block; width: 13px; height: 13px; border: 2px solid rgba(255,255,255,.3); border-top-color: #fff; border-radius: 50%; animation: spin .65s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Dark mode ── */
:global([data-theme="dark"]) .member-table,
:global([data-theme="dark"]) .invitations-section { background: rgba(30,39,50,0.8); }
:global([data-theme="dark"]) .table-head,
:global([data-theme="dark"]) .inv-section-head,
:global([data-theme="dark"]) .inv-table-head { background: rgba(255,255,255,0.03); }
:global([data-theme="dark"]) .table-row:hover,
:global([data-theme="dark"]) .inv-row:hover { background: rgba(255,255,255,0.04); }
:global([data-theme="dark"]) .filter-tabs { background: rgba(255,255,255,0.05); }
:global([data-theme="dark"]) .filter-tab.active { background: rgba(255,255,255,0.1); }
:global([data-theme="dark"]) .invite-btn { background: #F7F9F9; color: #15202B; }
:global([data-theme="dark"]) .invite-btn:hover { opacity: 0.9; }
:global([data-theme="dark"]) .role-owner { background: rgba(251,191,36,0.15); border-color: rgba(251,191,36,0.3); }
:global([data-theme="dark"]) .role-admin { background: rgba(59,130,246,0.15); border-color: rgba(59,130,246,0.3); }
:global([data-theme="dark"]) .role-member { background: rgba(255,255,255,0.06); border-color: var(--border); }
:global([data-theme="dark"]) .inv-pending { background: rgba(251,191,36,0.12); border-color: rgba(251,191,36,0.3); }
:global([data-theme="dark"]) .inv-accepted { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.3); }

@media (max-width: 768px) {
  .team-page { padding: 20px 16px 60px; }
  .table-head { display: none; }
  .table-row { grid-template-columns: 1fr; gap: 10px; padding: 16px; }
  .td-joined { display: none; }
  .page-head { flex-direction: column; }
  .controls-bar { flex-direction: column; align-items: stretch; }
  .search-wrap { max-width: 100%; }
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
.sk-avatar     { width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0; }
.sk-member-col { display: flex; flex-direction: column; gap: 5px; flex: 1; }
.sk-name       { height: 13px; width: 120px; }
.sk-email      { height: 11px; width: 170px; }
.sk-date       { height: 12px; width: 80px; }
.sk-role       { height: 22px; width: 64px; border-radius: 99px; }
.sk-action-btn { height: 28px; width: 80px; border-radius: 8px; }
</style>
