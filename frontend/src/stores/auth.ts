import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, TokenResponse } from '../types'
import { get, post, postForm } from './client'

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
    try {
      user.value = await get<User>('/users/me')
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return { user, token, loading, error, login, register, fetchUser, logout }
})
