<template>
  <div class="loading-wrap" :class="`size-${size}`">
    <div class="spinner-ring">
      <svg viewBox="0 0 44 44" fill="none">
        <circle cx="22" cy="22" r="18" stroke-width="3" class="track" />
        <circle cx="22" cy="22" r="18" stroke-width="3" class="arc" />
      </svg>
    </div>
    <p v-if="label" class="loading-label">{{ label }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  size?: 'sm' | 'md' | 'lg'
  label?: string
}>(), {
  size: 'md',
  label: '',
})
</script>

<style scoped>
.loading-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 60px 20px;
  width: 100%;
}

.size-sm { padding: 24px 12px; gap: 10px; }
.size-lg { padding: 80px 20px; gap: 18px; }

.spinner-ring {
  animation: spin 0.75s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.size-sm  .spinner-ring { width: 24px; height: 24px; }
.size-md  .spinner-ring { width: 36px; height: 36px; }
.size-lg  .spinner-ring { width: 52px; height: 52px; }

.track { stroke: var(--primary-muted); }
.arc {
  stroke: var(--primary);
  stroke-linecap: round;
  stroke-dasharray: 80;
  stroke-dashoffset: 60;
}

.loading-label {
  font-size: 13px;
  color: var(--text-muted);
  letter-spacing: 0.1px;
  animation: fade-pulse 1.6s ease-in-out infinite;
}

.size-sm .loading-label { font-size: 12px; }
.size-lg .loading-label { font-size: 14px; }

@keyframes spin { to { transform: rotate(360deg); } }

@keyframes fade-pulse {
  0%, 100% { opacity: 0.5; }
  50%       { opacity: 1; }
}
</style>
