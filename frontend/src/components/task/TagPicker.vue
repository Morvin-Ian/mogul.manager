<template>
  <div class="tag-picker" :class="{ 'picker-open': open }">
    <label class="picker-label">Tags</label>
    <div class="tag-list">
      <TagChip
        v-for="t in selected"
        :key="t.id"
        :tag="t"
        class="tag-chip-btn"
        @click.stop="remove(t)"
      />
      <button type="button" class="add-tag-btn" @click="open = !open">
        <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
          <path d="M6 1.5v9M1.5 6h9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </button>
    </div>

    <div v-if="open" class="picker-dropdown">
      <div class="picker-backdrop" @click="open = false"></div>
      <div class="picker-menu">
        <div class="picker-header">
          <input
            ref="searchInput"
            v-model="search"
            type="text"
            placeholder="Find or create tag..."
            class="picker-search"
            @keydown.enter="handleCreate"
          />
        </div>
        <div class="picker-body">
          <div
            v-for="t in filtered"
            :key="t.id"
            class="picker-item"
            :class="{ 'picker-item--on': selectedIds.has(t.id) }"
            @click="toggle(t)"
          >
            <TagChip :tag="t" />
            <svg v-if="selectedIds.has(t.id)" class="check" viewBox="0 0 12 12" fill="none" width="12" height="12">
              <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div v-if="search && !exists" class="picker-create" @click="handleCreate">
            Create "<strong>{{ search }}</strong>"
            <span class="create-hint">Enter ↵</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { Tag } from '../../types'
import { useTagStore } from '../../stores/tags'
import TagChip from './TagChip.vue'

const props = defineProps<{
  projectId: number
  modelValue: Tag[]
}>()

const emit = defineEmits<{
  'update:modelValue': [tags: Tag[]]
}>()

const tagStore = useTagStore()
const open = ref(false)
const search = ref('')
const searchInput = ref<HTMLInputElement>()

const selected = computed(() => props.modelValue)
const selectedIds = computed(() => new Set(selected.value.map((t) => t.id)))

const allTags = computed(() => tagStore.tags)
const exists = computed(() => allTags.value.some((t) => t.name.toLowerCase() === search.value.toLowerCase()))
const filtered = computed(() =>
  search.value
    ? allTags.value.filter((t) => t.name.toLowerCase().includes(search.value.toLowerCase()))
    : allTags.value
)

watch(open, async (v) => {
  if (v) {
    await tagStore.fetchByProject(props.projectId)
    await nextTick()
    searchInput.value?.focus()
  } else {
    search.value = ''
  }
})

function toggle(t: Tag) {
  const ids = selectedIds.value
  if (ids.has(t.id)) {
    emit('update:modelValue', selected.value.filter((x) => x.id !== t.id))
  } else {
    emit('update:modelValue', [...selected.value, t])
  }
}

function remove(t: Tag) {
  emit('update:modelValue', selected.value.filter((x) => x.id !== t.id))
}

async function handleCreate() {
  if (!search.value.trim() || exists.value) return
  const t = await tagStore.create(props.projectId, search.value.trim(), '#6366f1')
  emit('update:modelValue', [...selected.value, t])
  search.value = ''
}
</script>

<style scoped>
.tag-picker { position: relative; }

.picker-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-light);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
  min-height: 26px;
}

.tag-chip-btn { cursor: pointer; }
.tag-chip-btn:hover { opacity: 0.75; }

.add-tag-btn {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  border: 1.5px dashed var(--border-strong);
  background: transparent;
  color: var(--text-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: border-color 0.12s, color 0.12s;
}
.add-tag-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

/* Dropdown */
.picker-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
}

.picker-dropdown { position: relative; z-index: 51; }

.picker-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.14);
  overflow: hidden;
  max-height: 260px;
  display: flex;
  flex-direction: column;
}

.picker-header { padding: 8px; border-bottom: 1px solid var(--border); }

.picker-search {
  width: 100%;
  padding: 8px 10px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  font-family: inherit;
  font-size: 13px;
  color: var(--text);
  outline: none;
}
.picker-search:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-muted); }

.picker-body { overflow-y: auto; flex: 1; padding: 4px 0; }

.picker-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  cursor: pointer;
  transition: background 0.1s;
}
.picker-item:hover { background: var(--bg); }
.picker-item--on { background: var(--primary-light); }

.check { color: var(--primary); flex-shrink: 0; }

.picker-create {
  padding: 8px 10px;
  color: var(--primary);
  font-size: 13px;
  cursor: pointer;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.picker-create:hover { background: var(--bg); }
.create-hint { font-size: 11px; color: var(--text-light); }
</style>
