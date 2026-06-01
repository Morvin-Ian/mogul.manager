<template>
    <aside class="sidebar">
        <nav class="sidebar-nav">
            <router-link
                to="/"
                exact-active-class="active"
                class="nav-item"
                title="Home"
            >
                <span class="icon-wrap">
                    <font-awesome-icon :icon="['fas', 'house']" />
                </span>
                <span class="nav-label">Home</span>
            </router-link>

            <router-link
                to="/workspaces"
                active-class="active"
                class="nav-item"
                title="Workspaces"
            >
                <span class="icon-wrap">
                    <font-awesome-icon :icon="['fas', 'layer-group']" />
                </span>
                <span class="nav-label">Spaces</span>
            </router-link>

            <router-link
                to="/team"
                active-class="active"
                class="nav-item"
                title="Team"
            >
                <span class="icon-wrap">
                    <font-awesome-icon :icon="['fas', 'users']" />
                </span>
                <span class="nav-label">Team</span>
            </router-link>

            <router-link
                to="/plans"
                active-class="active"
                class="nav-item"
                title="Plans"
            >
                <span class="icon-wrap">
                    <font-awesome-icon :icon="['fas', 'list-check']" />
                </span>
                <span class="nav-label">Plans</span>
            </router-link>

            <router-link
                to="/chat"
                active-class="active"
                class="nav-item nav-item--ai"
                title="AI Chat — ask me anything"
                @click="dismissAiBadge"
            >
                <span class="icon-wrap">
                    <font-awesome-icon :icon="['fas', 'wand-magic-sparkles']" />
                    <span v-if="showAiBadge" class="ai-badge-dot" />
                </span>
                <span class="nav-label">AI Chat</span>
            </router-link>

            <router-link
                to="/documents"
                active-class="active"
                class="nav-item"
                title="Documents"
            >
                <span class="icon-wrap">
                    <font-awesome-icon :icon="['fas', 'file-lines']" />
                </span>
                <span class="nav-label">Docs</span>
            </router-link>
        </nav>

        <div class="sidebar-footer">
            <button
                class="theme-toggle-btn"
                @click="toggle"
                :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
            >
                <span class="toggle-track" :class="{ 'is-dark': isDark }">
                    <span class="toggle-thumb">
                        <font-awesome-icon
                            :icon="['fas', isDark ? 'moon' : 'sun']"
                            class="toggle-icon"
                        />
                    </span>
                </span>
            </button>

            <button
                class="nav-item logout-btn"
                @click="handleLogout"
                title="Sign out"
            >
                <span class="icon-wrap">
                    <font-awesome-icon :icon="['fas', 'right-from-bracket']" />
                </span>
                <span class="nav-label">Sign Out</span>
            </button>
        </div>
    </aside>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "../../stores/auth";
import { useTheme } from "../../composables/useTheme";

import { ref } from 'vue'
const router = useRouter();
const auth = useAuthStore();
const { isDark, toggle } = useTheme();

// Show pulsing badge until user clicks AI Chat
const showAiBadge = ref(localStorage.getItem('ai_chat_visited') !== '1')
function dismissAiBadge() {
  showAiBadge.value = false
  localStorage.setItem('ai_chat_visited', '1')
}

function handleLogout() {
    auth.logout();
    router.push("/login");
}
</script>

<style scoped>
.sidebar {
    width: 88px;
    background: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-right: 1px solid rgba(180, 180, 185, 0.4);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    padding: 16px 0 12px;
}

.sidebar-nav {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 0 10px;
    flex: 1;
}

.sidebar-footer {
    padding: 10px 10px 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
}

.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    padding: 10px 8px;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    text-decoration: none;
    width: 100%;
    transition: color 0.14s;
    cursor: pointer;
    background: none;
    border: none;
    font-family: inherit;
}

.nav-item:hover {
    color: var(--text);
    text-decoration: none;
}
.nav-item:hover .icon-wrap {
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 3px 12px rgba(10, 11, 13, 0.14);
}

.nav-item.active {
    color: var(--text);
}
.nav-item.active .icon-wrap {
    background: #1c1c1e;
    color: #ffffff;
    box-shadow: 0 4px 14px rgba(10, 11, 13, 0.22);
}

