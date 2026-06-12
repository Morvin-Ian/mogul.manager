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
      <div v-for="c in topLevelComments" :key="c.id" class="feed-item" :id="`comment-${c.id}`">
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

          <!-- Footer row: reply + expand toggle -->
          <div class="comment-footer-row">
            <button class="comment-reply-btn" @click="startReply(c.id)">
              <font-awesome-icon :icon="['fas', 'reply']" style="font-size:10px;" />
              Reply
            </button>
            <button
              v-if="repliesFor(c.id).length > 0"
              class="comment-expand-btn"
              @click="toggleReplies(c.id)"
            >
              <font-awesome-icon
                :icon="['fas', 'chevron-down']"
                class="expand-chevron"
                :class="{ 'expand-chevron-open': expandedReplies.has(c.id) }"
              />
              {{ repliesFor(c.id).length }} {{ repliesFor(c.id).length === 1 ? 'reply' : 'replies' }}
            </button>
          </div>

          <!-- Inline reply form -->
          <div v-if="replyingToId === c.id" class="reply-form">
            <div class="reply-avatar" :style="auth.user?.profile_path ? {} : { background: memberGradient(auth.user?.username || 'U') }">
              <img v-if="auth.user?.profile_path" :src="auth.user.profile_path" class="comment-avatar-img" />
              <font-awesome-icon v-else :icon="['fas', 'user']" style="font-size:11px;color:#fff;" />
            </div>
            <div class="reply-input-wrap">
              <input
                v-model="replyContent"
                class="reply-input"
                :placeholder="`Reply to ${c.user?.username ?? 'comment'}...`"
                @keydown.enter.prevent="submitReply(c.id)"
                @keydown.escape="replyingToId = null"
              />
              <div class="reply-form-actions">
                <button class="btn-comment-save" @click="submitReply(c.id)" :disabled="!replyContent.trim()">Send</button>
                <button class="btn-comment-cancel" @click="replyingToId = null">Cancel</button>
              </div>
            </div>
          </div>

          <!-- Threaded replies -->
          <div v-if="expandedReplies.has(c.id) && repliesFor(c.id).length > 0" class="replies-thread">
            <div v-for="r in repliesFor(c.id)" :key="r.id" class="reply-card">
              <div class="reply-line" />
              <div class="reply-body">
                <div class="feed-meta">
                  <div class="reply-avatar" :style="r.user?.profile_path ? {} : { background: memberGradient(r.user?.username || 'U') }">
                    <img v-if="r.user?.profile_path" :src="r.user.profile_path" class="comment-avatar-img" :alt="r.user?.username" />
                    <font-awesome-icon v-else :icon="['fas', 'user']" style="font-size:11px;color:#fff;" />
                  </div>
                  <span class="feed-author">{{ r.user?.username ?? 'Team Member' }}</span>
                  <span class="feed-time">{{ timeAgo(r.created_at) }}</span>
                  <button
                    v-if="r.user_id === auth.user?.id"
                    class="feed-delete"
                    @click="handleDeleteComment(r.id)"
                    title="Delete reply"
                  >
                    <font-awesome-icon :icon="['fas', 'trash']" style="font-size: 10px;" />
                  </button>
                </div>
                <p class="reply-text">{{ r.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useCommentStore } from '../../stores/comments'
import { useConfirm } from '../../composables/useConfirm'
import { useToast } from '../../composables/useToast'
import type { Comment } from '../../types'

const props = defineProps<{ taskId: number; highlightCommentId?: number | null }>()
const emit = defineEmits<{ countChange: [number] }>()

const auth = useAuthStore()
const commentStore = useCommentStore()
const { confirm } = useConfirm()
const toast = useToast()

const newComment = ref('')
const postingComment = ref(false)
const loading = ref(false)
const commentFocused = ref(false)
const replyingToId = ref<number | null>(null)
const replyContent = ref('')
const expandedReplies = ref<Set<number>>(new Set())

// Derive comments from the shared store so replies made from the homepage
// dashboard are immediately visible in the task drawer.
const comments = computed(() => commentStore.all.filter(c => c.task_id === props.taskId))
const topLevelComments = computed(() => comments.value.filter(c => !c.parent_id))
function repliesFor(parentId: number): Comment[] {
  return comments.value.filter(c => c.parent_id === parentId)
}

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

// Watch both taskId AND commentStore.all so new comments (e.g. from the
// dashboard) are reflected without a manual refetch.
watch(
  () => props.taskId,
  async (id) => {
    loading.value = true
    try {
      await commentStore.fetchForTask(id)
      emit('countChange', comments.value.length)
    } catch { /* noop */ } finally {
      loading.value = false
    }
  },
  { immediate: true }
)

// When comments arrive from another source (homepage reply) update the badge
// and scroll to the highlighted comment if one was requested via URL.
watch(
  () => comments.value.length,
  async (n) => {
    emit('countChange', n)
    if (props.highlightCommentId) {
      await nextTick()
      const el = document.getElementById(`comment-${props.highlightCommentId}`)
      el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  },
)

async function addComment() {
  if (!newComment.value.trim()) return
  postingComment.value = true
  try {
    await commentStore.create({ task_id: props.taskId, content: newComment.value.trim() })
    newComment.value = ''
    emit('countChange', comments.value.length)
  } catch (e: any) {
    toast.error(e?.message || 'Failed to post comment')
  } finally {
    postingComment.value = false
  }
}

function startReply(commentId: number) {
  replyingToId.value = replyingToId.value === commentId ? null : commentId
  replyContent.value = ''
}

function toggleReplies(commentId: number) {
  const next = new Set(expandedReplies.value)
  if (next.has(commentId)) next.delete(commentId)
  else next.add(commentId)
  expandedReplies.value = next
}

async function submitReply(parentId: number) {
  const content = replyContent.value.trim()
  if (!content) return
  try {
    await commentStore.create({ task_id: props.taskId, content, parent_id: parentId })
    replyContent.value = ''
    replyingToId.value = null
    expandedReplies.value = new Set([...expandedReplies.value, parentId])
    emit('countChange', comments.value.length)
  } catch (e: any) {
    toast.error(e?.message || 'Failed to post reply')
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
  try {
    await commentStore.remove(id)
    emit('countChange', comments.value.length)
  } catch (e: any) {
    toast.error(e?.message || 'Failed to delete comment')
  }
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

/* ── Footer row ── */
.comment-footer-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 2px;
}

.comment-reply-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 11px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  background: none;
  cursor: pointer;
  transition: all 0.12s;
}
.comment-reply-btn:hover {
  background: var(--bg);
  color: var(--text);
  border-color: var(--border-strong);
}

.comment-expand-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 11px;
  border: 1.5px solid var(--primary-border);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  background: var(--primary-muted);
  cursor: pointer;
  transition: all 0.12s;
}
.comment-expand-btn:hover { opacity: 0.8; }

.expand-chevron {
  font-size: 10px;
  transition: transform 0.2s;
}
.expand-chevron-open { transform: rotate(180deg); }

/* ── Inline reply form ── */
.reply-form {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 10px 0 2px;
  border-top: 1.5px solid var(--border);
  margin-top: 6px;
}

.reply-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  font-size: 11px;
  font-weight: 800;
  color: #fff;
}

