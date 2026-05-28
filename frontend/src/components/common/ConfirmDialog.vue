<template>
  <Teleport to="body">
    <Transition name="cd-fade">
      <div
        v-if="state.open"
        class="cd-overlay"
        tabindex="-1"
        ref="overlayRef"
        @click.self="respond(false)"
        @keydown.esc.prevent="respond(false)"
        @keydown.enter.prevent="respond(true)"
      >
        <Transition name="cd-pop">
          <div v-if="state.open" class="cd-modal" role="alertdialog" :aria-modal="true">
            <div class="cd-icon-wrap" :class="state.danger ? 'icon-danger' : 'icon-warn'">
              <!-- Trash icon for danger -->
              <svg v-if="state.danger" viewBox="0 0 24 24" fill="none" width="22" height="22">
                <path d="M3 6h18M8 6V4a1 1 0 011-1h6a1 1 0 011 1v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 11v6M14 11v6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
              <!-- Warning triangle for non-danger -->
              <svg v-else viewBox="0 0 24 24" fill="none" width="22" height="22">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                <line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>

            <h3 class="cd-title">{{ state.title }}</h3>
            <p class="cd-message">{{ state.message }}</p>

            <ul v-if="state.consequences.length" class="cd-consequences">
              <li v-for="(item, i) in state.consequences" :key="i">{{ item }}</li>
            </ul>

            <div class="cd-actions">
              <button class="cd-btn cd-cancel" @click="respond(false)">
                {{ state.cancelLabel }}
              </button>
              <button
                class="cd-btn"
                :class="state.danger ? 'cd-confirm-danger' : 'cd-confirm-primary'"
                ref="confirmBtn"
                @click="respond(true)"
              >
                {{ state.confirmLabel }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useConfirm } from '../../composables/useConfirm'

const { state, respond } = useConfirm()
const overlayRef = ref<HTMLElement | null>(null)
const confirmBtn = ref<HTMLButtonElement | null>(null)

watch(() => state.open, (v) => {
  if (v) nextTick(() => { overlayRef.value?.focus() })
})
</script>

<style scoped>
.cd-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  outline: none;
}

.cd-modal {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 20px;
  padding: 32px 32px 28px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18), 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0;
}

.cd-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
  flex-shrink: 0;
}

.icon-danger {
  background: #FFF1F2;
  border: 1.5px solid #FECDD3;
  color: #BE123C;
}

.icon-warn {
  background: #FFFBEB;
  border: 1.5px solid #FDE68A;
  color: #92400E;
}

.cd-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.4px;
  line-height: 1.25;
  margin-bottom: 10px;
}

.cd-message {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.65;
  margin-bottom: 0;
}

.cd-consequences {
  list-style: none;
  padding: 0;
  margin: 14px 0 0;
  width: 100%;
  background: #FFF1F2;
  border: 1.5px solid #FECDD3;
  border-radius: 10px;
  padding: 12px 16px;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.cd-consequences li {
  font-size: 13px;
  color: #9F1239;
  font-weight: 500;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.cd-consequences li::before {
  content: '•';
  font-size: 16px;
  line-height: 1.2;
  flex-shrink: 0;
  color: #F43F5E;
}

.cd-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
  width: 100%;
}

.cd-btn {
  flex: 1;
  padding: 11px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  font-family: inherit;
  transition: opacity 0.14s, transform 0.1s, box-shadow 0.14s;
  letter-spacing: -0.1px;
}

.cd-btn:active { transform: scale(0.97); }

.cd-cancel {
  background: var(--bg);
  color: var(--text-muted);
  border: 1.5px solid var(--border);
}

.cd-cancel:hover {
  background: var(--surface);
  color: var(--text);
  border-color: var(--border-strong);
}

.cd-confirm-primary {
  background: #0052FF;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 82, 255, 0.25);
}

.cd-confirm-primary:hover { opacity: 0.88; }

.cd-confirm-danger {
  background: #DC2626;
  color: #fff;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
}

.cd-confirm-danger:hover { opacity: 0.88; }

/* Transitions */
.cd-fade-enter-active,
.cd-fade-leave-active { transition: opacity 0.2s ease; }
.cd-fade-enter-from,
.cd-fade-leave-to { opacity: 0; }

.cd-pop-enter-active { transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1); }
.cd-pop-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.cd-pop-enter-from { opacity: 0; transform: scale(0.88) translateY(12px); }
.cd-pop-leave-to { opacity: 0; transform: scale(0.94); }

/* Dark mode */
:global([data-theme="dark"]) .cd-modal {
  background: var(--surface);
  border-color: var(--border);
}

:global([data-theme="dark"]) .cd-consequences {
  background: rgba(220, 38, 38, 0.12);
  border-color: rgba(220, 38, 38, 0.3);
}

:global([data-theme="dark"]) .cd-consequences li { color: #FDA4AF; }
:global([data-theme="dark"]) .cd-consequences li::before { color: #F87171; }

:global([data-theme="dark"]) .icon-danger {
  background: rgba(220, 38, 38, 0.15);
  border-color: rgba(220, 38, 38, 0.3);
  color: #F87171;
}

:global([data-theme="dark"]) .icon-warn {
  background: rgba(217, 119, 6, 0.15);
  border-color: rgba(217, 119, 6, 0.3);
  color: #FCD34D;
}
</style>