.logout-btn:hover .icon-wrap {
    background: #ffe5e5;
    color: #c04040;
    box-shadow: 0 3px 12px rgba(192, 64, 64, 0.15);
}

.theme-toggle-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 8px 0;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
}

.toggle-track {
    width: 46px;
    height: 26px;
    border-radius: 13px;
    background: #d8d8dc;
    position: relative;
    transition: background 0.28s ease;
    display: flex;
    align-items: center;
    flex-shrink: 0;
}

.toggle-track.is-dark {
    background: #1c1c1e;
}

.toggle-thumb {
    position: absolute;
    left: 3px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    transition:
        left 0.28s cubic-bezier(0.34, 1.56, 0.64, 1),
        box-shadow 0.2s;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.22);
}

.toggle-track.is-dark .toggle-thumb {
    left: 23px;
}

.toggle-icon {
    font-size: 10px;
    color: #1c1c1e;
    transition: color 0.2s;
}

.toggle-track.is-dark .toggle-icon {
    color: #1c1c1e;
}

/* ── Dark mode sidebar ── */
:global([data-theme="dark"]) .sidebar {
    background: rgba(21, 32, 43, 0.92);
    border-right-color: rgba(56, 68, 77, 0.5);
}

:global([data-theme="dark"]) .icon-wrap {
    background: rgba(255, 255, 255, 0.07);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

:global([data-theme="dark"]) .nav-item:hover .icon-wrap {
    background: rgba(255, 255, 255, 0.14);
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.35);
}

:global([data-theme="dark"]) .nav-item.active .icon-wrap {
    background: #f7f9f9;
    color: #15202b;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
}

:global([data-theme="dark"]) .nav-item {
    color: #8b98a5;
}
:global([data-theme="dark"]) .nav-item:hover {
    color: #f7f9f9;
}
:global([data-theme="dark"]) .nav-item.active {
    color: #f7f9f9;
}

:global([data-theme="dark"]) .logout-btn:hover .icon-wrap {
    background: rgba(255, 107, 120, 0.18);
    color: #ff8896;
    box-shadow: 0 3px 12px rgba(255, 107, 120, 0.2);
}

:global([data-theme="dark"]) .toggle-track {
    background: #38444d;
}

:global([data-theme="dark"]) .toggle-track.is-dark {
    background: #f7f9f9;
}

:global([data-theme="dark"]) .toggle-thumb {
    background: #1e2732;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
}

:global([data-theme="dark"]) .toggle-icon {
    color: #8b98a5;
}

:global([data-theme="dark"]) .toggle-track.is-dark .toggle-icon {
    color: #8b98a5;
}

.icon-wrap {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.75);
    box-shadow:
        0 2px 8px rgba(10, 11, 13, 0.09),
        0 1px 3px rgba(10, 11, 13, 0.05);
    transition:
        background 0.14s,
        color 0.14s,
        box-shadow 0.14s;
    color: inherit;
    flex-shrink: 0;
    font-size: 17px;
}

.nav-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.1px;
    line-height: 1;
    text-align: center;
    color: inherit;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 68px;
}

@media (max-width: 640px) {
    .sidebar {
        width: 68px;
        padding: 12px 0 8px;
    }
    .sidebar-nav {
        padding: 0 6px;
    }
    .sidebar-footer {
        padding: 8px 6px 0;
    }
    .icon-wrap {
        width: 36px;
        height: 36px;
        font-size: 15px;
    }
    .nav-label {
        font-size: 9.5px;
    }
}

/* AI Chat badge dot */
.ai-badge-dot {
    position: absolute;
    top: 3px;
    right: 3px;
    width: 8px;
    height: 8px;
    background: var(--primary);
    border-radius: 50%;
    border: 2px solid var(--surface);
    animation: ai-badge-pulse 1.8s ease-in-out infinite;
}
@keyframes ai-badge-pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50%       { transform: scale(1.3); opacity: 0.7; }
}

/* AI Chat nav item — subtle highlight */
.nav-item--ai .icon-wrap { position: relative; }
</style>
