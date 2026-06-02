<template>
  <div class="chat-input-wrap">

    <!-- Upload / voice feedback bar -->
    <Transition name="feedback-slide">
      <div v-if="uploadState.status !== 'idle'" class="feedback-bar" :class="`fb-${uploadState.status}`">
        <span v-if="uploadState.status === 'uploading'" class="fb-spinner"></span>
        <svg v-else-if="uploadState.status === 'success'" viewBox="0 0 14 14" fill="none" width="13" height="13">
          <circle cx="7" cy="7" r="6" fill="#00BA7C"/>
          <path d="M4.5 7l2 2 3-3" stroke="#fff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else viewBox="0 0 14 14" fill="none" width="13" height="13">
          <circle cx="7" cy="7" r="6" fill="#EF4444"/>
          <path d="M5 5l4 4M9 5l-4 4" stroke="#fff" stroke-width="1.4" stroke-linecap="round"/>
        </svg>
        <span class="fb-text">{{ uploadState.message }}</span>
        <button class="fb-close" @click="resetUpload">×</button>
      </div>
    </Transition>

    <div class="input-box" :class="{ focused, disabled: streaming, recording }">

      <!-- Hidden file input -->
      <input
        ref="fileInputRef"
        type="file"
        accept=".pdf,.docx,.txt,.csv,.md"
        style="display:none"
        @change="handleFileChange"
      />

      <!-- Voice recording overlay inside textarea area -->
      <div v-if="recording" class="recording-overlay">
        <div class="recording-pulse">
          <span class="rec-dot"></span>
          <span class="rec-dot"></span>
          <span class="rec-dot"></span>
        </div>
        <span class="recording-label">Listening… speak now</span>
        <button class="rec-stop" @click="stopVoice">Stop</button>
      </div>

      <textarea
        v-else
        ref="textareaRef"
        v-model="text"
        :placeholder="placeholder"
        rows="1"
        :disabled="streaming"
        @keydown.enter.exact.prevent="$emit('send', text)"
        @focus="focused = true"
        @blur="focused = false"
        @input="autoResize"
      ></textarea>

      <!-- Action bar -->
      <div class="input-actions">
        <div class="actions-left">
          <!-- Attach -->
          <button
            class="action-btn"
            :class="{ 'action-loading': uploadState.status === 'uploading' }"
            :disabled="streaming || uploadState.status === 'uploading'"
            @click="openFilePicker"
            title="Attach a file (PDF, DOCX, TXT, CSV)"
          >
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
              <path d="M13.5 7.5l-6.5 6.5a4 4 0 01-5.66-5.66l7-7a2.5 2.5 0 013.54 3.54l-7 7a1 1 0 01-1.42-1.42l6.5-6.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ uploadState.status === 'uploading' ? 'Uploading…' : 'Attach' }}</span>
          </button>

          <!-- Voice -->
          <button
            class="action-btn"
            :class="{ 'action-active': recording, 'action-unsupported': !speechSupported }"
            :disabled="streaming"
            @click="toggleVoice"
            :title="!speechSupported ? 'Voice input not supported in this browser' : recording ? 'Stop recording' : 'Voice message'"
          >
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
              <path d="M8 1a3 3 0 00-3 3v4a3 3 0 006 0V4a3 3 0 00-3-3zM3 7v1a5 5 0 0010 0V7M8 13v2.5M5.5 15.5h5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ recording ? 'Listening…' : 'Voice' }}</span>
            <span v-if="recording" class="voice-live-dot"></span>
          </button>

          <!-- Browse Prompts -->
          <button class="action-btn" :disabled="streaming" @click="showPrompts = !showPrompts" title="Browse prompts">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
              <rect x="1" y="1" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
              <rect x="9" y="1" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
              <rect x="1" y="9" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
              <rect x="9" y="9" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <span>Browse Prompts</span>
          </button>
        </div>

        <div class="actions-right">
          <span class="char-count" :class="{ 'char-warn': text.length > 2700 }">
            {{ text.length }} / 3,000
          </span>
          <button
            class="send-btn"
            @click="$emit('send', text)"
            :disabled="streaming || !text.trim()"
          >
            <span v-if="streaming" class="streaming-dot"></span>
            <svg v-else viewBox="0 0 16 16" fill="none" width="15" height="15">
              <path d="M13.5 8H2.5M9.5 3.5L14 8l-4.5 4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Quick prompts dropdown -->
    <Transition name="prompts-drop">
      <div v-if="showPrompts" class="prompts-dropdown">
        <p class="prompts-heading">Suggested prompts</p>
        <button
          v-for="p in suggestedPrompts"
          :key="p"
          class="prompt-item"
          @click="usePrompt(p)"
        >{{ p }}</button>
      </div>
    </Transition>

    <p class="disclaimer">
      Mogul Manager may generate inaccurate information. Verify important details independently.
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'

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
const fileInputRef = ref<HTMLInputElement | null>(null)

