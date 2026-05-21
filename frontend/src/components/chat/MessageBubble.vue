<template>
  <div class="message" :class="[role === 'user' ? 'message-user' : 'message-assistant', { 'message-streaming': streaming }]">
    <div class="message-avatar">
      {{ role === 'user' ? initials : 'AI' }}
    </div>
    <div class="message-content">
      <div class="message-text">
        <span v-if="streaming && !content">▊</span>
        <template v-else-if="role === 'assistant'">
          <div class="md-body" v-html="renderedContent"></div>
          <span v-if="streaming" class="cursor-blink">|</span>
        </template>
        <template v-else>
          <span>{{ content }}</span>
        </template>
      </div>
      <div v-if="!streaming && content" class="message-time">{{ time }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useAuthStore } from '../../stores/auth'

const props = defineProps<{
  role: string
  content: string
  streaming?: boolean
  createdAt?: string
}>()

const auth = useAuthStore()

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
</script>

<style scoped>
.message {
  display: flex;
  gap: 10px;
  max-width: 78%;
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
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 2px;
}

.message-user .message-avatar {
  background: var(--primary-light);
  color: var(--primary);
  border: 1.5px solid var(--primary-border);
}

.message-assistant .message-avatar {
  background: #f4f4f5;
  color: #52525b;
  border: 1.5px solid var(--border);
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.message-text {
  padding: 10px 14px;
  border-radius: var(--radius);
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.message-user .message-text {
  background: var(--primary);
  color: #fff;
  border-bottom-right-radius: var(--radius-xs);
  white-space: pre-wrap;
}

.message-assistant .message-text {
  background: #f4f4f5;
  color: var(--text);
  border-bottom-left-radius: var(--radius-xs);
  border: 1px solid var(--border);
}

.message-time {
  font-size: 11px;
  color: var(--text-light);
  padding: 0 2px;
}

.message-user .message-time {
  text-align: right;
}

.message-streaming .message-text {
  background: #f4f4f5;
  border: 1px solid var(--border);
  color: var(--text);
  border-bottom-left-radius: var(--radius-xs);
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
</style>
