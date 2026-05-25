const BASE_URL = '/api'

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  if (options.body instanceof FormData || options.body instanceof URLSearchParams) {
    delete headers['Content-Type']
  }
  const res = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers })
  if (res.status === 204) return null as T
  const data = await res.json()
  if (!res.ok) {
    throw new Error(data.detail || 'Request failed')
  }
  return data as T
}

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
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body,
  }).then(async (res) => {
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Request failed')
    return data as T
  })
}

export function postFile<T>(endpoint: string, formData: FormData): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
  }).then(async (res) => {
    if (res.status === 201 || res.status === 200) {
      const data = await res.json()
      return data as T
    }
    const data = await res.json()
    throw new Error(data.detail || 'Upload failed')
  })
}

export function patchFile<T>(endpoint: string, formData: FormData): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return fetch(`${BASE_URL}${endpoint}`, {
    method: 'PATCH',
    headers,
    body: formData,
  }).then(async (res) => {
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Request failed')
    return data as T
  })
}
