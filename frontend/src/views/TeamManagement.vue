<template>
  <div class="team-page">
    <Loading v-if="loading" label="Loading team…" />

    <template v-else-if="workspace">
      <div class="page-head">
        <div>
          <button class="back-pill" @click="$router.push(`/workspaces/${workspace.id}`)">
            <font-awesome-icon :icon="['fas', 'chevron-left']" />
            {{ workspace.title }}
          </button>
          <h2>Team</h2>
        </div>
        <div class="page-actions">
          <button v-if="isAdmin" class="invite-btn" @click="showInviteForm = true">
            <font-awesome-icon :icon="['fas', 'user-plus']" />
            Invite
          </button>
        </div>
      </div>

      <!-- Invite form -->
      <div v-if="showInviteForm" class="invite-form-card">
        <h3>Invite someone</h3>
        <div class="invite-form-row">
          <input
            v-model="inviteEmail"
            type="email"
            placeholder="Email address"
            class="invite-input"
            @keyup.enter="handleInvite"
          />
          <select v-model="inviteRole" class="invite-select">
            <option value="member">Member</option>
            <option value="admin">Admin</option>
          </select>
          <button class="btn btn-primary btn-sm" @click="handleInvite" :disabled="inviting">
            {{ inviting ? 'Sending…' : 'Send invite' }}
          </button>
        </div>
        <p v-if="inviteErr" class="form-error">{{ inviteErr }}</p>
      </div>

      <!-- Members list -->
      <section class="team-section">
        <h3>Members <span class="count-badge">{{ members.length }}</span></h3>
        <div v-if="members.length === 0" class="empty-section">No members yet.</div>
        <div v-else class="member-list">
          <div v-for="m in members" :key="m.user_id" class="member-card">
            <div class="member-card-left">
              <div class="member-avatar" :style="m.user?.profile_path ? {} : { background: avatarGradient(m.user?.username || '') }">
                <img v-if="m.user?.profile_path" :src="m.user.profile_path" class="member-avatar-img" :alt="m.user?.username" />
                <template v-else>{{ (m.user?.username || '?').charAt(0).toUpperCase() }}</template>
              </div>
              <div class="member-details">
                <div class="member-name-row">
                  <span class="member-name">{{ m.user?.username }}</span>
                  <span v-if="m.user_id === auth.user?.id" class="you-chip">You</span>
                  <span class="role-tag" :class="`role-${m.role}`">{{ m.role }}</span>
                </div>
                <span class="member-email">{{ m.user?.email }}</span>
                <div class="member-meta">
                  <span class="meta-item">
                    <font-awesome-icon :icon="['fas', 'calendar']" />
                    Joined {{ shortDate(m.joined_at) }}
                  </span>
                  <span v-if="m.last_seen_at" class="meta-item">
                    <font-awesome-icon :icon="['fas', 'clock']" />
                    Active {{ timeAgo(m.last_seen_at) }}
                  </span>
                </div>
              </div>
            </div>
            <div v-if="isAdmin && m.role !== 'owner'" class="member-card-actions">
              <select
                :value="m.role"
                @change="handleRoleChange(m.user_id, ($event.target as HTMLSelectElement).value)"
                class="role-select"
              >
                <option value="member">Member</option>
                <option value="admin">Admin</option>
              </select>
              <button
                v-if="m.user_id !== auth.user?.id"
                class="btn btn-sm btn-danger"
                @click="handleRemove(m.user_id)"
              >
                Remove
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Invitations list -->
      <section v-if="isAdmin" class="team-section">
        <h3>Pending invitations <span class="count-badge">{{ invitations.length }}</span></h3>
        <div v-if="invitations.length === 0" class="empty-section">No pending invitations.</div>
        <div v-else class="invitation-list">
          <div v-for="inv in invitations" :key="inv.id" class="invitation-row">
            <font-awesome-icon :icon="['fas', 'envelope']" class="inv-icon" />
            <span class="inv-email">{{ inv.email }}</span>
            <span class="role-tag" :class="`role-${inv.role}`">{{ inv.role }}</span>
            <span class="inv-status" :class="`status-${inv.status}`">{{ inv.status }}</span>
            <button class="btn btn-sm btn-danger" @click="handleRevoke(inv.id)">Revoke</button>
          </div>
        </div>
      </section>
    </template>
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
import Loading from '../components/common/Loading.vue'

const route = useRoute()
const router = useRouter()
const workspaceStore = useWorkspaceStore()
const membersStore = useMembersStore()
const auth = useAuthStore()
const { confirm } = useConfirm()

const workspaceId = computed(() => Number(route.params.id))
const workspace = computed(() => workspaceStore.current)
const members = computed(() => membersStore.members)
const invitations = computed(() => membersStore.invitations)
const membership = computed(() => membersStore.myMembership)
const isAdmin = computed(() => membership.value?.role === 'admin' || membership.value?.role === 'owner')

const loading = ref(true)
const showInviteForm = ref(false)
const inviteEmail = ref('')
const inviteRole = ref<MemberRole>('member')
const inviting = ref(false)
const inviteErr = ref<string | null>(null)

onMounted(async () => {
  try {
    await workspaceStore.fetchOne(workspaceId.value)
    await membersStore.fetchMyMembership(workspaceId.value)
    await membersStore.fetchMembers(workspaceId.value)
    if (isAdmin.value) {
      await membersStore.fetchInvitations(workspaceId.value)
    }
  } catch (e) {
    router.push('/')
  } finally {
    loading.value = false
  }
})

