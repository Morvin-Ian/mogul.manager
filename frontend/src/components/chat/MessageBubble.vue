<template>
  <div class="message" :class="[role === 'user' ? 'message-user' : 'message-assistant', { 'message-streaming': streaming }]">
    <div class="message-avatar">
      {{ role === 'user' ? 'U' : 'AI' }}
    </div>
    <div class="message-content">
      <div class="message-text">
        <span v-if="streaming && !content">{{ cursor }}</span>
        <span v-else>{{ content }}</span>
        <span v-if="streaming && content" class="cursor-blink">|</span>
      </div>
      <div v-if="!streaming && content" class="message-time">{{ time }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  role: string
  content: string
  streaming?: boolean
  createdAt?: string
}>()

const time = computed(() => {
  if (!props.createdAt) return ''
  return new Date(props.createdAt).toLocaleTimeString()
})

const cursor = computed(() => {
  const indicators = ['▊']
  return indicators[0]
})
</script>
