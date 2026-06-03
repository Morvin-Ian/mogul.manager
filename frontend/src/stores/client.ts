const BASE_URL = '/api'

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>
}

// ── Silent refresh state ────────────────────────────────────────────
let isRefreshing = false
let pendingCallbacks: Array<(token: string | null) => void> = []

function flushPending(token: string | null) {
  pendingCallbacks.forEach(cb => cb(token))
  pendingCallbacks = []
}

async function tryRefresh(): Promise<string | null> {
  try {
    const res = await fetch(`${BASE_URL}/users/refresh`, {
      method: 'POST',
      credentials: 'include',
    })
    if (!res.ok) return null
    const data = await res.json()
    const newToken: string = data.access_token
    localStorage.setItem('token', newToken)
    return newToken
  } catch {
    return null
  }
}

function forceLogout() {
  localStorage.removeItem('token')
  window.location.href = '/login'
}

// ── Core request ────────────────────────────────────────────────────
async function request<T>(endpoint: string, options: RequestOptions = {}, _retry = false): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (options.body instanceof FormData || options.body instanceof URLSearchParams) {
    delete headers['Content-Type']
  }

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include',
  })

  // ── Handle 401 with silent refresh ──
  const isAuthEndpoint = endpoint.includes('/users/token') || endpoint.includes('/users/refresh')
  if (res.status === 401 && !isAuthEndpoint && !_retry) {
    if (isRefreshing) {
      // Queue until ongoing refresh completes
      return new Promise<T>((resolve, reject) => {
        pendingCallbacks.push(async (newToken) => {
          if (!newToken) { reject(new Error('Session expired')); return }
          try {
            resolve(await request<T>(endpoint, options, true))
          } catch (e) {
            reject(e)
          }
        })
      })
    }

    isRefreshing = true
    const newToken = await tryRefresh()
    isRefreshing = false

    if (!newToken) {
      flushPending(null)
      forceLogout()
      throw new Error('Session expired. Please log in again.')
    }

    flushPending(newToken)
    return request<T>(endpoint, options, true)
  }

  if (res.status === 204) return null as T
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Request failed')
  return data as T
}

// ── Public helpers ──────────────────────────────────────────────────
export function get<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint, { method: 'GET' })
}

export function post<T>(endpoint: string, body?: unknown): Promise<T> {
  return request<T>(endpoint, { method: 'POST', body: JSON.stringify(body) })
}

export function patch<T>(endpoint: string, body?: unknown): Promise<T> {
  return request<T>(endpoint, { method: 'PATCH', body: JSON.stringify(body) })
}

export function del<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint, { method: 'DELETE' })
}

export function postForm<T>(endpoint: string, body: URLSearchParams): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  return fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body,
    credentials: 'include',
  }).then(async (res) => {
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Request failed')
    return data as T
  })
}

export async function fetchBlob(endpoint: string): Promise<Blob> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${BASE_URL}${endpoint}`, { headers, credentials: 'include' })
  if (!res.ok) throw new Error(`Failed to fetch file: ${res.status}`)
  return res.blob()
}

export function postFile<T>(endpoint: string, formData: FormData): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  return fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
    credentials: 'include',
  }).then(async (res) => {
    if (res.status === 201 || res.status === 200) return res.json() as Promise<T>
    const data = await res.json()
    throw new Error(data.detail || 'Upload failed')
  })
}

export function patchFile<T>(endpoint: string, formData: FormData): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  return fetch(`${BASE_URL}${endpoint}`, {
    method: 'PATCH',
    headers,
    body: formData,
    credentials: 'include',
  }).then(async (res) => {
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Request failed')
    return data as T
  })
}
