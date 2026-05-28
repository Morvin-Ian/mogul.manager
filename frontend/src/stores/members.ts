import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { WorkspaceMember, Invitation, InvitationInfo, MyMembershipResponse, AcceptInviteResponse, MemberRole } from '../types'
import { get, post, patch, del } from './client'

export const useMembersStore = defineStore('members', () => {
  const members = ref<WorkspaceMember[]>([])
  const invitations = ref<Invitation[]>([])
  const myMembership = ref<MyMembershipResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMembers(workspaceId: number) {
    loading.value = true
    error.value = null
    try {
      members.value = await get<WorkspaceMember[]>(`/workspaces/${workspaceId}/members`)
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
      const items = await get<Invitation[]>(`/workspaces/${workspaceId}/members/invitations`)
      invitations.value = items
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function invite(workspaceId: number, email: string, role: MemberRole) {
    error.value = null
    try {
      const inv = await post<Invitation>(`/workspaces/${workspaceId}/members/invite`, { email, role })
      invitations.value.push(inv)
      return inv
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function removeMember(workspaceId: number, userId: number) {
    error.value = null
    try {
      await del(`/workspaces/${workspaceId}/members/${userId}`)
      members.value = members.value.filter((m) => m.user_id !== userId)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function updateRole(workspaceId: number, userId: number, role: MemberRole) {
    error.value = null
    try {
      const updated = await patch<WorkspaceMember>(`/workspaces/${workspaceId}/members/${userId}/role`, { role })
      const idx = members.value.findIndex((m) => m.user_id === userId)
      if (idx !== -1) members.value[idx] = updated
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function revokeInvitation(workspaceId: number, invitationId: number) {
    error.value = null
    try {
      await del(`/workspaces/${workspaceId}/members/invitations/${invitationId}`)
      invitations.value = invitations.value.filter((i) => i.id !== invitationId)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function fetchMyMembership(workspaceId: number) {
    try {
      myMembership.value = await get<MyMembershipResponse>(`/workspaces/${workspaceId}/members/me`)
      return myMembership.value
    } catch {
      myMembership.value = null
      return null
    }
  }

  async function acceptInvite(token: string) {
    error.value = null
    try {
      const res = await post<AcceptInviteResponse>(`/invitations/${token}/accept`)
      return res
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function getInviteInfo(token: string) {
    try {
      return await get<InvitationInfo>(`/invitations/${token}`)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  return {
    members,
    invitations,
    myMembership,
    loading,
    error,
    fetchMembers,
    fetchInvitations,
    fetchMyMembership,
    invite,
    removeMember,
    updateRole,
    revokeInvitation,
    acceptInvite,
    getInviteInfo,
  }
})
