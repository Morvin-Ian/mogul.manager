<template>
  <div class="settings-card" id="ai-section">
    <h3 class="settings-card-title">AI Provider</h3>

    <p class="ai-intro">
      Choose which vendor answers your chats, plans and document summaries, and
      store your own API key for it. Keys are encrypted before they are saved
      and are never sent back to the browser.
    </p>

    <p v-if="store.loading && !store.providers.length" class="ai-loading">
      <span class="spinner spinner-sm"></span> Loading providers…
    </p>
    <p v-else-if="store.error" class="form-error" style="margin: 0 24px 12px;">{{ store.error }}</p>

    <!-- One row per supported vendor -->
    <div class="info-rows">
      <div
        v-for="p in store.providers"
        :key="p.slug"
        class="info-row provider-row"
        :class="{ open: openSlug === p.slug }"
      >
        <div class="provider-head" @click="toggle(p)">
          <span
            class="info-dot"
            :class="p.is_active ? 'dot-active' : (p.configured ? 'dot-stored' : '')"
          ></span>
          <div class="info-content">
            <span class="info-label">{{ p.label }}</span>
            <span class="provider-desc">{{ p.description }}</span>
            <span v-if="p.configured" class="provider-meta">
              Key ••••{{ p.key_hint }}<template v-if="p.model"> · {{ p.model }}</template>
            </span>
          </div>

          <span v-if="p.is_active" class="online-badge">In use</span>
          <span v-else-if="p.configured" class="stored-badge">Stored</span>
          <span v-else class="unset-badge">Not set</span>

          <font-awesome-icon
            class="provider-chevron"
            :icon="['fas', openSlug === p.slug ? 'chevron-up' : 'chevron-down']"
          />
        </div>

        <!-- Expanded editor -->
        <form v-if="openSlug === p.slug" class="provider-form" @submit.prevent="save(p)">
          <div class="form-row">
            <div class="form-group">
              <label :for="`key-${p.slug}`">API key</label>
              <input
                :id="`key-${p.slug}`"
                v-model="form.api_key"
                type="password"
                autocomplete="off"
                spellcheck="false"
                :placeholder="p.configured ? 'Leave blank to keep the stored key' : 'Paste your API key'"
              />
            </div>
            <div class="form-group">
              <label :for="`model-${p.slug}`">
                Model
                <span v-if="p.requires_model" class="req">required</span>
                <span v-else class="opt">optional</span>
              </label>
              <input
                :id="`model-${p.slug}`"
                v-model="form.model"
                type="text"
                spellcheck="false"
                :placeholder="p.requires_model
                  ? `e.g. ${p.model_example}`
                  : `Defaults to ${p.default_model}`"
              />
            </div>
          </div>

          <p class="provider-hint">
            <a :href="p.signup_url" target="_blank" rel="noopener">Get a key</a>
            ·
            <a :href="p.catalog_url" target="_blank" rel="noopener">Browse models</a>
            <template v-if="p.requires_model">
              — {{ p.label }} fronts many vendors, so it needs an explicit model id.
            </template>
          </p>

          <p v-if="rowError" class="form-error">{{ rowError }}</p>
          <p v-if="rowSuccess" class="inline-success">{{ rowSuccess }}</p>

          <div class="provider-actions">
            <button
              v-if="p.configured"
              type="button"
              class="btn-quiet danger"
              :disabled="busy"
              @click="remove(p)"
            >
              Remove key
            </button>
            <span class="spacer"></span>
            <button type="button" class="btn-quiet" :disabled="busy" @click="test(p)">
              <span v-if="testing" class="spinner spinner-sm"></span>
              {{ testing ? 'Testing…' : 'Test connection' }}
            </button>
            <button type="submit" class="btn btn-primary" :disabled="busy">
              <span v-if="saving" class="spinner spinner-white"></span>
              {{ saving ? 'Saving…' : (p.is_active ? 'Save' : 'Save & use') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <p v-if="!store.loading && !store.active" class="ai-fallback">
      No provider selected — the server's own DeepSeek key is being used.
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import type { AIProvider } from '../../types'
import { useAiProvidersStore } from '../../stores/aiProviders'

const store = useAiProvidersStore()

const openSlug = ref<string | null>(null)
const form = reactive({ api_key: '', model: '' })
const saving = ref(false)
const testing = ref(false)
const removing = ref(false)
const rowError = ref<string | null>(null)
const rowSuccess = ref<string | null>(null)

const busy = computed(() => saving.value || testing.value || removing.value)

onMounted(() => { store.fetchProviders().catch(() => {}) })

function toggle(p: AIProvider) {
  if (openSlug.value === p.slug) { openSlug.value = null; return }
  openSlug.value = p.slug
  // The key is never sent back, so the field always starts blank; a stored
  // key is kept when it is left that way.
  form.api_key = ''
  form.model = p.model ?? ''
  rowError.value = null
  rowSuccess.value = null
}

async function save(p: AIProvider) {
  rowError.value = null
  rowSuccess.value = null
  if (!p.configured && !form.api_key.trim()) {
    rowError.value = `Paste your ${p.label} API key first.`
    return
  }
  if (p.requires_model && !form.model.trim()) {
    rowError.value = `${p.label} needs a model id (for example ${p.model_example}).`
    return
  }
  saving.value = true
  try {
    await store.saveProvider(p.slug, {
      api_key: form.api_key.trim() || undefined,
      model: form.model.trim() || null,
      activate: true,
    })
    form.api_key = ''
    rowSuccess.value = `${p.label} saved and now in use.`
  } catch (e) {
    rowError.value = (e as Error).message
  } finally {
    saving.value = false
  }
}

async function test(p: AIProvider) {
  rowError.value = null
  rowSuccess.value = null
  if (!p.configured && !form.api_key.trim()) {
    rowError.value = `Paste your ${p.label} API key first.`
    return
  }
  testing.value = true
  try {
    const res = await store.testProvider(p.slug, {
      api_key: form.api_key.trim() || undefined,
      model: form.model.trim() || null,
    })
    if (res.ok) rowSuccess.value = res.message
    else rowError.value = res.message
  } catch (e) {
    rowError.value = (e as Error).message
  } finally {
    testing.value = false
  }
}

async function remove(p: AIProvider) {
  rowError.value = null
  rowSuccess.value = null
  removing.value = true
  try {
    await store.removeProvider(p.slug)
    form.api_key = ''
    form.model = ''
    openSlug.value = null
  } catch (e) {
    rowError.value = (e as Error).message
  } finally {
    removing.value = false
  }
}
</script>

<style scoped>
/* Card chrome. ProfileSettings styles its own cards in a scoped block, which
   reaches this component's root element but nothing inside it — so the panel
   carries its own copy and stays self-contained wherever it is mounted. */
.settings-card {
  background: #fff;
  border-radius: 18px;
  border: 1.5px solid var(--border);
  box-shadow: 0 2px 12px rgba(10,11,13,0.06);
  overflow: hidden;
}

.settings-card-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
  padding: 20px 24px 6px;
}

.info-rows { display: flex; flex-direction: column; }

.info-row { border-top: 1px solid var(--border); }

.info-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--border-strong);
  flex-shrink: 0;
}
.info-dot.dot-active { background: var(--success); }
.info-dot.dot-stored { background: var(--primary); }

