<template>
  <div class="members-section">
    <div class="members-head">
      <div>
        <h3>Members</h3>
        <p class="members-sub">{{ membersStore.members.length }} member{{ membersStore.members.length !== 1 ? 's' : '' }}</p>
      </div>
      <button
        v-if="canManage"
        class="btn btn-sm btn-primary"
        @click="showInviteModal = true"
      >
        <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
          <path d="M7 1v12M1 7h12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
        Invite member
      </button>
    </div>

    <div v-if="membersStore.loading" class="members-loading">
      <div class="spinner"></div>
      <span>Loading members…</span>
    </div>

    <!-- Member list -->
    <div v-else class="members-list">
      <div
        v-for="member in membersStore.members"
        :key="member.id"
        class="member-row"
      >
        <div class="member-avatar" :style="member.user.profile_path ? {} : { background: avatarColor(member.user.username) }">
          <img v-if="member.user.profile_path" :src="member.user.profile_path" :alt="member.user.username" class="member-avatar-img" />
          <span v-else>{{ initials(member.user.username) }}</span>
        </div>
        <div class="member-info">
          <span class="member-name">{{ member.user.username }}</span>
          <span class="member-email">{{ member.user.email }}</span>
          <span v-if="member.last_seen_at" class="member-seen">Last seen {{ timeAgo(member.last_seen_at) }}</span>
        </div>
        <div class="member-right">
          <!-- Role: owner always shows badge, admins can change member/admin roles -->
          <select
            v-if="canManage && currentUserRole === 'owner' && member.role !== 'owner'"
            :value="member.role"
            class="role-select"
            @change="changeRole(member, ($event.target as HTMLSelectElement).value as MemberRole)"
          >
            <option value="member">Member</option>
            <option value="admin">Admin</option>
          </select>
          <span v-else class="badge" :class="roleBadgeClass(member.role)">{{ member.role }}</span>

          <span class="member-joined">Joined {{ shortDate(member.joined_at) }}</span>

          <button
            v-if="canRemove(member)"
            class="btn btn-sm btn-danger remove-btn"
            @click="confirmRemove(member)"
          >
            Remove
          </button>
        </div>
      </div>
    </div>

    <!-- Pending invitations -->
    <template v-if="canManage && membersStore.invitations.length > 0">
      <div class="invitations-head">
        <h4>Pending invitations</h4>
      </div>
      <div class="invitations-list">
        <div
          v-for="inv in pendingInvitations"
          :key="inv.id"
          class="invitation-row"
        >
          <div class="invitation-icon">
            <svg viewBox="0 0 20 20" fill="none" width="16" height="16">
              <path d="M3 4h14a1 1 0 011 1v10a1 1 0 01-1 1H3a1 1 0 01-1-1V5a1 1 0 011-1z" stroke="currentColor" stroke-width="1.4"/>
              <path d="M2 5l8 6 8-6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="invitation-info">
            <span class="inv-email">{{ inv.email }}</span>
            <span class="inv-meta">
              <span class="badge" :class="roleBadgeClass(inv.role)">{{ inv.role }}</span>
              · Expires {{ shortDate(inv.expires_at) }}
            </span>
          </div>
          <button class="btn btn-sm btn-danger" @click="handleRevoke(inv.id)">Revoke</button>
        </div>
      </div>
    </template>

    <InviteModal
      v-if="showInviteModal"
      :workspace-id="workspaceId"
      @close="onInviteClose"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useMembersStore } from '../../stores/members'
import { useAuthStore } from '../../stores/auth'
import { useConfirm } from '../../composables/useConfirm'
import type { WorkspaceMember, MemberRole } from '../../types'
import InviteModal from './InviteModal.vue'

const props = defineProps<{
  workspaceId: number
  currentUserRole: string
}>()

const membersStore = useMembersStore()
const auth = useAuthStore()
const { confirm } = useConfirm()
const showInviteModal = ref(false)

onMounted(() => {
  membersStore.fetchMembers(props.workspaceId)
  if (canManage.value) {
    membersStore.fetchInvitations(props.workspaceId)
  }
})

