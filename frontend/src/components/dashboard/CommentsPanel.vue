<template>
  <div class="panel">
    <div class="panel-hdr">
      <span class="panel-title">Comments</span>
      <span class="comments-count-badge" v-if="topLevelComments.length">{{ topLevelComments.length }}</span>
    </div>

    <div v-if="topLevelComments.length === 0" class="comments-empty">
      <svg viewBox="0 0 40 40" fill="none" width="36" height="36">
        <path d="M36 20c0 8.837-7.163 16-16 16a15.93 15.93 0 01-7.4-1.8L4 36l1.8-8.6A15.93 15.93 0 014 20C4 11.163 11.163 4 20 4s16 7.163 16 16z" stroke="#D1D5DB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <p>No comments yet</p>
    </div>

    <div v-else class="comments-list">
      <div v-for="c in topLevelComments" :key="c.id" class="comment-card">
        <!-- Header -->
        <div class="comment-card-hdr">
          <div class="comment-avatar" :style="c.user?.profile_path ? {} : { background: commentColor(c.user_id) }">
            <img v-if="c.user?.profile_path" :src="c.user.profile_path" class="comment-avatar-img" :alt="c.user?.username" />
            <font-awesome-icon v-else :icon="['fas', 'user']" style="font-size:14px;color:#fff;" />
          </div>
          <div class="comment-card-author">
            <span class="comment-author-name">
              {{ c.user?.username ?? (c.user_id === auth.user?.id ? auth.user?.username : 'Team Member') }}
            </span>
            <button class="comment-task-label comment-task-link" @click="goToComment(c.task_id, c.id)" :title="`Open ${taskTitleFor(c.task_id)}`">
              {{ taskTitleFor(c.task_id) }}
            </button>
          </div>
          <span class="comment-time">{{ timeAgo(c.created_at) }}</span>
        </div>

        <!-- Content or inline editor -->
        <div v-if="editingCommentId === c.id" class="comment-edit-wrap">
          <textarea
            v-model="editingContent"
            class="comment-edit-input"
            rows="2"
            @keydown.enter.ctrl.prevent="saveEdit(c.id)"
          />
          <div class="comment-edit-actions">
            <button class="btn-comment-save" @click="saveEdit(c.id)">Save</button>
            <button class="btn-comment-cancel" @click="editingCommentId = null">Cancel</button>
          </div>
        </div>
        <p v-else class="comment-content comment-content--link" @click="goToComment(c.task_id, c.id)">{{ c.content }}</p>

        <!-- Footer row: reply + expand toggle + owner actions -->
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
          <div class="comment-owner-actions" v-if="c.user_id === auth.user?.id">
            <button class="comment-action-btn" @click="startEdit(c)">Edit</button>
            <button class="comment-action-btn danger" @click="deleteComment(c.id)">Delete</button>
          </div>
        </div>

        <!-- Inline reply form -->
        <div v-if="replyingToId === c.id" class="reply-form">
          <div class="reply-avatar" :style="auth.user?.profile_path ? {} : { background: commentColor(auth.user?.id ?? 0) }">
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
          <div v-for="reply in repliesFor(c.id)" :key="reply.id" class="reply-card">
            <div class="reply-line" />
            <div class="reply-body">
              <div class="comment-card-hdr">
                <div class="comment-avatar comment-avatar-sm" :style="reply.user?.profile_path ? {} : { background: commentColor(reply.user_id) }">
                  <img v-if="reply.user?.profile_path" :src="reply.user.profile_path" class="comment-avatar-img" :alt="reply.user?.username" />
                  <font-awesome-icon v-else :icon="['fas', 'user']" style="font-size:11px;color:#fff;" />
                </div>
                <div class="comment-card-author">
                  <span class="comment-author-name">
                    {{ reply.user?.username ?? (reply.user_id === auth.user?.id ? auth.user?.username : 'Team Member') }}
                  </span>
                </div>
                <span class="comment-time">{{ timeAgo(reply.created_at) }}</span>
              </div>
              <div v-if="editingCommentId === reply.id" class="comment-edit-wrap">
                <textarea v-model="editingContent" class="comment-edit-input" rows="2" @keydown.enter.ctrl.prevent="saveEdit(reply.id)" />
                <div class="comment-edit-actions">
                  <button class="btn-comment-save" @click="saveEdit(reply.id)">Save</button>
                  <button class="btn-comment-cancel" @click="editingCommentId = null">Cancel</button>
                </div>
              </div>
              <p v-else class="comment-content">{{ reply.content }}</p>
              <div v-if="reply.user_id === auth.user?.id" class="comment-footer-row">
                <button class="comment-action-btn" @click="startEdit(reply)">Edit</button>
                <button class="comment-action-btn danger" @click="deleteComment(reply.id)">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add comment -->
    <div class="comment-form">
      <select v-model="newCommentTaskId" class="comment-task-select">
        <option :value="null" disabled>Pick a task...</option>
        <option v-for="t in tasks.slice(0, 12)" :key="t.id" :value="t.id">{{ t.title }}</option>
      </select>
      <div class="comment-input-row">
        <input
          v-model="newCommentContent"
          class="comment-input"
          placeholder="Write a comment..."
          @keydown.enter.prevent="submitComment"
        />
        <button
          class="comment-submit"
          @click="submitComment"
          :disabled="!newCommentContent.trim() || !newCommentTaskId"
        >
          <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCommentStore } from '../../stores/comments'
