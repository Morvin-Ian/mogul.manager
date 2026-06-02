<template>
    <div class="chat-view">
        <div class="chat-layout">

            <!-- Left panel: conversations -->
            <ChatConversations
                :conversations="chatStore.conversations"
                :loading="chatStore.loading"
                :streaming="chatStore.streaming"
                :current-id="chatStore.current?.id ?? null"
                @select="selectConversation"
                @new="handleNewConversation"
                @delete="handleDeleteConv"
                @clear="handleClearAll"
            />

            <!-- Main chat area -->
            <main class="chat-main" :class="{ 'has-conv': !!chatStore.current }">

                <!-- Active conversation -->
                <template v-if="chatStore.current">
                    <div class="chat-messages" ref="messagesRef" @scroll="onMessagesScroll">
                        <!-- Welcome / empty thread -->
                        <div
                            v-if="chatStore.current.messages.length === 0"
                            class="chat-welcome"
                        >
                            <div class="welcome-brand">
                                <span class="brand-word">mogul<span class="brand-dot">.</span></span>
                                <span class="brand-sub">manager</span>
                            </div>
                            <h1 class="welcome-title">How can I help you today?</h1>
                            <p class="welcome-sub">
                                Ask me anything about your workspaces, projects, or tasks.
                                I can act on your behalf — creating, updating, and analysing in real time.
                            </p>

                            <!-- Action cards -->
                            <div class="action-grid">
                                <button
                                    v-for="card in actionCards"
                                    :key="card.text"
                                    class="action-card"
                                    @click="quickSend(card.text)"
                                >
                                    <div class="action-icon" :style="{ background: card.bg }">
                                        <component :is="'span'" v-html="card.svg"></component>
                                    </div>
                                    <span class="action-label">{{ card.label }}</span>
                                    <span class="action-plus">
                                        <svg viewBox="0 0 12 12" fill="none" width="11" height="11">
                                            <path d="M6 1v10M1 6h10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
                                        </svg>
                                    </span>
                                </button>
                            </div>
                        </div>

                        <!-- Messages -->
                        <MessageBubble
                            v-for="(msg, i) in chatStore.current.messages"
                            :key="msg.id || msg.content"
                            :role="msg.role"
                            :content="msg.content"
                            :created-at="msg.created_at"
                            :grouped="i > 0 && chatStore.current.messages[i - 1].role === msg.role"
                        />

                        <!-- Thinking indicator -->
                        <Transition name="thinking-fade">
                            <div
                                v-if="chatStore.streaming && !chatStore.streamContent && !chatStore.toolActivity"
                                class="thinking-status"
                                :key="chatStore.thinkingStatus"
                            >
                                <span class="thinking-dots">
                                    <span class="thinking-dot"></span>
                                    <span class="thinking-dot"></span>
                                    <span class="thinking-dot"></span>
                                </span>
                                <span class="thinking-text">{{ chatStore.thinkingStatus }}</span>
                            </div>
                        </Transition>

                        <!-- Tool activity -->
                        <Transition name="thinking-fade">
                            <div v-if="chatStore.streaming && chatStore.toolActivity" class="tool-activity">
                                <span class="tool-activity-dot"></span>
                                Running {{ formatToolName(chatStore.toolActivity) }}…
                            </div>
                        </Transition>

                        <!-- Streaming bubble -->
                        <MessageBubble
                            v-if="chatStore.streaming && chatStore.streamContent"
                            role="assistant"
                            :content="chatStore.streamContent"
                            :streaming="true"
                        />
                    </div>

                    <!-- Scroll-to-bottom FAB -->
                    <Transition name="fab-fade">
                        <button v-if="showScrollBtn" class="scroll-fab" @click="scrollToBottom" title="Scroll to bottom">
                            <svg viewBox="0 0 16 16" fill="none" width="16" height="16">
                                <path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    </Transition>

                    <ChatInput
                        v-model="input"
                        :streaming="chatStore.streaming"
                        :placeholder="currentPlaceholder"
                        @send="handleSend"
                    />
                </template>

                <!-- No conversation selected -->
                <div v-else class="no-conv-state">
                    <div class="welcome-brand">
                        <span class="brand-word">mogul<span class="brand-dot">.</span></span>
                        <span class="brand-sub">manager</span>
                    </div>
                    <h1 class="welcome-title">How can I help you today?</h1>
                    <p class="welcome-sub">Select a conversation or start a new one.</p>
                    <div class="action-grid">
                        <button
                            v-for="card in actionCards"
                            :key="card.text"
                            class="action-card"
                            @click="startWithPrompt(card.text)"
                        >
                            <div class="action-icon" :style="{ background: card.bg }">
                                <component :is="'span'" v-html="card.svg"></component>
                            </div>
                            <span class="action-label">{{ card.label }}</span>
                            <span class="action-plus">
                                <svg viewBox="0 0 12 12" fill="none" width="11" height="11">
                                    <path d="M6 1v10M1 6h10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
                                </svg>
                            </span>
                        </button>
                    </div>
                </div>
            </main>

            <!-- Right panel: projects -->
            <aside class="projects-panel">
                <div class="proj-panel-head">
                    <span class="proj-panel-title">Projects</span>
                    <span class="proj-panel-count">({{ allProjects.length }})</span>
                </div>
                <div class="proj-panel-list">
                    <div v-if="projectsLoading" v-for="n in 6" :key="n" class="proj-sk-item">
                        <div class="sk-line sk-proj-title"></div>
                        <div class="sk-line sk-proj-sub"></div>
                    </div>
                    <div v-else-if="allProjects.length === 0" class="proj-panel-empty">
                        No projects yet
                    </div>
                    <div
                        v-else
                        v-for="p in allProjects"
                        :key="p.id"
                        class="proj-panel-item"
                        @click="quickSendProject(p.title)"
                    >
                        <div class="proj-panel-info">
                            <p class="proj-panel-name">{{ p.title }}</p>
                            <p class="proj-panel-desc">{{ p.description || p.status }}</p>
                        </div>
                        <span class="proj-panel-dot" :class="`dot-${p.status}`"></span>
                    </div>
                </div>
            </aside>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import { useChatStore } from "../stores/chat";