watch(() => props.modelValue, (v) => { text.value = v })
watch(text, (v) => emit('update:modelValue', v))

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 180) + 'px'
}

// ── File Attach ──────────────────────────────────────────────────
const uploadState = ref<{ status: 'idle' | 'uploading' | 'success' | 'error'; message: string }>({
  status: 'idle', message: '',
})

function openFilePicker() {
  fileInputRef.value?.click()
}

function resetUpload() {
  uploadState.value = { status: 'idle', message: '' }
}

async function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (fileInputRef.value) fileInputRef.value.value = ''

  uploadState.value = { status: 'uploading', message: `Uploading ${file.name}…` }

  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', file.name.replace(/\.[^.]+$/, ''))

    const token = localStorage.getItem('token')
    const headers: Record<string, string> = {}
    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch('/api/documents', {
      method: 'POST',
      headers,
      body: formData,
      credentials: 'include',
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || 'Upload failed')
    }

    uploadState.value = { status: 'success', message: `"${file.name}" uploaded — AI can now reference it in this chat.` }

    // Pre-fill input so the user can ask about the file
    const msg = `I've just uploaded "${file.name}". Can you summarise what it's about?`
    text.value = msg
    emit('update:modelValue', msg)

    setTimeout(resetUpload, 5000)
  } catch (err) {
    uploadState.value = { status: 'error', message: (err as Error).message }
    setTimeout(resetUpload, 6000)
  }
}

// ── Voice Input ──────────────────────────────────────────────────
const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
const speechSupported = !!SpeechRecognition

const recording = ref(false)
let recognitionInstance: any = null

function toggleVoice() {
  if (!speechSupported) return
  if (recording.value) {
    stopVoice()
  } else {
    startVoice()
  }
}

function startVoice() {
  const sr = new SpeechRecognition()
  sr.continuous = false
  sr.interimResults = true
  sr.lang = 'en-US'

  sr.onstart = () => { recording.value = true }

  sr.onresult = (e: any) => {
    const transcript = Array.from(e.results as SpeechRecognitionResultList)
      .map((r: SpeechRecognitionResult) => r[0].transcript)
      .join('')
    text.value = transcript
    emit('update:modelValue', transcript)
  }

  sr.onend = () => {
    recording.value = false
    recognitionInstance = null
  }

  sr.onerror = (e: any) => {
    recording.value = false
    recognitionInstance = null
    if (e.error === 'not-allowed') {
      uploadState.value = { status: 'error', message: 'Microphone permission denied. Please allow access in your browser.' }
      setTimeout(resetUpload, 5000)
    }
  }

  recognitionInstance = sr
  sr.start()
}

function stopVoice() {
  recognitionInstance?.stop()
  recording.value = false
}

onBeforeUnmount(() => {
  recognitionInstance?.abort()
})

// ── Browse Prompts ───────────────────────────────────────────────
const showPrompts = ref(false)

const suggestedPrompts = [
  'What tasks are overdue across all my projects?',
  'Who has the most tasks assigned right now?',
  'Summarize progress across all active workspaces',
  'Which project is furthest behind schedule?',
  'Create 5 tasks for a new product launch',
  'Move all blocked tasks back to In Progress',
  'What should I focus on today?',
  'Draft a project status update for stakeholders',
]

function usePrompt(p: string) {
  text.value = p
  emit('update:modelValue', p)
  showPrompts.value = false
}
</script>

