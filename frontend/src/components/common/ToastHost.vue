<template>
  <Teleport to="body">
    <div class="toast-host" aria-live="polite">
      <TransitionGroup name="toast">
        <div
          v-for="t in state.toasts"
          :key="t.id"
          class="toast"
          :class="`toast--${t.kind}`"
          :role="t.kind === 'error' ? 'alert' : 'status'"
        >
          <span class="toast-icon">
            <font-awesome-icon v-if="t.kind === 'success'" :icon="['fas', 'circle-check']" />
            <font-awesome-icon v-else-if="t.kind === 'error'" :icon="['fas', 'circle-exclamation']" />
            <font-awesome-icon v-else :icon="['fas', 'circle-info']" />
          </span>
          <span class="toast-msg">{{ t.message }}</span>
          <button
            v-if="t.actionLabel"
            class="toast-action"
            @click="runAction(t)"
          >{{ t.actionLabel }}</button>
          <button class="toast-close" aria-label="Dismiss notification" @click="dismiss(t.id)">
            <font-awesome-icon :icon="['fas', 'xmark']" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast, type Toast } from '../../composables/useToast'

const { state, dismiss } = useToast()

function runAction(t: Toast) {
  dismiss(t.id)
  t.onAction?.()
}
</script>

<style scoped>
.toast-host {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  pointer-events: none;
  width: min(440px, calc(100vw - 32px));
}

.toast {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 11px 14px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow);
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text);
  line-height: 1.45;
}

.toast-icon { flex-shrink: 0; font-size: 15px; display: flex; }
.toast--success .toast-icon { color: var(--success); }
.toast--error   .toast-icon { color: var(--danger); }
.toast--info    .toast-icon { color: var(--primary); }

.toast--error { border-color: var(--danger-border); }
.toast--success { border-color: var(--success-border); }

.toast-msg { flex: 1; min-width: 0; }

.toast-action {
  flex-shrink: 0;
  background: none;
  border: none;
  font-family: inherit;
  font-size: 12.5px;
  font-weight: 700;
  color: var(--primary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 7px;
  transition: background 0.12s;
}
.toast-action:hover { background: var(--primary-muted); }

.toast-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  font-size: 13px;
  padding: 4px 6px;
  border-radius: 6px;
  display: flex;
  transition: color 0.12s, background 0.12s;
}
.toast-close:hover { color: var(--text); background: var(--bg); }

/* Transitions */
.toast-enter-active { transition: opacity 0.2s ease, transform 0.2s cubic-bezier(0.34, 1.3, 0.64, 1); }
.toast-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.toast-enter-from { opacity: 0; transform: translateY(10px) scale(0.96); }
.toast-leave-to { opacity: 0; transform: translateY(6px); }
.toast-move { transition: transform 0.2s ease; }
</style>
