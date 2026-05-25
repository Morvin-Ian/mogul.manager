import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { WorkspaceMember, Invitation, MemberRole } from '../types'
import { useAuthStore } from './auth'

export const useMembersStore = defineStore('members', () => {
  const members = ref<WorkspaceMember[]>([])
  const invitations = ref<Invitation[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  function authHeaders() {
    const auth = useAuthStore()
    return { Authorization: `Bearer ${auth.token}` }
  }

  async function fetchMembers(workspaceId: number) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`/api/workspaces/${workspaceId}/members`, {
        headers: authHeaders(),
      })
      if (!res.ok) throw new Error(await res.text())
      members.value = await res.json()
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchInvitations(workspaceId: number) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`/api/workspaces/${workspaceId}/members/invitations`, {
        headers: authHeaders(),
      })
      if (!res.ok) throw new Error(await res.text())
      invitations.value = await res.json()
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function invite(workspaceId: number, email: string, role: MemberRole) {
    error.value = null
    const res = await fetch(`/api/workspaces/${workspaceId}/members/invite`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, role }),
    })
    if (!res.ok) {
      const msg = await res.text()
      error.value = msg
      throw new Error(msg)
    }
    const inv: Invitation = await res.json()
    invitations.value.push(inv)
    return inv
  }

  async function removeMember(workspaceId: number, userId: number) {
    error.value = null
    const res = await fetch(`/api/workspaces/${workspaceId}/members/${userId}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    if (!res.ok) {
      const msg = await res.text()
      error.value = msg
      throw new Error(msg)
    }
    members.value = members.value.filter((m) => m.user_id !== userId)
  }

  async function updateRole(workspaceId: number, userId: number, role: MemberRole) {
    error.value = null
    const res = await fetch(`/api/workspaces/${workspaceId}/members/${userId}/role`, {
      method: 'PATCH',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ role }),
    })
    if (!res.ok) {
      const msg = await res.text()
      error.value = msg
      throw new Error(msg)
    }
    const updated: WorkspaceMember = await res.json()
    const idx = members.value.findIndex((m) => m.user_id === userId)
    if (idx !== -1) members.value[idx] = updated
  }

  async function revokeInvitation(workspaceId: number, invitationId: number) {
    error.value = null
    const res = await fetch(`/api/workspaces/${workspaceId}/members/invitations/${invitationId}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    if (!res.ok) {
      const msg = await res.text()
      error.value = msg
      throw new Error(msg)
    }
    invitations.value = invitations.value.filter((i) => i.id !== invitationId)
  }

  async function acceptInvite(token: string) {
    error.value = null
    const res = await fetch(`/api/invitations/${token}/accept`, {
      method: 'POST',
      headers: authHeaders(),
    })
    if (!res.ok) {
      const msg = await res.text()
      error.value = msg
      throw new Error(msg)
    }
    return await res.json()
  }

  async function getInviteInfo(token: string) {
    error.value = null
    const res = await fetch(`/api/invitations/${token}`)
    if (!res.ok) {
      const msg = await res.text()
      error.value = msg
      throw new Error(msg)
    }
    return (await res.json()) as Invitation
  }

  return {
    members,
    invitations,
    loading,
    error,
    fetchMembers,
    fetchInvitations,
    invite,
    removeMember,
    updateRole,
    revokeInvitation,
    acceptInvite,
    getInviteInfo,
  }
})
