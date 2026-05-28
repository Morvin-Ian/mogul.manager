<template>
  <div class="chat-input-bar">
    <div class="chat-input-wrap" :class="{ focused: focused, disabled: streaming }">
      <textarea
        ref="textareaRef"
        v-model="text"
        :placeholder="placeholder"
        rows="1"
        @keydown.enter.exact.prevent="$emit('send', text)"
        @focus="focused = true"
        @blur="focused = false"
        @input="autoResize"
        :disabled="streaming"
      ></textarea>
      <button
        class="send-btn"
        @click="$emit('send', text)"
        :disabled="streaming || !text.trim()"
      >
        <svg v-if="!streaming" viewBox="0 0 16 16" fill="none" width="16" height="16">
          <path d="M2 8l12-6-6 12V9L2 8z" fill="currentColor"/>
        </svg>
        <span v-else class="streaming-dot"></span>
      </button>
    </div>
    <p class="input-hint">Press Enter to send · Shift+Enter for new line</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string
  streaming: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  send: [text: string]
}>()

const text = ref(props.modelValue)
const focused = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

watch(() => props.modelValue, (v) => { text.value = v })
watch(text, (v) => emit('update:modelValue', v))

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}
</script>

<style scoped>
.chat-input-bar {
  padding: 16px 32px 24px;
  background: var(--bg);
  max-width: 820px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-input-wrap {
  display: flex;
  align-items: flex-end;
  gap: 0;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.chat-input-wrap.disabled {
  background: var(--bg);
}

.chat-input-wrap.focused {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.chat-input-wrap textarea {
  flex: 1;
  padding: 13px 16px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  color: var(--text);
  line-height: 1.5;
  max-height: 140px;
  overflow-y: auto;
}

.chat-input-wrap textarea:focus { outline: none; }
.chat-input-wrap textarea::placeholder { color: var(--text-light); }
.chat-input-wrap textarea:disabled { opacity: 0.6; }

.send-btn {
  width: 40px;
  height: 40px;
  margin: 10px 10px 10px 4px;
  border: none;
  border-radius: 10px;
  background: #1c1c1e;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s;
  align-self: flex-end;
  box-shadow: 0 2px 8px rgba(10, 11, 13, 0.25);
}

.send-btn:hover:not(:disabled) { background: #2e2e30; }
.send-btn:active:not(:disabled) { transform: scale(0.96); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.streaming-dot {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(0.75); }
}

.input-hint {
  font-size: 11.5px;
  color: var(--text-light);
  text-align: center;
}
</style>
