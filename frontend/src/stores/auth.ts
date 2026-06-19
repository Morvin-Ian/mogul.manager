import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, TokenResponse } from '../types'
import { get, post, patch, del, postForm, patchFile } from './client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function login(email: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)
      const res = await postForm<TokenResponse>('/users/token', formData)
      token.value = res.access_token
      localStorage.setItem('token', res.access_token)
      await fetchUser()
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function register(data: { username: string; email: string; password: string }) {
    loading.value = true
    error.value = null
    try {
      await post<User>('/users', data)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    user.value = await get<User>('/users/me')
  }

  async function forgotPassword(email: string) {
    await post<{ message: string }>('/users/forgot-password', { email })
  }

  async function resetPassword(resetToken: string, newPassword: string) {
    await post<{ message: string }>('/users/reset-password', {
      token: resetToken,
      new_password: newPassword,
    })
  }

  async function changePassword(currentPassword: string, newPassword: string) {
    await patch<{ message: string }>('/users/me/password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  async function updateProfile(data: { username?: string; email?: string }) {
    if (!user.value) return
    const updated = await patch<User>(`/users/${user.value.id}`, data)
    user.value = updated
  }

  async function uploadProfilePicture(file: File) {
    if (!user.value) return
    const formData = new FormData()
    formData.append('file', file)
    const updated = await patchFile<User>(`/users/${user.value.id}/picture`, formData)
    user.value = updated
  }

  async function deleteProfilePicture() {
    if (!user.value) return
    const updated = await del<User>(`/users/${user.value.id}/picture`)
    user.value = updated
  }

  async function unlinkGoogle() {
    const updated = await post<{ message: string }>('/auth/google/unlink', {})
    await fetchUser()
    return updated
  }

  async function deleteAccount() {
    if (!user.value) return
    await del<void>(`/users/${user.value.id}`)
    logout()
  }

  async function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    try {
      await fetch('/api/users/logout', { method: 'POST', credentials: 'include' })
    } catch { /* best-effort */ }
  }

  return {
    user,
    token,
    loading,
    error,
    login,
    register,
    fetchUser,
    forgotPassword,
    resetPassword,
    changePassword,
    updateProfile,
    uploadProfilePicture,
    deleteProfilePicture,
    unlinkGoogle,
    deleteAccount,
    logout,
  }
})
