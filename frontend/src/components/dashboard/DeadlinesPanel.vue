<template>
  <div class="panel">
    <div class="panel-hdr">
      <span class="panel-title">Upcoming Deadlines</span>
      <svg viewBox="0 0 16 16" fill="none" width="15" height="15" style="color:var(--text-muted)">
        <rect x="1" y="3" width="14" height="12" rx="2" stroke="currentColor" stroke-width="1.4"/>
        <path d="M1 7h14M5 1v4M11 1v4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
      </svg>
    </div>

    <div v-if="upcomingDeadlines.length === 0" class="deadlines-empty">
      <svg viewBox="0 0 48 48" fill="none" width="40" height="40">
        <rect x="6" y="10" width="36" height="32" rx="4" stroke="#D1D5DB" stroke-width="2"/>
        <path d="M6 18h36M16 6v8M32 6v8" stroke="#D1D5DB" stroke-width="2" stroke-linecap="round"/>
        <path d="M14 28h8M14 34h12" stroke="#D1D5DB" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <p>No upcoming deadlines</p>
      <span>Tasks and projects with due dates appear here</span>
    </div>

    <div v-else class="deadlines-list">
      <div
        v-for="item in upcomingDeadlines"
        :key="item.id"
        class="deadline-row"
        :class="`urgency-${item.urgency}`"
        @click="$router.push(`/projects/${item.projectId}`)"
      >
        <span class="deadline-badge" :class="`dl-badge-${item.urgency}`">
          {{ item.label }}
        </span>
        <div class="deadline-info">
          <p class="deadline-title">{{ item.title }}</p>
          <p class="deadline-sub">
            <span class="deadline-type-dot" :class="item.type" />
            <span class="deadline-sub-label">{{ item.subtitle }}</span>
            <span class="deadline-date">{{ item.formattedDate }}</span>
          </p>
        </div>
        <span class="deadline-type-icon" :class="item.type">
          <svg v-if="item.type === 'task'" viewBox="0 0 16 16" fill="none" width="12" height="12">
            <rect x="1.5" y="1.5" width="13" height="13" rx="2" stroke="currentColor" stroke-width="1.5"/>
            <path d="M5.5 8.5l2 2 3-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else viewBox="0 0 16 16" fill="none" width="12" height="12">
            <path d="M2 5h12M5 2v3M11 2v3M3 3h10a1 1 0 011 1v9a1 1 0 01-1 1H3a1 1 0 01-1-1V4a1 1 0 011-1z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task, Project } from '../../types'

const props = defineProps<{ tasks: Task[]; projects: Project[] }>()

type Urgency = 'overdue' | 'today' | 'soon' | 'later'

function classifyDeadline(date: Date): { label: string; urgency: Urgency } {
  const diff = Math.floor((date.getTime() - Date.now()) / 86400000)
  if (diff < 0)  return { label: `${Math.abs(diff)}d ago`, urgency: 'overdue' }
  if (diff === 0) return { label: 'Today',                  urgency: 'today' }
  if (diff === 1) return { label: 'Tomorrow',               urgency: 'soon' }
  if (diff <= 7)  return { label: `${diff}d left`,          urgency: 'soon' }
  return             { label: `${diff}d left`,               urgency: 'later' }
}

function projectNameFor(projectId: number): string {
  return props.projects.find(p => p.id === projectId)?.title ?? 'Unknown Project'
}

const upcomingDeadlines = computed(() => {
  function fmt(d: Date): string {
    const today = new Date()
    const sameYear = d.getFullYear() === today.getFullYear()
    return d.toLocaleDateString('en-US', {
      month: 'short', day: 'numeric',
      ...(sameYear ? {} : { year: 'numeric' }),
    })
  }

  const taskItems = props.tasks
    .filter(t => t.due_date && t.status !== 'completed')
    .map(t => {
      const d = new Date(t.due_date!)
      const { label, urgency } = classifyDeadline(d)
      return {
        id: `task-${t.id}`,
        title: t.title,
        subtitle: projectNameFor(t.project_id),
        dueDate: d,
        formattedDate: fmt(d),
        type: 'task' as const,
        projectId: t.project_id,
        label,
        urgency,
      }
    })

  const projItems = props.projects
    .filter(p => p.due_date && p.status !== 'completed' && p.status !== 'archived')
    .map(p => {
      const d = new Date(p.due_date!)
      const { label, urgency } = classifyDeadline(d)
      return {
        id: `proj-${p.id}`,
        title: p.title,
        subtitle: 'Project deadline',
        dueDate: d,
        formattedDate: fmt(d),
        type: 'project' as const,
        projectId: p.id,
        label,
        urgency,
      }
    })

  return [...taskItems, ...projItems]
    .sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime())
    .slice(0, 20)
})
</script>

<style scoped>
/* ── Deadlines Panel ─────────────────── */
.deadlines-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 0 12px;
  text-align: center;
}
.deadlines-empty p {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}
.deadlines-empty span {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.5;
}

.deadlines-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 420px;
  overflow-y: auto;
  padding-right: 2px;
}
.deadlines-list::-webkit-scrollbar { width: 4px; }
.deadlines-list::-webkit-scrollbar-track { background: transparent; }
.deadlines-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

.deadline-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 16px;
  border-radius: 14px;
  border: 1.5px solid transparent;
  cursor: pointer;
  transition: filter 0.12s, transform 0.12s;
}
.deadline-row:hover { filter: brightness(0.97); transform: translateX(2px); }

.urgency-overdue { background: #F5DEDE; border-color: #CC8888; }
.urgency-today   { background: #F5E4CC; border-color: #D0A060; }
.urgency-soon    { background: #E5E2FF; border-color: #B0A8E8; }
.urgency-later   { background: #D8F0DC; border-color: #70C888; }

.deadline-badge {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
  min-width: 72px;
  text-align: center;
}
.dl-badge-overdue { background: #D07878; color: #601010; }
.dl-badge-today   { background: #CFA060; color: #6A3008; }
.dl-badge-soon    { background: #C0BAF0; color: #3830A0; }
.dl-badge-later   { background: #68CC80; color: #145820; }

.deadline-info { flex: 1; min-width: 0; }

.deadline-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.deadline-sub {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
}

.deadline-type-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.deadline-type-dot.task    { background: #5250C0; }
.deadline-type-dot.project { background: #B06030; }

.deadline-sub-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.deadline-date {
  margin-left: auto;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-light);
  white-space: nowrap;
  flex-shrink: 0;
}

.deadline-type-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(0,0,0,0.05);
  color: var(--text-light);
}
.urgency-overdue .deadline-type-icon.task    { color: #601010; background: rgba(96,16,16,0.12); }
.urgency-overdue .deadline-type-icon.project { color: #601010; background: rgba(96,16,16,0.12); }
.urgency-today   .deadline-type-icon.task    { color: #6A3008; background: rgba(106,48,8,0.12); }
.urgency-today   .deadline-type-icon.project { color: #6A3008; background: rgba(106,48,8,0.12); }
.urgency-soon    .deadline-type-icon.task    { color: #3830A0; background: rgba(56,48,160,0.12); }
.urgency-soon    .deadline-type-icon.project { color: #3830A0; background: rgba(56,48,160,0.12); }
.urgency-later   .deadline-type-icon.task    { color: #145820; background: rgba(20,88,32,0.12); }
.urgency-later   .deadline-type-icon.project { color: #145820; background: rgba(20,88,32,0.12); }
</style>
