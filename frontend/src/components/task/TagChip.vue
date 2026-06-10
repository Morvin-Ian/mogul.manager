<template>
  <span class="tag-chip" :style="{ background: bgColor, color: textColor }">
    {{ tag.name }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Tag } from '../../types'

const props = defineProps<{ tag: Tag }>()

const hex = computed(() => props.tag.color)

function hexToRgb(h: string) {
  const r = parseInt(h.slice(1, 3), 16)
  const g = parseInt(h.slice(3, 5), 16)
  const b = parseInt(h.slice(5, 7), 16)
  return { r, g, b }
}

const bgColor = computed(() => {
  const c = hexToRgb(hex.value)
  return `rgba(${c.r}, ${c.g}, ${c.b}, 0.18)`
})

const textColor = computed(() => {
  const c = hexToRgb(hex.value)
  const lum = (0.299 * c.r + 0.587 * c.g + 0.114 * c.b) / 255
  if (lum > 0.6) {
    return `hsl(0, 0%, 20%)`
  }
  return hex.value
})
</script>

<style scoped>
.tag-chip {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.1px;
  white-space: nowrap;
  line-height: 1.4;
}
</style>