<style scoped>
.chat-input-wrap {
  padding: 0 28px 20px;
  max-width: 780px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

/* ── Feedback bar ── */
.feedback-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}
.fb-uploading { background: var(--surface); border: 1px solid var(--border); color: var(--text-muted); }
.fb-success   { background: #D1FAE5; border: 1px solid #6EE7B7; color: #065F46; }
.fb-error     { background: #FEE2E2; border: 1px solid #FCA5A5; color: #991B1B; }
.fb-text { flex: 1; }
.fb-close {
  background: none; border: none; cursor: pointer;
  font-size: 16px; line-height: 1; color: inherit; opacity: 0.6;
  padding: 0 2px;
}
.fb-close:hover { opacity: 1; }
.fb-spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(0,0,0,0.15);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.65s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.feedback-slide-enter-active, .feedback-slide-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.feedback-slide-enter-from, .feedback-slide-leave-to {
  opacity: 0; transform: translateY(-6px);
}

/* ── Input box ── */
.input-box {
  border: 1.5px solid var(--border);
  border-radius: 14px;
  background: var(--surface);
  transition: border-color 0.15s, box-shadow 0.15s;
  overflow: hidden;
  position: relative;
}
.input-box.focused { border-color: var(--border-strong); box-shadow: 0 0 0 3px rgba(0,0,0,0.05); }
.input-box.disabled { opacity: 0.7; }
.input-box.recording { border-color: #EF4444; box-shadow: 0 0 0 3px rgba(239,68,68,0.1); }

textarea {
  width: 100%;
  padding: 16px 18px 10px;
  border: none; outline: none;
  background: transparent;
  font-size: 14.5px; font-family: inherit;
  color: var(--text); resize: none;
  line-height: 1.55; max-height: 180px; overflow-y: auto; display: block;
}
textarea::placeholder { color: var(--text-light); }
textarea:disabled { opacity: 0.6; }

/* ── Recording overlay ── */
.recording-overlay {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 18px;
  min-height: 58px;
}
.recording-pulse { display: flex; align-items: center; gap: 3px; }
.rec-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: #EF4444;
  animation: rec-bounce 0.8s ease-in-out infinite;
}
.rec-dot:nth-child(2) { animation-delay: 0.15s; height: 9px; }
.rec-dot:nth-child(3) { animation-delay: 0.3s; }
@keyframes rec-bounce {
  0%, 100% { transform: scaleY(1); }
  50%       { transform: scaleY(1.8); }
}
.recording-label { flex: 1; font-size: 14px; color: #EF4444; font-weight: 500; }
.rec-stop {
  background: #EF4444; color: #fff; border: none;
  padding: 5px 12px; border-radius: 8px;
  font-size: 12.5px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: background 0.12s;
}
.rec-stop:hover { background: #DC2626; }

/* ── Action bar ── */
.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px 10px;
  border-top: 1px solid var(--border);
  gap: 8px;
}
.actions-left  { display: flex; align-items: center; gap: 2px; }
.actions-right { display: flex; align-items: center; gap: 10px; }

.action-btn {
  display: inline-flex; align-items: center; gap: 5px;
  background: none; border: none; cursor: pointer;
  color: var(--text-muted);
  font-size: 12.5px; font-family: inherit; font-weight: 500;
  padding: 5px 8px; border-radius: 8px;
  transition: background 0.12s, color 0.12s;
  white-space: nowrap;
}
.action-btn:hover { background: var(--bg); color: var(--text); }
.action-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.action-btn.action-active { color: #EF4444; background: rgba(239,68,68,0.08); }
.action-btn.action-loading { opacity: 0.6; }
.action-btn.action-unsupported { opacity: 0.35; cursor: not-allowed; }

.voice-live-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #EF4444;
  animation: pulse-dot 1s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.3; }
}

.char-count {
  font-size: 12px; color: var(--text-light); font-weight: 500; white-space: nowrap;
}
.char-warn { color: var(--danger); font-weight: 700; }

.send-btn {
  width: 34px; height: 34px; border-radius: 10px;
  background: #1c1c1e; color: #fff; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: background 0.15s, transform 0.1s;
}
.send-btn:hover:not(:disabled) { background: #2e2e30; }
.send-btn:active:not(:disabled) { transform: scale(0.94); }
.send-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.streaming-dot {
  width: 8px; height: 8px; background: #fff; border-radius: 50%;
  animation: pulse-dot 1s ease-in-out infinite;
}

/* ── Prompts dropdown ── */
.prompts-dropdown {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(10,11,13,0.12);
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.prompts-heading {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-light);
  padding: 4px 10px 6px;
}
.prompt-item {
  display: block; width: 100%; text-align: left;
  background: none; border: none; cursor: pointer;
  font-size: 13.5px; font-family: inherit; color: var(--text);
  padding: 9px 10px; border-radius: 9px;
  transition: background 0.1s;
  line-height: 1.4;
}
.prompt-item:hover { background: var(--bg); }

.prompts-drop-enter-active, .prompts-drop-leave-active {
  transition: opacity 0.18s, transform 0.18s;
}
.prompts-drop-enter-from, .prompts-drop-leave-to {
  opacity: 0; transform: translateY(6px);
}

/* ── Disclaimer ── */
.disclaimer {
  font-size: 11.5px; color: var(--text-light); text-align: center; line-height: 1.5;
}

/* Dark mode */
:global([data-theme="dark"]) .send-btn { background: #F7F9F9; color: #15202B; }
:global([data-theme="dark"]) .send-btn:hover:not(:disabled) { background: #e2e5e5; }
:global([data-theme="dark"]) .fb-success { background: rgba(0,186,124,0.15); border-color: rgba(0,186,124,0.3); color: #00BA7C; }
:global([data-theme="dark"]) .fb-error   { background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.3); color: #FCA5A5; }
</style>
