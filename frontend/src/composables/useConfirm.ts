import { reactive } from 'vue'

interface ConfirmOptions {
  title: string
  message: string
  consequences?: string[]
  confirmLabel?: string
  cancelLabel?: string
  danger?: boolean
}

const state = reactive({
  open: false,
  title: '',
  message: '',
  consequences: [] as string[],
  confirmLabel: 'Confirm',
  cancelLabel: 'Cancel',
  danger: false,
  resolve: null as ((v: boolean) => void) | null,
})

export function useConfirm() {
  function confirm(opts: ConfirmOptions): Promise<boolean> {
    return new Promise((resolve) => {
      state.open = true
      state.title = opts.title
      state.message = opts.message
      state.consequences = opts.consequences ?? []
      state.confirmLabel = opts.confirmLabel ?? 'Confirm'
      state.cancelLabel = opts.cancelLabel ?? 'Cancel'
      state.danger = opts.danger ?? false
      state.resolve = resolve
    })
  }

  function respond(value: boolean) {
    state.open = false
    state.resolve?.(value)
    state.resolve = null
  }

  return { state, confirm, respond }
}