import { useAuthStore } from '../../stores/auth'
import { timeAgo } from '../../utils/time'
import type { Task } from '../../types'

const props = defineProps<{ tasks: Task[] }>()
const emit = defineEmits<{ 'comment-updated': [taskId: number, delta: number] }>()

const commentStore = useCommentStore()
const auth = useAuthStore()
const router = useRouter()

// Open the comment's task on the project detail page, comments tab active
function goToComment(taskId: number, commentId?: number) {
  const task = props.tasks.find(t => t.id === taskId)
  if (!task?.project_uuid) return
  let path = `/projects/${task.project_uuid}?task=${task.uuid}&tab=comments`
  if (commentId) path += `&commentId=${commentId}`
  router.push(path)
}

const newCommentContent = ref('')
const newCommentTaskId = ref<number | null>(null)
const editingCommentId = ref<number | null>(null)
const editingContent = ref('')
const replyingToId = ref<number | null>(null)
const replyContent = ref('')
const expandedReplies = ref<Set<number>>(new Set())

const completedTaskIds = computed(() =>
  new Set(props.tasks.filter(t => t.status === 'completed').map(t => t.id))
)

const topLevelComments = computed(() =>
  [...commentStore.all]
    .filter(c => c.parent_id === null && !completedTaskIds.value.has(c.task_id))
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 8)
)

function repliesFor(parentId: number) {
  return commentStore.all
    .filter(c => c.parent_id === parentId)
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
}

function taskTitleFor(taskId: number): string {
  return props.tasks.find(t => t.id === taskId)?.title ?? 'Unknown task'
}

const COMMENT_COLORS = ['#F59E0B','#3B82F6','#10B981','#6366F1','#0D9488','#EF4444','#F97316']
function commentColor(userId: number): string {
  return COMMENT_COLORS[userId % COMMENT_COLORS.length]
}

async function submitComment() {
  const content = newCommentContent.value.trim()
  if (!content || !newCommentTaskId.value) return
  await commentStore.create({ task_id: newCommentTaskId.value, content })
  newCommentContent.value = ''
  emit('comment-updated', newCommentTaskId.value, 1)
}

async function submitReply(parentId: number) {
  const content = replyContent.value.trim()
  if (!content) return
  const parent = commentStore.all.find(c => c.id === parentId)
  if (!parent) return
  await commentStore.create({ task_id: parent.task_id, content, parent_id: parentId })
  replyContent.value = ''
  replyingToId.value = null
  expandedReplies.value = new Set([...expandedReplies.value, parentId])
  emit('comment-updated', parent.task_id, 1)
}

