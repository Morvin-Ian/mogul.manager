<template>
  <div class="comments-tab">
    <div class="comment-compose">
      <div class="compose-avatar" :style="auth.user?.profile_path ? {} : { background: memberGradient(auth.user?.username || 'U') }">
        <img v-if="auth.user?.profile_path" :src="auth.user.profile_path" :alt="auth.user?.username" class="avatar-img" />
        <span v-else>{{ (auth.user?.username || 'U').charAt(0).toUpperCase() }}</span>
      </div>
      <div class="compose-field" :class="{ 'compose-field--focused': commentFocused }">
        <textarea
          v-model="newComment"
          rows="2"
          placeholder="Write a comment…"
          class="compose-textarea"
          @focus="commentFocused = true"
          @blur="commentFocused = false"
        ></textarea>
        <div class="compose-actions">
          <button
            class="btn-post"
            :disabled="!newComment.trim() || postingComment"
            @click="addComment"
          >
            {{ postingComment ? 'Posting…' : 'Post' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="feed-empty">Loading comments…</div>
    <div v-else-if="comments.length === 0" class="feed-empty">No comments yet. Be the first!</div>
    <div v-else class="comments-feed">
      <div v-for="c in comments" :key="c.id" class="feed-item">
        <div class="feed-avatar" :style="(c.user?.profile_path || auth.user?.profile_path) ? {} : { background: memberGradient(c.user?.username || auth.user?.username || 'U') }">
          <img v-if="c.user?.profile_path || auth.user?.profile_path" :src="c.user?.profile_path || auth.user?.profile_path || ''" :alt="c.user?.username || auth.user?.username" class="avatar-img" />
          <span v-else>{{ (c.user?.username || auth.user?.username || 'U').charAt(0).toUpperCase() }}</span>
        </div>
        <div class="feed-body">
          <div class="feed-meta">
            <span class="feed-author">{{ c.user?.username || auth.user?.username }}</span>
            <span class="feed-time">{{ timeAgo(c.created_at) }}</span>
            <button
              v-if="c.user_id === auth.user?.id"
              class="feed-delete"
              @click="handleDeleteComment(c.id)"
              title="Delete comment"
            >
              <font-awesome-icon :icon="['fas', 'trash']" style="font-size: 10px;" />
            </button>
          </div>
          <p class="feed-text">{{ c.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useTaskStore } from '../../stores/tasks'
import { useConfirm } from '../../composables/useConfirm'
import type { Comment } from '../../types'

const props = defineProps<{ taskId: number }>()
const emit = defineEmits<{ countChange: [number] }>()

const auth = useAuthStore()
const taskStore = useTaskStore()
const { confirm } = useConfirm()

const comments = ref<Comment[]>([])
const newComment = ref('')
const postingComment = ref(false)
const loading = ref(false)
const commentFocused = ref(false)

const GRADIENTS = [
  'linear-gradient(135deg, #6366F1, #8B5CF6)',
  'linear-gradient(135deg, #0EA5E9, #2563EB)',
  'linear-gradient(135deg, #10B981, #059669)',
  'linear-gradient(135deg, #F59E0B, #D97706)',
  'linear-gradient(135deg, #EF4444, #DC2626)',
  'linear-gradient(135deg, #0D9488, #0891B2)',
]

function memberGradient(name: string): string {
  let hash = 0
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) & 0xffffffff
  return GRADIENTS[Math.abs(hash) % GRADIENTS.length]
}

function timeAgo(d: string): string {
  const diff = Date.now() - new Date(d).getTime()
  const min = Math.floor(diff / 60000)
  if (min < 1) return 'just now'
  if (min < 60) return `${min}m ago`
  const hr = Math.floor(min / 60)
  if (hr < 24) return `${hr}h ago`
  const day = Math.floor(hr / 24)
  if (day < 7) return `${day}d ago`
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

watch(
  () => props.taskId,
  async (id) => {
    loading.value = true
    try {
      comments.value = await taskStore.fetchComments(id)
      emit('countChange', comments.value.length)
    } catch { /* noop */ } finally {
      loading.value = false
    }
  },
  { immediate: true }
)

async function addComment() {
  if (!newComment.value.trim()) return
  postingComment.value = true
  try {
    const c = await taskStore.createComment({ task_id: props.taskId, content: newComment.value.trim() })
    comments.value.push(c)
    newComment.value = ''
    emit('countChange', comments.value.length)
  } catch (e) {
    console.error(e)
  } finally {
    postingComment.value = false
  }
}

async function handleDeleteComment(id: number) {
  const ok = await confirm({
    title: 'Delete comment?',
    message: 'This comment will be permanently deleted.',
    confirmLabel: 'Delete comment',
    danger: true,
  })
  if (!ok) return
  await taskStore.deleteComment(id)
  comments.value = comments.value.filter((c) => c.id !== id)
  emit('countChange', comments.value.length)
}
</script>

<style scoped>
/* ── Comment compose ── */
.comment-compose {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.compose-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  flex-shrink: 0;
  margin-top: 2px;
  overflow: hidden;
}

.compose-field {
  flex: 1;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  overflow: hidden;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.compose-field--focused {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.compose-textarea {
  width: 100%;
  padding: 10px 12px 6px;
  border: none;
  background: transparent;
  font-size: 13.5px;
  font-family: inherit;
  color: var(--text);
  resize: none;
  display: block;
  line-height: 1.6;
}
.compose-textarea:focus { outline: none; }
.compose-textarea::placeholder { color: var(--text-light); }

.compose-actions {
  padding: 7px 10px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--border);
  background: var(--surface);
}

.btn-post {
  display: inline-flex;
  align-items: center;
  padding: 5px 14px;
  border-radius: 7px;
  font-size: 12.5px;
  font-weight: 700;
  font-family: inherit;
  background: var(--primary);
  color: #fff;
  border: none;
  cursor: pointer;
  transition: opacity 0.12s;
}
.btn-post:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-post:not(:disabled):hover { opacity: 0.88; }

/* ── Comments feed ── */
.feed-empty {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding: 20px 0;
}

.comments-feed {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feed-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.feed-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  flex-shrink: 0;
  overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.feed-body { flex: 1; min-width: 0; }

.feed-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.feed-author {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
}

.feed-time {
  font-size: 11.5px;
  color: var(--text-light);
  flex: 1;
}

.feed-delete {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-light);
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.12s, color 0.12s;
}
.feed-item:hover .feed-delete { opacity: 1; }
.feed-delete:hover { color: var(--danger, #EF4444); }

.feed-text {
  font-size: 13.5px;
  line-height: 1.6;
  color: var(--text);
  word-break: break-word;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
}

/* ── Dark mode ── */
:global([data-theme="dark"]) .compose-field { background: #1E2732; border-color: #38444D; }
:global([data-theme="dark"]) .compose-actions { background: #15202B; border-top-color: #38444D; }
:global([data-theme="dark"]) .feed-text { background: #15202B; border-color: #38444D; }
</style>
