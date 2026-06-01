<template>
  <div class="review-tab">
    <div v-if="links.length" class="rv-links-list">
      <div v-for="(link, i) in links" :key="i" class="rv-link-row">
        <span class="rv-link-icon" :class="`rvli-${link.type}`">
          <font-awesome-icon :icon="reviewLinkIcon(link.type)" />
        </span>
        <div class="rv-link-info">
          <a :href="link.url" target="_blank" rel="noopener noreferrer" class="rv-link-label" @click.stop>
            {{ link.label || link.url }}
          </a>
          <span class="rv-link-url">{{ link.url }}</span>
        </div>
        <button class="rv-link-del" @click="removeLink(i)" title="Remove link">
          <font-awesome-icon :icon="['fas', 'xmark']" />
        </button>
      </div>
    </div>
    <p v-else class="desc-empty">No review links added yet.</p>

    <div class="rv-add-form">
      <p class="rv-add-title">Add a link</p>
      <select v-model="newLink.type" class="rv-type-select">
        <option value="repo">Repo / PR</option>
        <option value="doc">Document</option>
        <option value="design">Design</option>
        <option value="link">Other link</option>
      </select>
      <input v-model="newLink.url" class="rv-input" placeholder="https://…" type="url" @keydown.enter="addLink" />
      <input v-model="newLink.label" class="rv-input" placeholder="Label (optional)" @keydown.enter="addLink" />
      <button class="rv-add-btn" :disabled="!newLink.url.trim() || saving" @click="addLink">
        <font-awesome-icon :icon="['fas', 'plus']" />
        {{ saving ? 'Saving…' : 'Add link' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { patch } from '../../stores/client'
import type { Task } from '../../types'

interface ReviewLink { url: string; label: string; type: string }

const props = defineProps<{ task: Task }>()
const emit = defineEmits<{ updated: [task: Task] }>()

const newLink = reactive<ReviewLink>({ url: '', label: '', type: 'link' })
const saving = ref(false)

const links = computed<ReviewLink[]>(() => {
  const meta = props.task.metadata_json as Record<string, any> | null
  return (meta?.review_links as ReviewLink[]) ?? []
})

function reviewLinkIcon(type: string): string[] {
  if (type === 'repo') return ['fas', 'code-branch']
  if (type === 'doc') return ['fas', 'file-lines']
  if (type === 'design') return ['fas', 'pen-ruler']
  return ['fas', 'link']
}

async function saveLinks(links: ReviewLink[]) {
  saving.value = true
  try {
    const meta = { ...(props.task.metadata_json as Record<string, any> ?? {}), review_links: links }
    const updated = await patch<Task>(`/tasks/${props.task.uuid}`, { metadata_json: meta })
    emit('updated', updated)
  } finally {
    saving.value = false
  }
}

async function addLink() {
  if (!newLink.url.trim()) return
  await saveLinks([...links.value, { url: newLink.url.trim(), label: newLink.label.trim(), type: newLink.type }])
  newLink.url = ''
  newLink.label = ''
  newLink.type = 'link'
}

async function removeLink(index: number) {
  await saveLinks(links.value.filter((_, i) => i !== index))
}
</script>

<style scoped>
.rv-links-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.rv-link-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  transition: border-color 0.12s;
}
.rv-link-row:hover { border-color: var(--border-strong); }

.rv-link-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
}
.rvli-repo   { background: #F0FDF4; color: #16A34A; }
.rvli-doc    { background: #EFF6FF; color: #2563EB; }
.rvli-design { background: #FDF4FF; color: #9333EA; }
.rvli-link   { background: #F8FAFC; color: #475569; }

.rv-link-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rv-link-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rv-link-label:hover { text-decoration: underline; }

.rv-link-url {
  font-size: 11px;
  color: var(--text-light);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rv-link-del {
  width: 26px;
  height: 26px;
  border: none;
  background: none;
  color: var(--text-light);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: background 0.12s, color 0.12s;
  flex-shrink: 0;
}
.rv-link-del:hover { background: #FEE2E2; color: #DC2626; }

.rv-add-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 12px;
}

.rv-add-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin: 0;
}

.rv-type-select {
  padding: 8px 10px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  outline: none;
}
.rv-type-select:focus { border-color: var(--primary); }

.rv-input {
  padding: 8px 12px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  background: var(--surface);
  color: var(--text);
  outline: none;
  transition: border-color 0.14s;
}
.rv-input:focus { border-color: var(--primary); }
.rv-input::placeholder { color: var(--text-light); }

.rv-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 16px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.14s;
  align-self: flex-start;
}
.rv-add-btn:hover { opacity: 0.82; }
.rv-add-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.desc-empty {
  font-size: 13px;
  color: var(--text-light);
  font-style: italic;
}

:global([data-theme="dark"]) .rvli-repo   { background: rgba(22,163,74,0.18); color: #4ADE80; }
:global([data-theme="dark"]) .rvli-doc    { background: rgba(37,99,235,0.18); color: #60A5FA; }
:global([data-theme="dark"]) .rvli-design { background: rgba(147,51,234,0.18); color: #C084FC; }
:global([data-theme="dark"]) .rvli-link   { background: rgba(255,255,255,0.07); color: #8B98A5; }
:global([data-theme="dark"]) .rv-link-del:hover { background: rgba(220,38,38,0.18); color: #F87171; }
:global([data-theme="dark"]) .rv-input { background: #253341; border-color: #38444D; }
:global([data-theme="dark"]) .rv-type-select { background: #253341; border-color: #38444D; }
:global([data-theme="dark"]) .rv-add-btn { background: #F7F9F9; color: #15202B; }
</style>
