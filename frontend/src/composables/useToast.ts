import { reactive } from 'vue'

export type ToastKind = 'success' | 'error' | 'info'

export interface Toast {
  id: number
  kind: ToastKind
  message: string
  /** Optional action button (e.g. retry) */
  actionLabel?: string
  onAction?: () => void
}

const state = reactive({
  toasts: [] as Toast[],
})

let nextId = 1

const DURATION: Record<ToastKind, number> = {
  success: 3500,
  info: 4500,
  error: 6000,
}

function push(kind: ToastKind, message: string, opts?: { actionLabel?: string; onAction?: () => void }) {
  const id = nextId++
  state.toasts.push({ id, kind, message, ...opts })
  setTimeout(() => dismiss(id), DURATION[kind])
  return id
}

function dismiss(id: number) {
  const idx = state.toasts.findIndex(t => t.id === id)
  if (idx !== -1) state.toasts.splice(idx, 1)
}

export function useToast() {
  return {
    state,
    dismiss,
    success: (msg: string) => push('success', msg),
    info: (msg: string) => push('info', msg),
    error: (msg: string, opts?: { actionLabel?: string; onAction?: () => void }) =>
      push('error', msg, opts),
  }
}