async function handleInvite() {
  if (!inviteEmail.value.trim()) return
  inviting.value = true
  inviteErr.value = null
  try {
    await membersStore.invite(workspaceId.value, inviteEmail.value, inviteRole.value)
    inviteEmail.value = ''
    showInviteForm.value = false
  } catch (e) {
    inviteErr.value = (e as Error).message
  } finally {
    inviting.value = false
  }
}

const AVATAR_GRADIENTS = [
  'linear-gradient(135deg, #6366F1, #8B5CF6)',
  'linear-gradient(135deg, #0EA5E9, #2563EB)',
  'linear-gradient(135deg, #10B981, #059669)',
  'linear-gradient(135deg, #F59E0B, #D97706)',
  'linear-gradient(135deg, #EF4444, #DC2626)',
  'linear-gradient(135deg, #EC4899, #DB2777)',
]

function avatarGradient(name: string): string {
  let hash = 0
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) & 0xffffffff
  return AVATAR_GRADIENTS[Math.abs(hash) % AVATAR_GRADIENTS.length]
}

function shortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function timeAgo(iso: string): string {
  const secs = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (secs < 60) return 'just now'
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`
  return `${Math.floor(secs / 86400)}d ago`
}

async function handleRoleChange(userId: number, role: string) {
  await membersStore.updateRole(workspaceId.value, userId, role as MemberRole)
}

async function handleRemove(userId: number) {
  const member = members.value.find((m) => m.user_id === userId)
  const name = member?.user?.username || 'this member'
  const ok = await confirm({
    title: 'Remove member?',
    message: `${name} will lose access to this workspace and all its projects.`,
    confirmLabel: 'Remove member',
    cancelLabel: 'Cancel',
    danger: true,
  })
  if (!ok) return
  await membersStore.removeMember(workspaceId.value, userId)
}

async function handleRevoke(invitationId: number) {
  const inv = invitations.value.find((i) => i.id === invitationId)
  const email = inv?.email || 'this invitation'
  const ok = await confirm({
    title: 'Revoke invitation?',
    message: `The invite sent to ${email} will be cancelled. They won't be able to join with this link.`,
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
  padding: 36px 36px 80px;
  max-width: 800px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 28px;
}

.page-head h2 {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.6px;
  margin-top: 12px;
}

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
  transition: opacity 0.15s, transform 0.1s;
  white-space: nowrap;
}
.invite-btn:hover { opacity: 0.82; }
.invite-btn:active { transform: scale(0.97); }
:global([data-theme="dark"]) .invite-btn { background: #F7F9F9; color: #15202B; }

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
  transition: background 0.12s, color 0.12s, border-color 0.12s;
  align-self: flex-start;
}
.back-pill:hover { background: var(--bg); color: var(--text); border-color: var(--border-strong); }

.invite-form-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin-bottom: 24px;
}
.invite-form-card h3 { font-size: 14px; font-weight: 700; margin-bottom: 12px; }

.invite-form-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.invite-input {
  flex: 1;
  padding: 8px 12px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13.5px;
  font-family: inherit;
  background: var(--bg);
  color: var(--text);
}
.invite-input:focus { border-color: var(--primary); outline: none; }
.invite-select {
  padding: 8px 10px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  background: var(--bg);
  color: var(--text);
}

.team-section {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin-bottom: 16px;
}
.team-section h3 {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.count-badge {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  padding: 1px 7px;
  font-size: 11px;
  color: var(--text-light);
}

.empty-section { font-size: 13.5px; color: var(--text-muted); text-align: center; padding: 20px 0; }

.member-list, .invitation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Rich member card */
.member-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.member-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

.member-card-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.member-avatar {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  font-weight: 800;
  flex-shrink: 0;
  letter-spacing: -0.5px;
  overflow: hidden;
}

.member-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 14px;
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.member-name-row {
  display: flex;
  align-items: center;
  gap: 7px;
  flex-wrap: wrap;
}

.member-name {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
}

.you-chip {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
  background: var(--primary-light);
  color: var(--primary);
  border: 1px solid var(--primary-border);
  letter-spacing: 0.2px;
}

.member-email {
  font-size: 12.5px;
  color: var(--text-muted);
}

.member-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 2px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-light);
  font-weight: 500;
}

.role-tag {
  display: inline-flex;
  align-items: center;
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: var(--radius-full);
  text-transform: capitalize;
  letter-spacing: 0.1px;
}
.role-owner { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
.role-admin { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
.role-member { background: #F0F2F5; color: #374151; border: 1px solid #E2E8F0; }

.member-card-actions {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-shrink: 0;
}

.invitation-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  transition: background 0.1s;
}
.invitation-row:hover { background: var(--bg); }

.role-select {
  font-size: 11px;
  padding: 4px 6px;
  border: 1.5px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
  font-family: inherit;
}

.inv-icon { color: var(--text-light); flex-shrink: 0; font-size: 11px; }
.inv-email { flex: 1; font-size: 13.5px; color: var(--text); }

.inv-status {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  text-transform: capitalize;
}
.status-pending { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.status-accepted { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
.status-expired { background: #F0F2F5; color: #6B7280; border: 1px solid #E2E8F0; }
.status-revoked { background: #FFF1F2; color: #BE123C; border: 1px solid #FECDD3; }
</style>