const canManage = computed(() => props.currentUserRole === 'owner' || props.currentUserRole === 'admin')

const pendingInvitations = computed(() =>
  membersStore.invitations.filter((i) => i.status === 'pending')
)

function canRemove(member: WorkspaceMember): boolean {
  if (member.role === 'owner') return false
  if (props.currentUserRole === 'owner') return true
  if (props.currentUserRole === 'admin' && member.role === 'member') return true
  return false
}

function initials(name: string): string {
  return name
    .split(/[\s_-]/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join('')
}

const AVATAR_COLORS = [
  '#2563EB', '#7C3AED', '#DB2777', '#D97706',
  '#16A34A', '#0891B2', '#DC2626', '#9333EA',
]

function avatarColor(name: string): string {
  let hash = 0
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) & 0xffffffff
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length]
}

function roleBadgeClass(role: string): string {
  if (role === 'owner') return 'badge-owner'
  if (role === 'admin') return 'badge-admin'
  return 'badge-member'
}

function shortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function timeAgo(iso: string): string {
  const secs = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (secs < 60) return 'just now'
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`
  if (secs < 2592000) return `${Math.floor(secs / 86400)}d ago`
  return shortDate(iso)
}

async function changeRole(member: WorkspaceMember, newRole: MemberRole) {
  await membersStore.updateRole(props.workspaceId, member.user_id, newRole)
}

async function confirmRemove(member: WorkspaceMember) {
  const ok = await confirm({
    title: 'Remove member?',
    message: `${member.user.username} will lose access to this workspace and all its projects.`,
    confirmLabel: 'Remove member',
    cancelLabel: 'Cancel',
    danger: true,
  })
  if (!ok) return
  await membersStore.removeMember(props.workspaceId, member.user_id)
}

async function handleRevoke(invitationId: number) {
  const inv = membersStore.invitations.find((i) => i.id === invitationId)
  const email = inv?.email || 'this invitation'
  const ok = await confirm({
    title: 'Revoke invitation?',
    message: `The invite sent to ${email} will be cancelled.`,
    confirmLabel: 'Revoke invite',
    cancelLabel: 'Keep it',
  })
  if (!ok) return
  await membersStore.revokeInvitation(props.workspaceId, invitationId)
}

function onInviteClose() {
  showInviteModal.value = false
  membersStore.fetchInvitations(props.workspaceId)
}
</script>

<style scoped>
.members-section {
  margin-top: 32px;
  padding-top: 28px;
  border-top: 1px solid var(--border);
}

.members-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.members-head h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}

.members-sub {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 2px;
}

.members-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
  font-size: 14px;
  padding: 20px 0;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

.members-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.member-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border-radius: 10px;
  transition: background 0.12s;
}

.member-row:hover {
  background: var(--bg);
}

.member-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
  letter-spacing: 0.5px;
  overflow: hidden;
}
.member-avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.member-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.member-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.member-email {
  font-size: 12.5px;
  color: var(--text-muted);
}

.member-seen {
  font-size: 11.5px;
  color: var(--text-light);
}

.member-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.member-joined {
  font-size: 12px;
  color: var(--text-light);
}

.remove-btn {
  font-size: 12px;
}

/* Role badges */
.badge {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 20px;
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.2px;
}

.badge-owner  { background: #F3E8FF; color: #7C3AED; }
.badge-admin  { background: #EFF6FF; color: #2563EB; }
.badge-member { background: var(--bg); color: var(--text-muted); border: 1px solid var(--border); }

/* Role select dropdown */
.role-select {
  font-size: 12.5px;
  font-weight: 600;
  padding: 3px 8px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: var(--bg);
  color: var(--text);
  cursor: pointer;
  outline: none;
}

.role-select:focus {
  border-color: var(--primary);
}

/* Invitations */
.invitations-head {
  margin-top: 24px;
  margin-bottom: 12px;
}

.invitations-head h4 {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.invitations-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.invitation-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--bg);
  border: 1px solid var(--border);
}

.invitation-icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--surface);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  flex-shrink: 0;
}

.invitation-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.inv-email {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text);
}

.inv-meta {
  font-size: 12px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