.reply-input-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.reply-input {
  width: 100%;
  padding: 7px 11px;
  border: 1.5px solid var(--border);
  border-radius: 9px;
  font-size: 13px;
  font-family: inherit;
  color: var(--text);
  background: var(--bg);
  outline: none;
  transition: border-color 0.14s;
}
.reply-input:focus { border-color: var(--primary); background: #fff; box-shadow: 0 0 0 3px var(--primary-muted); }
.reply-input::placeholder { color: var(--text-light); }

.reply-form-actions {
  display: flex;
  gap: 6px;
}

.btn-comment-save {
  padding: 6px 14px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.14s;
}
.btn-comment-save:hover { opacity: 0.8; }

.btn-comment-cancel {
  padding: 6px 14px;
  background: transparent;
  color: var(--text-muted);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.btn-comment-cancel:hover { background: var(--bg); color: var(--text); }

/* ── Threaded replies ── */
.replies-thread {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 6px;
}

.reply-card {
  display: flex;
  gap: 0;
  padding-left: 16px;
  position: relative;
}

.reply-line {
  position: absolute;
  left: 16px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border);
  border-radius: 2px;
}

.reply-body {
  flex: 1;
  margin-left: 14px;
  background: var(--bg);
  border-radius: 12px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.reply-body .feed-meta { margin-bottom: 0; }

.reply-text {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text);
  word-break: break-word;
}

.comment-avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

/* ── Dark mode ── */
:global([data-theme="dark"]) .compose-field { background: #1E2732; border-color: #38444D; }
:global([data-theme="dark"]) .compose-actions { background: #15202B; border-top-color: #38444D; }
:global([data-theme="dark"]) .feed-text { background: #15202B; border-color: #38444D; }
</style>