.info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.info-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.online-badge {
  flex-shrink: 0;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
  background: #EBF5EC;
  color: #285830;
  border: 1px solid #B4D4BA;
}

.form-error { margin-top: 10px; }

.ai-intro {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
  padding: 0 24px 14px;
}

.ai-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
  padding: 0 24px 16px;
}

.ai-fallback {
  font-size: 12.5px;
  color: var(--text-light);
  padding: 14px 24px 20px;
}

/* Provider rows stack a clickable head over an optional form */
.provider-row.open { background: var(--bg); }

.provider-head {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 13px 24px;
  cursor: pointer;
  transition: background 0.1s;
}
.provider-head:hover { background: var(--bg); }

.provider-desc {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.45;
}

.provider-meta {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 3px;
  font-variant-numeric: tabular-nums;
}

.provider-chevron {
  flex-shrink: 0;
  font-size: 11px;
  color: var(--text-light);
}

.stored-badge,
.unset-badge {
  flex-shrink: 0;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
}
.stored-badge { background: #EEF0F8; color: #4A4676; border: 1px solid #CBD0E6; }
.unset-badge  { background: var(--bg); color: var(--text-light); border: 1px solid var(--border); }

.provider-form {
  padding: 4px 24px 20px;
  border-top: 1px solid var(--border);
  margin-top: 2px;
}

.provider-form label .req,
.provider-form label .opt {
  font-size: 11px;
  font-weight: 600;
  margin-left: 6px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.provider-form label .req { color: #682828; }
.provider-form label .opt { color: var(--text-light); }

.provider-hint {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.5;
  margin-top: 10px;
}
.provider-hint a { color: #4A4676; font-weight: 600; }

.provider-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 16px;
}
.provider-actions .spacer { flex: 1; }

.btn-quiet {
  padding: 8px 16px;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--border);
  background: #fff;
  color: var(--text);
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  transition: background 0.12s, border-color 0.12s, color 0.12s;
}
.btn-quiet:hover:not(:disabled) { background: var(--bg); border-color: var(--border-strong); }
.btn-quiet:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-quiet.danger { color: #682828; border-color: #D8BCBC; }
.btn-quiet.danger:hover:not(:disabled) { background: #F5ECEC; }

.provider-actions .btn-primary {
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  padding: 9px 20px;
  box-shadow: none;
}
.provider-actions .btn-primary:hover:not(:disabled) { background: #2e2e30; }

.spinner {
  display: inline-block;
  width: 13px;
  height: 13px;
  border: 2px solid rgba(0,0,0,0.12);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.65s linear infinite;
  flex-shrink: 0;
}
.spinner-white { border-color: rgba(255,255,255,0.3); border-top-color: #fff; }
.spinner-sm { width: 11px; height: 11px; }

@keyframes spin { to { transform: rotate(360deg); } }

.inline-success {
  font-size: 13px;
  font-weight: 500;
  color: #285830;
  background: #EBF5EC;
  border: 1px solid #B4D4BA;
  padding: 9px 13px;
  border-radius: 9px;
  margin-top: 10px;
}
</style>
