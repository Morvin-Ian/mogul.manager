<template>
  <div class="message" :class="[role === 'user' ? 'message-user' : 'message-assistant', { 'message-streaming': streaming, 'message-grouped': grouped }]">
    <div class="message-avatar" :class="{ 'avatar-hidden': grouped }">
      {{ role === 'user' ? initials : 'AI' }}
    </div>
    <div class="message-content">
      <div class="message-text">
        <span v-if="streaming && !content">▊</span>
        <template v-else-if="role === 'assistant'">
          <div class="md-body" ref="mdBodyRef" v-html="renderedContent"></div>
          <span v-if="streaming" class="cursor-blink">|</span>
        </template>
        <template v-else>
          <span>{{ content }}</span>
        </template>
      </div>
      <div class="message-meta" v-if="!streaming && content">
        <span class="message-time">{{ time }}</span>
        <button class="copy-btn" @click="copyContent" :title="copied ? 'Copied!' : 'Copy message'">
          <svg v-if="!copied" viewBox="0 0 14 14" fill="none" width="12" height="12">
            <rect x="4.5" y="4.5" width="8" height="8" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M9.5 4.5V3a1 1 0 00-1-1H3a1 1 0 00-1 1v5.5a1 1 0 001 1h1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          <svg v-else viewBox="0 0 14 14" fill="none" width="12" height="12">
            <path d="M2.5 7l3 3L11.5 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="copy-label">{{ copied ? 'Copied' : 'Copy' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useAuthStore } from '../../stores/auth'

const props = defineProps<{
  role: string
  content: string
  streaming?: boolean
  createdAt?: string
  grouped?: boolean
}>()

const auth = useAuthStore()
const copied = ref(false)
const mdBodyRef = ref<HTMLElement | null>(null)

function injectCodeCopyButtons() {
  if (!mdBodyRef.value) return
  mdBodyRef.value.querySelectorAll('pre').forEach(pre => {
    if (pre.querySelector('.code-copy-btn')) return
    const btn = document.createElement('button')
    btn.className = 'code-copy-btn'
    btn.title = 'Copy code'
    btn.innerHTML = `<svg viewBox="0 0 14 14" fill="none" width="12" height="12"><rect x="4.5" y="4.5" width="8" height="8" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M9.5 4.5V3a1 1 0 00-1-1H3a1 1 0 00-1 1v5.5a1 1 0 001 1h1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg> Copy`
    btn.addEventListener('click', () => {
      const code = pre.querySelector('code')?.textContent ?? ''
      navigator.clipboard.writeText(code).then(() => {
        btn.textContent = 'Copied!'
        setTimeout(() => {
          btn.innerHTML = `<svg viewBox="0 0 14 14" fill="none" width="12" height="12"><rect x="4.5" y="4.5" width="8" height="8" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M9.5 4.5V3a1 1 0 00-1-1H3a1 1 0 00-1 1v5.5a1 1 0 001 1h1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg> Copy`
        }, 2000)
      })
    })
    pre.style.position = 'relative'
    pre.appendChild(btn)
  })
}

watch(() => props.content, () => {
  nextTick(injectCodeCopyButtons)
})

const initials = computed(() =>
  (auth.user?.username ?? 'U').slice(0, 2).toUpperCase()
)