async function deleteComment(id: number) {
  const c = commentStore.all.find(c => c.id === id)
  await commentStore.remove(id)
  if (c) emit('comment-updated', c.task_id, -1)
}

function startEdit(c: { id: number; content: string }) {
  editingCommentId.value = c.id
  editingContent.value = c.content
}

async function saveEdit(id: number) {
  const content = editingContent.value.trim()
  if (!content) return
  await commentStore.update(id, content)
  editingCommentId.value = null
  editingContent.value = ''
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
</script>

<style scoped>
/* ── Comments Panel ─────────────────── */
.comments-count-badge {
  background: #1c1c1e;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  border-radius: 999px;
  padding: 2px 8px;
  line-height: 1.4;
}

.comments-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 28px 0;
  color: var(--text-muted);
  font-size: 14px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  max-height: 320px;
  padding-right: 2px;
}

/* ── Comment card ── */
.comment-card {
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 14px 16px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: box-shadow 0.14s;
}
.comment-card:hover {
  box-shadow: 0 4px 16px rgba(10,11,13,0.07);
}

.comment-avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.comment-card-hdr {
  display: flex;
  align-items: center;
  gap: 10px;
}

.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.comment-card-author {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.comment-author-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}

.comment-task-label {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.comment-task-link {
  background: none;
  border: none;
  padding: 0;
  font-family: inherit;
  text-align: left;
  cursor: pointer;
  transition: color 0.12s;
}
.comment-task-link:hover {
  color: var(--primary);
  text-decoration: underline;
}

.comment-content--link { cursor: pointer; }
.comment-content--link:hover { color: var(--text); }

.comment-time {
  font-size: 11.5px;
  color: var(--text-light);
  flex-shrink: 0;
  align-self: flex-start;
}

.comment-content {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── Inline edit ── */
.comment-edit-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-edit-input {
  width: 100%;
  padding: 9px 12px;
  border: 1.5px solid var(--primary);
  border-radius: 10px;
  font-size: 14px;
  font-family: inherit;
  color: var(--text);
  background: #fff;
  resize: none;
  outline: none;
  line-height: 1.5;
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.comment-edit-actions {
  display: flex;
  gap: 8px;
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

/* ── Footer row ── */
.comment-footer-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
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

.comment-owner-actions {
  display: flex;
  gap: 6px;
  margin-left: auto;
}

/* ── Inline reply form ── */
.reply-form {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 10px 0 2px;
  border-top: 1.5px solid var(--border);
  margin-top: 2px;
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

/* ── Threaded replies ── */
.replies-thread {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 4px;
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

.comment-avatar-sm {
  width: 28px !important;
  height: 28px !important;
  font-size: 11px !important;
}

.comment-action-btn {
  background: none;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  padding: 5px 13px;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.12s;
}
.comment-action-btn:hover {
  background: var(--bg);
  color: var(--text);
  border-color: var(--border-strong);
}
.comment-action-btn.danger:hover {
  background: #FEF2F2;
  color: #EF4444;
  border-color: #FECACA;
}

/* ── Comment form ────────────────────── */
.comment-form {
  margin-top: 14px;
  border-top: 1.5px solid var(--border);
  padding-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-task-select {
  width: 100%;
  padding: 8px 12px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 13px;
  font-family: inherit;
  color: var(--text);
  background: var(--bg);
  appearance: none;
  cursor: pointer;
  outline: none;
}
.comment-task-select:focus { border-color: var(--border-strong); }

.comment-input-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.comment-input {
  flex: 1;
  padding: 9px 13px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 13px;
  font-family: inherit;
  background: var(--bg);
  color: var(--text);
  outline: none;
  transition: border-color 0.14s;
}
.comment-input:focus { border-color: var(--border-strong); background: #fff; }
.comment-input::placeholder { color: var(--text-light); }

.comment-submit {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #1c1c1e;
  border: none;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: opacity 0.14s;
}
.comment-submit:disabled { opacity: 0.35; cursor: not-allowed; }
.comment-submit:not(:disabled):hover { opacity: 0.8; }
</style>
