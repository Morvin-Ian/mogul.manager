import { ref, watch } from 'vue'

const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
const stored = localStorage.getItem('theme')
const isDark = ref(stored ? stored === 'dark' : prefersDark)

function applyTheme(dark: boolean) {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
}

applyTheme(isDark.value)

watch(isDark, (dark) => {
  applyTheme(dark)
  localStorage.setItem('theme', dark ? 'dark' : 'light')
})

export function useTheme() {
  function toggle() {
    isDark.value = !isDark.value
  }
  return { isDark, toggle }
}