const time = computed(() => {
  if (!props.createdAt) return ''
  return new Date(props.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
})

const renderedContent = computed(() => {
  if (!props.content) return ''
  const raw = marked.parse(props.content, { async: false }) as string
  return DOMPurify.sanitize(raw)
})

async function copyContent() {
  try {
    await navigator.clipboard.writeText(props.content)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {}
}
</script>

<style scoped>
.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message-grouped {
  margin-top: -14px;
}

.avatar-hidden {
  visibility: hidden;
}

.message-user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10.5px;
  font-weight: 800;
  flex-shrink: 0;
  margin-top: 3px;
  letter-spacing: 0.3px;
}

.message-user .message-avatar {
  background: #1c1c1e;
  color: #fff;
  border: none;
}

.message-assistant .message-avatar {
  background: var(--bg);
  color: var(--text-muted);
  border: 1.5px solid var(--border);
  font-size: 10px;
  letter-spacing: 0.4px;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.message-text {
  padding: 11px 15px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
}

.message-user .message-text {
  background: #1c1c1e;
  color: #fff;
  border-bottom-right-radius: 4px;
  white-space: pre-wrap;
  box-shadow: 0 2px 8px rgba(10, 11, 13, 0.22);
}

.message-assistant .message-text {
  background: var(--surface);
  color: var(--text);
  border-bottom-left-radius: 4px;
  border: 1.5px solid var(--border);
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 2px;
}

.message-user .message-meta {
  flex-direction: row-reverse;
}

.message-time {
  font-size: 11px;
  color: var(--text-light);
  opacity: 0;
  transition: opacity 0.15s;
}
.message:hover .message-time { opacity: 1; }

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-light);
  font-size: 11px;
  font-family: inherit;
  padding: 2px 5px;
  border-radius: 5px;
  opacity: 0;
  transition: opacity 0.15s, background 0.15s, color 0.15s;
}

.message:hover .copy-btn { opacity: 1; }
.copy-btn:hover { background: var(--bg); color: var(--text-muted); }
.copy-btn.copied, .copy-btn:has(svg path[d*="M2.5 7"]) { color: var(--success); opacity: 1; }

.copy-label {
  font-size: 11px;
}

.message-streaming .message-text {
  background: var(--surface);
  border: 1.5px solid var(--border);
  color: var(--text);
  border-bottom-left-radius: 4px;
}

.cursor-blink {
  display: inline-block;
  margin-left: 1px;
  animation: blink 0.9s step-end infinite;
  color: var(--primary);
  font-weight: 700;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0; }
}

/* Markdown body styles (assistant messages only) */
.md-body { line-height: 1.7; }
.md-body :deep(p)               { margin-bottom: 10px; }
.md-body :deep(p:last-child)    { margin-bottom: 0; }
.md-body :deep(h1),
.md-body :deep(h2),
.md-body :deep(h3)              { font-weight: 700; margin: 14px 0 6px; line-height: 1.3; }
.md-body :deep(h1)              { font-size: 17px; }
.md-body :deep(h2)              { font-size: 15px; }
.md-body :deep(h3)              { font-size: 13.5px; }
.md-body :deep(ul),
.md-body :deep(ol)              { padding-left: 20px; margin-bottom: 10px; }
.md-body :deep(li)              { margin-bottom: 4px; }
.md-body :deep(code)            { background: rgba(0,0,0,0.06); padding: 1px 5px; border-radius: 4px; font-size: 12.5px; font-family: 'Fira Mono', 'Consolas', monospace; }
.md-body :deep(pre)             { background: #1e1e2e; border-radius: 8px; padding: 14px 16px; margin: 10px 0; overflow-x: auto; }
.md-body :deep(pre code)        { background: none; padding: 0; color: #cdd6f4; font-size: 13px; }
.md-body :deep(blockquote)      { border-left: 3px solid var(--primary); padding-left: 12px; color: var(--text-muted); margin: 10px 0; font-style: italic; }
.md-body :deep(hr)              { border: none; border-top: 1px solid var(--border); margin: 14px 0; }
.md-body :deep(a)               { color: var(--primary); text-decoration: underline; }
.md-body :deep(strong)          { font-weight: 700; }
.md-body :deep(table)           { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }
.md-body :deep(th),
.md-body :deep(td)              { border: 1px solid var(--border); padding: 7px 12px; text-align: left; }
.md-body :deep(th)              { background: var(--bg); font-weight: 600; }
.md-body :deep(.code-copy-btn) {
  position: absolute;
  top: 8px;
  right: 8px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  color: rgba(255,255,255,0.6);
  font-size: 11px;
  font-family: inherit;
  padding: 3px 8px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s, background 0.15s, color 0.15s;
}
.md-body :deep(pre:hover .code-copy-btn) { opacity: 1; }
.md-body :deep(.code-copy-btn:hover) { background: rgba(255,255,255,0.15); color: #fff; }
</style>
