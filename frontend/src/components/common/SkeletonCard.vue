<template>
  <div class="sk-card">
    <div class="sk-line sk-title"></div>
    <div class="sk-line sk-body"></div>
    <div class="sk-line sk-body sk-body-short"></div>
    <div class="sk-footer">
      <div class="sk-pill"></div>
      <div class="sk-pill sk-pill-sm"></div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position:  400px 0; }
}

.sk-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sk-line,
.sk-pill {
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

.sk-title       { height: 14px; width: 60%; }
.sk-body        { height: 12px; width: 100%; }
.sk-body-short  { width: 75%; }

.sk-footer {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.sk-pill    { height: 20px; width: 64px; border-radius: 999px; }
.sk-pill-sm { width: 44px; }
</style>