import { useConfirm } from "../composables/useConfirm";
import { useWorkspaceStore } from "../stores/workspaces";
import { get } from "../stores/client";
import type { Project } from "../types";
import MessageBubble from "../components/chat/MessageBubble.vue";
import ChatConversations from "../components/chat/ChatConversations.vue";
import ChatInput from "../components/chat/ChatInput.vue";

const chatStore = useChatStore();
const workspaceStore = useWorkspaceStore();
const { confirm } = useConfirm();

// ── Projects panel ───────────────────────────────────────────────
const allProjects = ref<Project[]>([]);
const projectsLoading = ref(false);

async function loadProjects() {
    projectsLoading.value = true;
    try {
        await workspaceStore.fetchAll();
        const wsIds = workspaceStore.workspaces.map((ws) => ws.id);
        if (!wsIds.length) return;
        const arrays = await Promise.all(wsIds.map((id) => get<Project[]>(`/projects?workspace_id=${id}`)));
        allProjects.value = arrays.flat().filter((p) => !p.is_archived);
    } catch {}
    finally { projectsLoading.value = false; }
}

function quickSendProject(title: string) {
    quickSend(`What is the status of the "${title}" project?`);
}

// ── Action cards ────────────────────────────────────────────────
const actionCards = [
    {
        label: "What's blocking my team?",
        text: "What is currently blocking my team's tasks?",
        bg: '#DBEAFE',
        svg: `<svg viewBox="0 0 20 20" fill="none" width="20" height="20"><circle cx="10" cy="10" r="7.5" stroke="#1E40AF" stroke-width="1.5"/><path d="M10 6v5M10 14v.5" stroke="#1E40AF" stroke-width="1.8" stroke-linecap="round"/></svg>`,
    },
    {
        label: "Summarize project progress",
        text: "Summarize the current progress across all my active projects.",
        bg: '#D1FAE5',
        svg: `<svg viewBox="0 0 20 20" fill="none" width="20" height="20"><path d="M3 14l4-5 4 3 4-6" stroke="#065F46" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M3 17h14" stroke="#065F46" stroke-width="1.3" stroke-linecap="round"/></svg>`,
    },
    {
        label: "Create tasks from a goal",
        text: "Help me break down a goal into actionable tasks.",
        bg: '#FEF3C7',
        svg: `<svg viewBox="0 0 20 20" fill="none" width="20" height="20"><rect x="3" y="3" width="14" height="14" rx="3" stroke="#92400E" stroke-width="1.5"/><path d="M7 10l2.5 2.5L13 7.5" stroke="#92400E" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    },
    {
        label: "Draft a team status update",
        text: "Draft a weekly status update summarising what my team has accomplished.",
        bg: '#FCE7F3',
        svg: `<svg viewBox="0 0 20 20" fill="none" width="20" height="20"><path d="M4 4h12v10H4z" stroke="#9D174D" stroke-width="1.5" stroke-linejoin="round"/><path d="M7 8h6M7 11h4" stroke="#9D174D" stroke-width="1.3" stroke-linecap="round"/><path d="M12.5 14.5l2 2.5" stroke="#9D174D" stroke-width="1.3" stroke-linecap="round"/></svg>`,
    },
]

// ── State ────────────────────────────────────────────────────────
const input = ref("");
const messagesRef = ref<HTMLElement | null>(null);
const showScrollBtn = ref(false);

function onMessagesScroll() {
    const el = messagesRef.value;
    if (!el) return;
    showScrollBtn.value = el.scrollHeight - el.scrollTop - el.clientHeight > 80;
}

// ── Rotating placeholder ─────────────────────────────────────────
const placeholders = [
    "Ask me anything…",
    'Try: "What projects need attention?"',
    'Try: "Who has the most tasks right now?"',
    'Try: "Move all overdue tasks to In Revision"',
    'Try: "Show me everything due this week"',
];
const placeholderIndex = ref(0);
const currentPlaceholder = computed(() => placeholders[placeholderIndex.value]);
let placeholderTimer: ReturnType<typeof setInterval> | null = null;

// ── Pending message handler ──────────────────────────────────────
async function dispatchPendingMessage(msg: string) {
    chatStore.pendingMessage = null;
    if (!chatStore.current) {
        if (chatStore.conversations.length) {
            await chatStore.fetchConversation(chatStore.conversations[0].id);
        } else {
            const conv = await chatStore.createConversation();
            await chatStore.fetchConversation(conv.id);
        }
    }
    if (chatStore.current) {
        await chatStore.sendMessage(chatStore.current.id, msg);
    }
}

onMounted(async () => {
    await chatStore.fetchConversations();
    loadProjects();
    placeholderTimer = setInterval(() => {
        if (!input.value) {
            placeholderIndex.value = (placeholderIndex.value + 1) % placeholders.length;
        }
    }, 3500);
    await nextTick();
    messagesRef.value?.addEventListener("scroll", onMessagesScroll, { passive: true });
    if (chatStore.pendingMessage) {
        await dispatchPendingMessage(chatStore.pendingMessage);
    }
});

watch(() => chatStore.pendingMessage, async (msg) => {
    if (msg) await dispatchPendingMessage(msg);
});

onUnmounted(() => {
    if (placeholderTimer) clearInterval(placeholderTimer);
    messagesRef.value?.removeEventListener("scroll", onMessagesScroll);
});

watch(() => chatStore.current?.messages.length, async () => {
    await nextTick();
    scrollToBottom();
});
watch(() => chatStore.streamContent, async () => {
    await nextTick();
    scrollToBottom();
});

function scrollToBottom() {
    if (messagesRef.value)
        messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
}

// ── Handlers ─────────────────────────────────────────────────────
async function selectConversation(id: number) {
    try { await chatStore.fetchConversation(id); } catch {}
}

async function handleNewConversation() {
    try {
        const conv = await chatStore.createConversation();
        await chatStore.fetchConversation(conv.id);
    } catch {}
}

async function handleDeleteConv(id: number) {
    try { await chatStore.removeConversation(id); } catch {}
}

async function handleClearAll() {
    const count = chatStore.conversations.length;
    const ok = await confirm({
        title: "Clear all conversations?",
        message: `All ${count} conversation${count !== 1 ? "s" : ""} will be permanently deleted.`,
        consequences: ["Chat history cannot be recovered after deletion"],
        confirmLabel: "Yes, clear all",
        cancelLabel: "Cancel",
        danger: true,
    });
    if (!ok) return;
    for (const id of chatStore.conversations.map((c) => c.id)) {
        try { await chatStore.removeConversation(id); } catch {}
    }
}

async function handleSend(text: string) {
    if (!text.trim() || chatStore.streaming || !chatStore.current) return;
    input.value = "";
    await chatStore.sendMessage(chatStore.current.id, text.trim());
}

async function quickSend(text: string) {
    if (chatStore.streaming || !chatStore.current) return;
    await chatStore.sendMessage(chatStore.current.id, text);
}

async function startWithPrompt(text: string) {
    if (!chatStore.current && chatStore.conversations.length) {
        await chatStore.fetchConversation(chatStore.conversations[0].id);
    } else if (!chatStore.current) {
        const conv = await chatStore.createConversation();
        await chatStore.fetchConversation(conv.id);
    }
    if (chatStore.current) {
        await chatStore.sendMessage(chatStore.current.id, text);
    }
}

function formatToolName(name: string) {
    return name.replace(/_/g, " ");
}
</script>

<style scoped>
.chat-view {
    height: calc(100vh - 58px);
    display: flex;
    flex-direction: column;
    padding: 0;
}

.chat-layout {
    display: flex;
    height: 100%;
    overflow: hidden;
}

/* ── Main chat area ── */
.chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    background: var(--bg);
    position: relative;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 32px 28px 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-width: 780px;
    width: 100%;
    margin: 0 auto;
}

/* ── Welcome screen ── */
.chat-welcome,
.no-conv-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 56px 16px 32px;
    gap: 0;
    text-align: center;
}

.welcome-brand {
    display: flex;
    align-items: baseline;
    gap: 3px;
    margin-bottom: 28px;
}
.brand-word {
    font-size: 22px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.8px;
}
.brand-dot { color: var(--primary); }
.brand-sub {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
    letter-spacing: 0.2px;
}

.welcome-title {
    font-size: 34px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -1px;
    line-height: 1.15;
    margin-bottom: 14px;
}

.welcome-sub {
    font-size: 14.5px;
    color: var(--text-muted);
    line-height: 1.6;
    max-width: 480px;
    margin-bottom: 40px;
}

/* ── Action cards (2×2 grid) ── */
.action-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    width: 100%;
    max-width: 580px;
    text-align: left;
}

.action-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    cursor: pointer;
    font-family: inherit;
    text-align: left;
    transition: border-color 0.14s, box-shadow 0.14s, transform 0.1s;
    box-shadow: 0 1px 4px rgba(10,11,13,0.05);
}
.action-card:hover {
    border-color: var(--border-strong);
    box-shadow: 0 4px 16px rgba(10,11,13,0.1);
    transform: translateY(-1px);
}

.action-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.action-label {
    flex: 1;
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    line-height: 1.35;
    letter-spacing: -0.1px;
}

.action-plus {
    flex-shrink: 0;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background: #1c1c1e;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    transition: opacity 0.12s;
}
.action-card:hover .action-plus { opacity: 0.8; }
:global([data-theme="dark"]) .action-plus { background: #F7F9F9; color: #1c1c1e; }

/* ── Thinking & tool activity ── */
.thinking-status {
    align-self: flex-start;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    color: var(--text-muted);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 7px 12px;
}
.thinking-dots { display: flex; align-items: center; gap: 3px; flex-shrink: 0; }
.thinking-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--text-muted);
    animation: dot-bounce 1.2s ease-in-out infinite;
}
.thinking-dots .thinking-dot:nth-child(2) { animation-delay: 0.15s; }
.thinking-dots .thinking-dot:nth-child(3) { animation-delay: 0.3s; }
@keyframes dot-bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.45; }
    30%            { transform: translateY(-4px); opacity: 1; }
}

.tool-activity {
    align-self: flex-start;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    color: var(--text-muted);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 7px 12px;
}
.tool-activity-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #00BA7C;
    animation: pulse 1s ease-in-out infinite;
    flex-shrink: 0;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.75)} }

/* Transitions */
.thinking-fade-enter-active, .thinking-fade-leave-active {
    transition: opacity 0.25s ease, transform 0.25s ease;
}
.thinking-fade-enter-from, .thinking-fade-leave-to {
    opacity: 0; transform: translateY(4px);
}

/* Scroll FAB */
.scroll-fab {
    position: absolute;
    bottom: 100px;
    left: 50%;
    transform: translateX(-50%);
    width: 34px; height: 34px;
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    color: var(--text-muted);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: background 0.15s, box-shadow 0.15s;
    z-index: 10;
}
.scroll-fab:hover { background: var(--bg); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
.fab-fade-enter-active, .fab-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.fab-fade-enter-from, .fab-fade-leave-to { opacity: 0; transform: translateX(-50%) translateY(6px); }

/* ── Projects panel (right) ── */
.projects-panel {
    width: 268px;
    flex-shrink: 0;
    border-left: 1px solid var(--border);
    background: var(--surface);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.proj-panel-head {
    display: flex;
    align-items: baseline;
    gap: 5px;
    padding: 18px 16px 14px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
}
.proj-panel-title {
    font-size: 13.5px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.2px;
}
.proj-panel-count {
    font-size: 12.5px;
    color: var(--text-muted);
    font-weight: 500;
}
.proj-panel-list {
    flex: 1;
    overflow-y: auto;
    padding: 6px 8px;
}
.proj-panel-list::-webkit-scrollbar { width: 4px; }
.proj-panel-list::-webkit-scrollbar-track { background: transparent; }
.proj-panel-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
.proj-panel-empty {
    font-size: 13px;
    color: var(--text-light);
    text-align: center;
    padding: 32px 16px;
}
.proj-panel-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 10px;
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.1s;
    margin-bottom: 1px;
}
.proj-panel-item:hover { background: var(--bg); }
.proj-panel-info { flex: 1; min-width: 0; }
.proj-panel-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
}
.proj-panel-desc {
    font-size: 11.5px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-transform: capitalize;
}
.proj-panel-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-active    { background: #00BA7C; }
.dot-planning  { background: #94A3B8; }
.dot-on_hold   { background: #F59E0B; }
.dot-completed { background: #3B82F6; }
.dot-archived  { background: #CBD5E1; }

/* Skeleton */
.proj-sk-item {
    padding: 10px;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 2px;
}
@keyframes shimmer {
    0%   { background-position: -300px 0; }
    100% { background-position:  300px 0; }
}
.sk-line {
    background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
    background-size: 300px 100%;
    animation: shimmer 1.4s ease-in-out infinite;
    border-radius: 4px;
}
.sk-proj-title { height: 12px; width: 75%; }
.sk-proj-sub   { height: 10px; width: 50%; }

@media (max-width: 768px) {
    .action-grid { grid-template-columns: 1fr; }
    .welcome-title { font-size: 26px; }
    .projects-panel { display: none; }
}
</style>
