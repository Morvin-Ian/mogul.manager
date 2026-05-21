<template>
  <div class="sk-board">
    <div v-for="col in 4" :key="col" class="sk-col">
      <div class="sk-col-header">
        <div class="sk-line sk-col-title"></div>
        <div class="sk-pill"></div>
      </div>
      <div class="sk-col-body">
        <div
          v-for="card in colSizes[col - 1]"
          :key="card"
          class="sk-task"
          :style="`animation-delay: ${(col - 1) * 80 + card * 60}ms`"
        >
          <div class="sk-line sk-task-title"></div>
          <div class="sk-line sk-task-sub"></div>
          <div class="sk-task-foot">
            <div class="sk-dot"></div>
            <div class="sk-line sk-task-date"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const colSizes = [3, 2, 1, 2]
</script>

<style scoped>
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position:  400px 0; }
}

.sk-board {
  display: flex;
  gap: 12px;
}

.sk-col {
  flex: 0 0 240px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.sk-col-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
}

.sk-col-body {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sk-task {
  background: var(--bg);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.sk-task-foot {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 2px;
}

.sk-line,
.sk-pill,
.sk-dot {
  background: linear-gradient(
    90deg,
    #EEF0F3 25%,
    #E2E5EA 50%,
    #EEF0F3 75%
  );
  background-size: 400px 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: 6px;
}

.sk-col-title   { height: 10px; width: 72px; }
.sk-pill        { height: 18px; width: 28px; border-radius: 999px; }
.sk-task-title  { height: 12px; width: 85%; }
.sk-task-sub    { height: 11px; width: 60%; }
.sk-task-date   { height: 10px; width: 52px; }
.sk-dot         { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
</style>
