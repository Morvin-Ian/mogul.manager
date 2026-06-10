import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Conversation, ConversationDetail, Message } from '../types'
import { get, post, patch, del } from './client'

const THINKING_PHRASES = [
  'Thinking…',
  'Analyzing…',
  'Galvanizing…',
  'Figuring out…',
  'Processing…',
  'Connecting the dots…',
  'Strategizing…',
  'Calculating…',
  'Assembling context…',
  'Mapping it out…',
  'Synthesizing…',
  'Consulting the plan…',
  'Weighing the options…',
  'Reasoning through this…',
  'Crunching the numbers…',
  'Cross-referencing…',
  'On it…',
]

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<Conversation[]>([])
  const current = ref<ConversationDetail | null>(null)
  const pendingMessage = ref<string | null>(null)  // set by FAB to auto-send on chat open
  const streaming = ref(false)
  const streamContent = ref('')
  const toolActivity = ref<string | null>(null)
  const thinkingStatus = ref('')
  const loading = ref(false)
  const error = ref<string | null>(null)

  let _thinkingTimer: ReturnType<typeof setInterval> | null = null

  function _startThinking() {
    let lastIdx = -1
    const pick = () => {
      let idx
      do { idx = Math.floor(Math.random() * THINKING_PHRASES.length) } while (idx === lastIdx)
      lastIdx = idx
      return THINKING_PHRASES[idx]
    }
    thinkingStatus.value = pick()
    _thinkingTimer = setInterval(() => { thinkingStatus.value = pick() }, 1800)
  }

  function _stopThinking() {
    if (_thinkingTimer !== null) {
      clearInterval(_thinkingTimer)
      _thinkingTimer = null
    }
    thinkingStatus.value = ''
  }

  async function fetchConversations() {
    loading.value = true
    try {
      conversations.value = await get<Conversation[]>('/chat/conversations')
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchConversation(id: number) {
    loading.value = true
    try {
      current.value = await get<ConversationDetail>(`/chat/conversations/${id}`)
      return current.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createConversation(title?: string) {
    const conv = await post<Conversation>('/chat/conversations', { title: title || null })
    conversations.value.unshift(conv)
    return conv
  }

  async function updateConversation(id: number, data: { title?: string; is_archived?: boolean }) {
    const conv = await patch<Conversation>(`/chat/conversations/${id}`, data)
    const idx = conversations.value.findIndex((c) => c.id === id)
    if (idx !== -1) conversations.value[idx] = conv
    if (current.value?.id === id) current.value = { ...current.value, ...conv }
    return conv
  }

  async function removeConversation(id: number) {
    await del(`/chat/conversations/${id}`)
    conversations.value = conversations.value.filter((c) => c.id !== id)
    if (current.value?.id === id) current.value = null
  }

  async function sendMessage(conversationId: number, content: string): Promise<void> {
    streaming.value = true
    streamContent.value = ''
    toolActivity.value = null
    error.value = null
    _startThinking()

    const token = localStorage.getItem('token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    if (token) headers['Authorization'] = `Bearer ${token}`

    if (current.value) {
      current.value.messages.push({ role: 'user', content, id: 0, uuid: '', conversation_id: conversationId, created_at: new Date().toISOString() })
    }

    try {
      const res = await fetch(`/api/chat/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ content }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to send message')
      }

      const reader = res.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (!raw) continue
          try {
            const parsed = JSON.parse(raw)
            if (parsed.tool) {
              toolActivity.value = parsed.tool
            }
            if (parsed.token) {
              _stopThinking()
              toolActivity.value = null
              streamContent.value += parsed.token
            }
            if (parsed.done) {
              if (current.value && parsed.message) {
                current.value.messages.push(parsed.message)
              }
              toolActivity.value = null
              streamContent.value = ''
            }
          } catch {
            // skip malformed JSON chunks
          }
        }
      }
    } catch (e) {
      error.value = (e as Error).message
      if (current.value) {
        current.value.messages.pop()
      }
    } finally {
      streaming.value = false
      toolActivity.value = null
      _stopThinking()
    }
  }

  return {
    conversations, current, pendingMessage, streaming, streamContent, toolActivity, thinkingStatus, loading, error,
    fetchConversations, fetchConversation, createConversation,
    updateConversation, removeConversation, sendMessage,
  }
})
