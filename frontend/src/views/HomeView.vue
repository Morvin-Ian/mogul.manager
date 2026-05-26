<template>
    <div class="home-view">
        <!-- Page Header -->
        <div class="page-hdr">
            <div class="page-hdr-left">
                <div>
                    <p class="page-sub">Manage and track your projects</p>
                    <h1 class="page-title">Project Dashboard</h1>
                </div>
            </div>
            <div class="page-hdr-right">
                <div class="search-bar">
                    <svg
                        viewBox="0 0 20 20"
                        fill="none"
                        width="16"
                        height="16"
                        class="search-icon"
                    >
                        <path
                            d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                            fill="currentColor"
                        />
                    </svg>
                    <input
                        v-model="searchQuery"
                        class="search-input"
                        placeholder="Search tasks, projects, meetings..."
                    />
                </div>
            </div>
        </div>

        <!-- Dashboard Grid -->
        <div class="dash-grid">
            <!-- ── My Tasks (left, spans 2 rows) ── -->
            <div class="panel tasks-panel">
                <div class="panel-hdr">
                    <span class="panel-title">My Tasks</span>
                    <button
                        class="add-btn"
                        @click="showProjectForm = true"
                        title="New Project"
                    >+</button>
                </div>
                <div class="task-filter">
                    <button
                        class="filter-pill"
                        :class="{ active: taskFilter === 'today' }"
                        @click="taskFilter = 'today'"
                    >
                        Today
                    </button>
                    <button
                        class="filter-pill"
                        :class="{ active: taskFilter === 'tomorrow' }"
                        @click="taskFilter = 'tomorrow'"
                    >
                        Tomorrow
                    </button>
                </div>
                <div class="ongoing-wrap">
                    <div class="ongoing-row" @click="showStatusDropdown = !showStatusDropdown">
                        <span class="ongoing-badge">{{ badgeCount }}</span>
                        <span class="ongoing-label">{{ activeStatusLabel }}</span>
                        <svg viewBox="0 0 16 16" fill="currentColor" width="13" height="13"
                            class="chevron-icon" :class="{ 'chevron-open': showStatusDropdown }">
                            <path fill-rule="evenodd"
                                d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                                clip-rule="evenodd"/>
                        </svg>
                    </div>
                    <div v-if="showStatusDropdown" class="status-dropdown">
                        <button
                            v-for="s in statusOptions" :key="String(s.value)"
                            class="status-opt"
                            :class="{ active: statusFilter === s.value }"
                            @click="selectStatus(s.value)"
                        >
                            <span class="status-opt-dot" :style="{ background: s.color }"/>
                            <span class="status-opt-label">{{ s.label }}</span>
                            <span class="status-opt-count">{{ countForStatus(s.value) }}</span>
                        </button>
                    </div>
                </div>
                <div v-if="loading" class="tasks-loading">
                    <div class="loading-dot" v-for="n in 3" :key="n" />
                </div>
                <div
                    v-else-if="displayedTasks.length === 0"
                    class="tasks-empty"
                >
                    <svg viewBox="0 0 48 48" fill="none" width="44" height="44">
                        <rect
                            x="8"
                            y="8"
                            width="14"
                            height="14"
                            rx="3"
                            stroke="#D1D5DB"
                            stroke-width="2"
                        />
                        <rect
                            x="26"
                            y="8"
                            width="14"
                            height="14"
                            rx="3"
                            stroke="#D1D5DB"
                            stroke-width="2"
                        />
                        <rect
                            x="8"
                            y="26"
                            width="14"
                            height="14"
                            rx="3"
                            stroke="#D1D5DB"
                            stroke-width="2"
                        />
                        <rect
                            x="26"
                            y="26"
                            width="14"
                            height="14"
                            rx="3"
                            stroke="#D1D5DB"
                            stroke-width="2"
                        />
                    </svg>
                    <p>No tasks yet.</p>
                    <button
                        class="btn-sm-primary"
                        @click="showProjectForm = true"
                    >
                        Create a project
                    </button>
                </div>
                <div v-else class="task-list">
                    <div
                        v-for="task in displayedTasks"
                        :key="task.id"
                        class="task-card"
                        :style="{ background: projectColorFor(task.project_id) + '0D' }"
                        @click="$router.push(`/projects/${task.project_id}`)"
                    >
                        <div class="task-card-top">
                            <div
                                class="task-proj-chip"
                                :style="{
                                    background: projectColorFor(task.project_id) + '28',
                                    color: projectColorFor(task.project_id),
                                }"
                            >
                                {{ taskInitials(task.title) }}
                            </div>
                            <button
                                class="task-check"
                                :class="{ done: task.status === 'completed' }"
                                :style="task.status === 'completed' ? { background: projectColorFor(task.project_id), borderColor: projectColorFor(task.project_id) } : {}"
                                @click.stop
                            >
                                <svg viewBox="0 0 20 20" fill="none" width="11" height="11">
                                    <path
                                        d="M4 10l4.5 4.5 7.5-8"
                                        stroke="currentColor"
                                        stroke-width="2"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                </svg>
                            </button>
                        </div>
                        <h4 class="task-title">{{ task.title }}</h4>
                        <p v-if="task.description" class="task-desc">{{ task.description }}</p>
                    </div>
                </div>
            </div>

            <!-- ── Projects Overview (center top) ── -->
            <div class="panel overview-panel">
                <div class="panel-hdr">
                    <span class="panel-title">Projects Overview</span>
                    <button class="hdr-icon-btn" title="Expand">
                        <svg
                            viewBox="0 0 16 16"
                            fill="none"
                            width="14"
                            height="14"
                        >
                            <path
                                d="M9 3h4v4M3 9v4h4M15 1L9 7M1 15l6-6"
                                stroke="currentColor"
                                stroke-width="1.5"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                        </svg>
                    </button>
                </div>
                <!-- Stat strip -->
                <div class="ov-stats">
                    <div class="ov-stat">
                        <span class="ov-num">{{ allProjects.length }}</span>
                        <span class="ov-lbl">Total</span>
                    </div>
                    <div class="ov-stat-divider"/>
                    <div class="ov-stat">
                        <span class="ov-num" style="color:#F59E0B">{{ activeCount }}</span>
                        <span class="ov-lbl">Active</span>
                    </div>
                    <div class="ov-stat-divider"/>
                    <div class="ov-stat">
                        <span class="ov-num" style="color:#3B82F6">{{ completedCount }}</span>
                        <span class="ov-lbl">Done</span>
                    </div>
                    <div class="ov-stat-divider"/>
                    <div class="ov-stat">
                        <span class="ov-num" style="color:#9CA3AF">{{ notStartedCount }}</span>
                        <span class="ov-lbl">Planned</span>
                    </div>
                </div>

                <!-- Donut + legend -->
                <div class="overview-body">
                    <div class="donut-wrap">
                        <svg class="donut-svg" viewBox="0 0 200 200">
                            <circle cx="100" cy="100" r="72" fill="none" stroke="#F0F1F6" stroke-width="26"/>
                            <circle cx="100" cy="100" r="72" fill="none" stroke="#F59E0B" stroke-width="26"
                                :stroke-dasharray="`${ipArc} ${circumference}`"
                                stroke-dashoffset="0"
                                transform="rotate(-90 100 100)" stroke-linecap="round"/>
                            <circle cx="100" cy="100" r="72" fill="none" stroke="#3B82F6" stroke-width="26"
                                :stroke-dasharray="`${compArc} ${circumference}`"
                                :stroke-dashoffset="`${-ipArc}`"
                                transform="rotate(-90 100 100)" stroke-linecap="round"/>
                            <circle cx="100" cy="100" r="72" fill="none" stroke="#E5E7EB" stroke-width="26"
                                :stroke-dasharray="`${nsArc} ${circumference}`"
                                :stroke-dashoffset="`${-(ipArc + compArc)}`"
                                transform="rotate(-90 100 100)" stroke-linecap="round"/>
                            <text x="100" y="93" text-anchor="middle" font-size="34" font-weight="800"
                                fill="#0A0B0D" font-family="Outfit, sans-serif">{{ allProjects.length }}</text>
                            <text x="100" y="114" text-anchor="middle" font-size="13" fill="#5B616E"
                                font-family="Outfit, sans-serif">projects</text>
                        </svg>
                    </div>
                    <div class="donut-legend">
                        <div class="legend-row">
                            <span class="legend-dot" style="background:#F59E0B"/>
                            <span class="legend-text">Active <strong>{{ activeCount }}</strong></span>
                        </div>
                        <div class="legend-row">
                            <span class="legend-dot" style="background:#3B82F6"/>
                            <span class="legend-text">Completed <strong>{{ completedCount }}</strong></span>
                        </div>
                        <div class="legend-row">
                            <span class="legend-dot" style="background:#E5E7EB"/>
                            <span class="legend-text">Planned <strong>{{ notStartedCount }}</strong></span>
                        </div>
                    </div>
                </div>

                <!-- Recent projects -->
                <div v-if="allProjects.length > 0" class="ov-recent">
                    <span class="ov-recent-hdr">Recent</span>
                    <div
                        v-for="(p, idx) in allProjects.slice(0, 3)"
                        :key="p.id"
                        class="ov-proj-row"
                        @click="$router.push(`/projects/${p.id}`)"
                    >
                        <span class="ov-proj-dot" :style="{ background: PROJECT_COLORS[idx % PROJECT_COLORS.length] }"/>
                        <span class="ov-proj-name">{{ p.title }}</span>
                        <span class="badge" :class="`badge-${p.status}`">{{ (p.status ?? 'todo').replace('_',' ') }}</span>
                    </div>
                </div>
                <div v-else class="ov-empty">
                    <p>No projects yet — create one to get started.</p>
                </div>
            </div>

            <!-- ── Quick Actions (center top) ── -->
            <div class="panel quickactions-panel">
                <div class="panel-hdr">
                    <span class="panel-title">Quick Actions</span>
                </div>
                <div class="qa-list">
                    <button class="qa-card" @click="showProjectForm = true">
                        <div class="qa-icon">
                            <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
                                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M12 11v6M9 14h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            </svg>
                        </div>
                        <div class="qa-text">
                            <span class="qa-title">New Project</span>
                            <span class="qa-desc">Organize work into projects</span>
                        </div>
                        <svg viewBox="0 0 16 16" fill="none" width="14" height="14" class="qa-arrow">
                            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="qa-card" @click="$router.push('/chat')">
                        <div class="qa-icon">
                            <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
                                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </div>
                        <div class="qa-text">
                            <span class="qa-title">AI Chat</span>
                            <span class="qa-desc">Get instant AI assistance</span>
                        </div>
                        <svg viewBox="0 0 16 16" fill="none" width="14" height="14" class="qa-arrow">
                            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="qa-card" @click="$router.push('/documents')">
                        <div class="qa-icon">
                            <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
                                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            </svg>
                        </div>
                        <div class="qa-text">
                            <span class="qa-title">Documents</span>
                            <span class="qa-desc">Browse files and resources</span>
                        </div>
                        <svg viewBox="0 0 16 16" fill="none" width="14" height="14" class="qa-arrow">
                            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="qa-card">
                        <div class="qa-icon">
                            <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
                                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </div>
                        <div class="qa-text">
                            <span class="qa-title">Invite Team</span>
                            <span class="qa-desc">Collaborate with your team</span>
                        </div>
                        <svg viewBox="0 0 16 16" fill="none" width="14" height="14" class="qa-arrow">
                            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- ── Workspaces (center bottom) ── -->
            <div class="panel workspaces-panel">
                <div class="panel-hdr">
                    <span class="panel-title">Workspaces</span>
                    <button class="create-new-btn" @click="showWorkspaceForm = true">
                        <svg viewBox="0 0 16 16" fill="none" width="11" height="11">
                            <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        Create new
                    </button>
                </div>
                <div v-if="workspaceStore.workspaces.length === 0" class="ws-empty-state">
                    <p>No workspaces yet</p>
                    <button class="create-new-btn" @click="showWorkspaceForm = true">Get started</button>
                </div>
                <div v-else class="ws-cards-grid">
                    <div
                        v-for="(ws, idx) in workspaceStore.workspaces"
                        :key="ws.id"
                        class="ws-card"
                        :style="{ background: WS_BG_COLORS[idx % WS_BG_COLORS.length] }"
                    >
                        <div class="ws-card-top">
                            <span class="ws-card-count">{{ wsProjectCount(ws.id) }} project{{ wsProjectCount(ws.id) !== 1 ? 's' : '' }}</span>
                            <div class="ws-menu-wrap">
                                <button class="ws-card-menu" @click.stop="wsMenuOpenId = wsMenuOpenId === ws.id ? null : ws.id">⋯</button>
                                <div v-if="wsMenuOpenId === ws.id" class="ws-dropdown">
                                    <button class="ws-dd-item" @click.stop="openEditWorkspace(ws)">
                                        <svg viewBox="0 0 16 16" fill="none" width="13" height="13"><path d="M11.5 2.5a2.121 2.121 0 013 3L5 15H2v-3L11.5 2.5z" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
                                        Edit
                                    </button>
                                    <button class="ws-dd-item ws-dd-danger" @click.stop="deleteWorkspace(ws.id)">
                                        <svg viewBox="0 0 16 16" fill="none" width="13" height="13"><path d="M2 4h12M5 4V3a1 1 0 011-1h4a1 1 0 011 1v1M6 7v5M10 7v5M3 4l1 9a1 1 0 001 1h6a1 1 0 001-1l1-9" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="ws-card-body">
                            <p class="ws-card-name">{{ ws.title }}</p>
                            <p class="ws-card-sub">{{ ws.description || 'Workspace' }}</p>
                        </div>
                        <div class="ws-card-footer">
                            <div class="ws-card-initial">{{ ws.title.slice(0,1).toUpperCase() }}</div>
                            <span class="ws-card-cta">View →</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ── Upcoming Deadlines (right top) ── -->
            <div class="panel deadlines-panel">
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
                                {{ item.subtitle }}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ── Comments (right bottom) ── -->
            <div class="panel comments-panel">
                <div class="panel-hdr">
                    <span class="panel-title">Comments</span>
                    <span class="comments-count-badge" v-if="topLevelComments.length">{{ commentStore.all.length }}</span>
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
                                <span class="comment-task-label">{{ taskTitleFor(c.task_id) }}</span>
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
                        <p v-else class="comment-content">{{ c.content }}</p>

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
                        <option v-for="t in allTasks.slice(0, 12)" :key="t.id" :value="t.id">{{ t.title }}</option>
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
        </div>

        <!-- Project creation modal -->
        <ProjectForm
            v-if="showProjectForm"
            @close="showProjectForm = false"
            @saved="handleProjectSaved"
        />

        <!-- Workspace create / edit modal -->
        <WorkspaceForm
            v-if="showWorkspaceForm"
            :workspace="editingWorkspace"
            @close="showWorkspaceForm = false; editingWorkspace = null"
            @saved="handleWorkspaceSaved"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useWorkspaceStore } from "../stores/workspaces";
import { useProjectStore } from "../stores/projects";
import { useCommentStore } from "../stores/comments";
import { useAuthStore } from "../stores/auth";
import { get } from "../stores/client";
import type { Task, Project, Workspace } from "../types";
import ProjectForm from "../components/project/ProjectForm.vue";
import WorkspaceForm from "../components/workspace/WorkspaceForm.vue";

const workspaceStore = useWorkspaceStore();
const projectStore = useProjectStore();
const commentStore = useCommentStore();
const auth = useAuthStore();

const loading = ref(false);
const searchQuery = ref("");
const taskFilter = ref<"today" | "tomorrow">("today");
const showProjectForm = ref(false);
const showWorkspaceForm = ref(false);
const editingWorkspace = ref<Workspace | null>(null);
const wsMenuOpenId = ref<number | null>(null);
const newCommentContent = ref("");
const newCommentTaskId = ref<number | null>(null);
const editingCommentId = ref<number | null>(null);
const editingContent = ref("");
const replyingToId = ref<number | null>(null);
const replyContent = ref("");
const expandedReplies = ref<Set<number>>(new Set());
const showStatusDropdown = ref(false);
const statusFilter = ref<string | null>(null);
const allProjects = ref<Project[]>([]);
const allTasks = ref<Task[]>([]);

const statusOptions = [
    { value: null,          label: "All Tasks",    color: "#6B7280" },
    { value: "todo",        label: "To Do",        color: "#7C3AED" },
    { value: "in_progress", label: "In Progress",  color: "#F59E0B" },
    { value: "review",      label: "In Review",    color: "#3B82F6" },
    { value: "blocked",     label: "Blocked",      color: "#EF4444" },
    { value: "completed",   label: "Completed",    color: "#10B981" },
];

function countForStatus(value: string | null) {
    if (value === null) return allTasks.value.filter(t => t.status !== "completed").length;
    return allTasks.value.filter(t => t.status === value).length;
}

function selectStatus(value: string | null) {
    statusFilter.value = value;
    showStatusDropdown.value = false;
}

const PROJECT_COLORS = [
    "#F59E0B",
    "#6B7280",
    "#EC4899",
    "#6366F1",
    "#10B981",
    "#EF4444",
    "#F97316",
    "#3B82F6",
];

const WS_COLORS = ["#0052FF", "#059669", "#9333EA", "#D97706", "#EF4444"];
const WS_BG_COLORS = ["#D6EEDC", "#FFE8D6", "#EAD6FF", "#FFD6E7", "#D6E8FF"];

function wsProjectCount(wsId: number): number {
    return allProjects.value.filter((p) => (p as any).workspace_id === wsId).length;
}

function projectColorFor(projectId: number): string {
    const idx = allProjects.value.findIndex((p) => p.id === projectId);
    return PROJECT_COLORS[Math.max(0, idx) % PROJECT_COLORS.length];
}

function projectNameFor(projectId: number): string {
    return (
        allProjects.value.find((p) => p.id === projectId)?.title ??
        "Unknown Project"
    );
}


function taskInitials(title: string): string {
    const words = title.trim().split(/\s+/);
    if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
    return words[0].slice(0, 2).toUpperCase();
}

// ── Computed task lists ──────────────────────────────────────────
const badgeCount = computed(() => countForStatus(statusFilter.value));

const activeStatusLabel = computed(() =>
    statusOptions.find(s => s.value === statusFilter.value)?.label ?? "On Going Tasks"
);

const displayedTasks = computed(() => {
    const tomorrow = new Date(Date.now() + 86400000).toDateString();
    let tasks = allTasks.value;

    // Search filter
    if (searchQuery.value.trim()) {
        const q = searchQuery.value.toLowerCase();
        tasks = tasks.filter(
            (t) =>
                t.title.toLowerCase().includes(q) ||
                (t.description ?? "").toLowerCase().includes(q),
        );
    }

    // Status filter — only applied when user explicitly picks one
    if (statusFilter.value !== null) {
        tasks = tasks.filter(t => t.status === statusFilter.value);
    }

    // Date filter — Tomorrow narrows by due date; Today shows everything
    if (taskFilter.value === "tomorrow") {
        tasks = tasks.filter(
            (t) => t.due_date && new Date(t.due_date).toDateString() === tomorrow,
        );
    }

    return tasks.slice(0, 8);
});

// ── Computed project counts ──────────────────────────────────────
const activeCount = computed(
    () => allProjects.value.filter((p) => p.status === "active").length,
);
const completedCount = computed(
    () => allProjects.value.filter((p) => p.status === "completed").length,
);
const notStartedCount = computed(
    () =>
        allProjects.value.filter(
            (p) => p.status === "planning" || p.status === "on_hold",
        ).length,
);

const circumference = 2 * Math.PI * 72; // ≈ 452.4
const ipArc = computed(() => {
    const total = allProjects.value.length;
    return total > 0 ? (activeCount.value / total) * circumference : 0;
});
const compArc = computed(() => {
    const total = allProjects.value.length;
    return total > 0 ? (completedCount.value / total) * circumference : 0;
});
const nsArc = computed(() => {
    const total = allProjects.value.length;
    return total > 0 ? (notStartedCount.value / total) * circumference : 0;
});


// ── Static data ───────────────────────────────────────────────────


// ── Data loading ──────────────────────────────────────────────────
async function loadAllData() {
    loading.value = true;
    try {
        await workspaceStore.fetchAll();
        const wsIds = workspaceStore.workspaces.map((ws) => ws.id);
        if (wsIds.length === 0) {
            loading.value = false;
            return;
        }

        const projectArrays = await Promise.all(
            wsIds.map((id) => get<Project[]>(`/projects?workspace_id=${id}`)),
        );
        allProjects.value = projectArrays.flat();

        const projectIds = allProjects.value.slice(0, 6).map((p) => p.id);
        if (projectIds.length > 0) {
            const taskArrays = await Promise.all(
                projectIds.map((id) => get<Task[]>(`/tasks?project_id=${id}`)),
            );
            allTasks.value = taskArrays.flat();

            // Load comments for the first 5 tasks
            commentStore.clear();
            const commentTasks = allTasks.value.slice(0, 5);
            await Promise.allSettled(
                commentTasks.map((t) => commentStore.fetchForTask(t.id)),
            );
        }
    } catch (e) {
        console.error("Failed to load dashboard data", e);
    } finally {
        loading.value = false;
    }
}

onMounted(loadAllData);

async function handleWorkspaceSaved(data: { title: string; description: string }) {
    if (editingWorkspace.value) {
        await workspaceStore.update(editingWorkspace.value.id, data);
        editingWorkspace.value = null;
    } else {
        await workspaceStore.create(data);
    }
    showWorkspaceForm.value = false;
    await loadAllData();
}

function openEditWorkspace(ws: Workspace) {
    editingWorkspace.value = ws;
    showWorkspaceForm.value = true;
    wsMenuOpenId.value = null;
}

async function deleteWorkspace(id: number) {
    if (!confirm("Delete this workspace? All projects inside will also be deleted.")) return;
    wsMenuOpenId.value = null;
    await workspaceStore.remove(id);
    await loadAllData();
}

async function submitComment() {
    const content = newCommentContent.value.trim();
    if (!content || !newCommentTaskId.value) return;
    await commentStore.create({ task_id: newCommentTaskId.value, content });
    newCommentContent.value = "";
}

async function submitReply(parentId: number) {
    const content = replyContent.value.trim();
    if (!content) return;
    const parent = commentStore.all.find((c) => c.id === parentId);
    if (!parent) return;
    await commentStore.create({ task_id: parent.task_id, content, parent_id: parentId });
    replyContent.value = "";
    replyingToId.value = null;
    expandedReplies.value = new Set([...expandedReplies.value, parentId]);
}

async function deleteComment(id: number) {
    await commentStore.remove(id);
}

function startEdit(c: { id: number; content: string }) {
    editingCommentId.value = c.id;
    editingContent.value = c.content;
}

async function saveEdit(id: number) {
    const content = editingContent.value.trim();
    if (!content) return;
    await commentStore.update(id, content);
    editingCommentId.value = null;
    editingContent.value = "";
}

function startReply(commentId: number) {
    replyingToId.value = replyingToId.value === commentId ? null : commentId;
    replyContent.value = "";
}

function toggleReplies(commentId: number) {
    const next = new Set(expandedReplies.value);
    if (next.has(commentId)) next.delete(commentId);
    else next.add(commentId);
    expandedReplies.value = next;
}

function taskTitleFor(taskId: number): string {
    return allTasks.value.find((t) => t.id === taskId)?.title ?? "Unknown task";
}

const COMMENT_COLORS = ["#F59E0B","#3B82F6","#10B981","#6366F1","#EC4899","#EF4444","#F97316"];
function commentColor(userId: number): string {
    return COMMENT_COLORS[userId % COMMENT_COLORS.length];
}

function timeAgo(dateStr: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
}

const topLevelComments = computed(() =>
    [...commentStore.all]
        .filter((c) => c.parent_id === null)
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, 8),
);

function repliesFor(parentId: number) {
    return commentStore.all
        .filter((c) => c.parent_id === parentId)
        .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
}

// keep recentComments as alias used by the count badge
const recentComments = topLevelComments;

type Urgency = "overdue" | "today" | "soon" | "later";

function classifyDeadline(date: Date): { label: string; urgency: Urgency } {
    const diff = Math.floor((date.getTime() - Date.now()) / 86400000);
    if (diff < 0)  return { label: `${Math.abs(diff)}d ago`,  urgency: "overdue" };
    if (diff === 0) return { label: "Today",                   urgency: "today" };
    if (diff === 1) return { label: "Tomorrow",                urgency: "soon" };
    if (diff <= 7)  return { label: `${diff}d left`,           urgency: "soon" };
    return             { label: `${diff}d left`,               urgency: "later" };
}

const upcomingDeadlines = computed(() => {
    const taskItems = allTasks.value
        .filter((t) => t.due_date && t.status !== "completed")
        .map((t) => {
            const d = new Date(t.due_date!);
            const { label, urgency } = classifyDeadline(d);
            return {
                id: `task-${t.id}`,
                title: t.title,
                subtitle: projectNameFor(t.project_id),
                dueDate: d,
                type: "task" as const,
                projectId: t.project_id,
                label,
                urgency,
            };
        });

    const projItems = allProjects.value
        .filter((p) => p.due_date && p.status !== "completed" && p.status !== "archived")
        .map((p) => {
            const d = new Date(p.due_date!);
            const { label, urgency } = classifyDeadline(d);
            return {
                id: `proj-${p.id}`,
                title: p.title,
                subtitle: "Project deadline",
                dueDate: d,
                type: "project" as const,
                projectId: p.id,
                label,
                urgency,
            };
        });

    return [...taskItems, ...projItems]
        .sort((a, b) => a.dueDate.getTime() - b.dueDate.getTime())
        .slice(0, 8);
});

async function handleProjectSaved(data: Record<string, any>) {
    let wsId = workspaceStore.workspaces[0]?.id;
    if (!wsId) {
        const ws = await workspaceStore.create({
            title: "My Projects",
            description: null,
        });
        wsId = ws.id;
    }
    await projectStore.create({ ...data, workspace_id: wsId } as any);
    showProjectForm.value = false;
    await loadAllData();
}
</script>

<style scoped>
.home-view {
    padding: 28px 32px;
    min-height: 100%;
}

/* ── Page Header ────────────────────── */
.page-hdr {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    gap: 20px;
}

.page-hdr-left {
    display: flex;
    align-items: center;
    gap: 16px;
}

.page-icon-box {
    width: 52px;
    height: 52px;
    background: #1c1c1e;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.page-sub {
    font-size: 13.5px;
    color: var(--text-muted);
    font-weight: 400;
    margin-bottom: 3px;
}

.page-title {
    font-size: 30px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.5px;
    line-height: 1.2;
}

.page-hdr-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.search-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.65);
    border: 1.5px solid rgba(200, 200, 208, 0.8);
    border-radius: var(--radius-full);
    padding: 10px 20px;
    width: 420px;
    transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
    box-shadow: 0 1px 6px rgba(10,11,13,0.06);
}

.search-bar:focus-within {
    border-color: var(--border-strong);
    background: rgba(255,255,255,0.95);
    box-shadow: 0 2px 12px rgba(10,11,13,0.09);
}

.search-icon {
    color: var(--text-muted);
    flex-shrink: 0;
}

.search-input {
    border: none;
    outline: none;
    background: none;
    font-size: 13.5px;
    color: var(--text);
    width: 100%;
}

.search-input::placeholder {
    color: var(--text-light);
}


/* ── Dashboard Grid ─────────────────── */
.dash-grid {
    display: grid;
    grid-template-columns: 340px minmax(0, 1fr) 330px;
    grid-template-rows: auto auto auto;
    gap: 18px;
}

/* ── Panels ─────────────────────────── */
.panel {
    background: #ffffff;
    border-radius: var(--radius-lg);
    padding: 20px 22px;
    border: none;
    box-shadow: 0 4px 24px rgba(10, 11, 13, 0.09), 0 1px 6px rgba(10, 11, 13, 0.06);
}

.tasks-panel {
    grid-column: 1;
    grid-row: 1 / 4;
    display: flex;
    flex-direction: column;
}
.overview-panel {
    grid-column: 2;
    grid-row: 1;
}
.quickactions-panel {
    grid-column: 2;
    grid-row: 2;
}
.workspaces-panel {
    grid-column: 2;
    grid-row: 3;
}
.deadlines-panel {
    grid-column: 3;
    grid-row: 1;
}
.comments-panel {
    grid-column: 3;
    grid-row: 2 / 4;
}

.panel-hdr {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}

.panel-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.3px;
}

.hdr-icon-btn {
    width: 30px;
    height: 30px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    cursor: pointer;
    transition:
        background 0.12s,
        color 0.12s;
}

.hdr-icon-btn:hover {
    background: var(--border);
    color: var(--text);
}

.hdr-icon-btn-sm {
    width: 24px;
    height: 24px;
    background: none;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: 6px;
    transition: background 0.12s;
}

.hdr-icon-btn-sm:hover {
    background: var(--bg);
}

/* ── My Tasks Panel ─────────────────── */
.add-btn {
    width: 30px;
    height: 30px;
    background: transparent;
    border: 1.5px solid var(--border-strong);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 20px;
    font-weight: 300;
    line-height: 1;
    transition: border-color 0.12s, color 0.12s;
    padding-bottom: 1px;
}
.add-btn:hover {
    border-color: var(--text);
    color: var(--text);
}

.task-filter {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}

.filter-pill {
    padding: 7px 18px;
    border-radius: var(--radius-full);
    border: 1.5px solid var(--border);
    background: transparent;
    font-size: 14px;
    font-weight: 400;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.12s;
}

.filter-pill.active {
    background: #1c1c1e;
    color: #fff;
    border-color: #1c1c1e;
    font-weight: 500;
}

.ongoing-wrap {
    position: relative;
    margin-bottom: 18px;
}

.ongoing-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 13px 18px;
    border: 1.5px solid var(--border);
    border-radius: 20px;
    background: #ffffff;
    cursor: pointer;
    font-size: 14.5px;
    color: var(--text-muted);
    font-weight: 400;
    transition: border-color 0.12s, box-shadow 0.12s;
}

.ongoing-row:hover {
    border-color: var(--border-strong);
    box-shadow: 0 2px 8px rgba(10,11,13,0.07);
}

.ongoing-badge {
    min-width: 26px;
    height: 26px;
    padding: 0 7px;
    background: #1c1c1e;
    color: #fff;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    flex-shrink: 0;
}

.ongoing-label {
    flex: 1;
    color: var(--text);
    font-weight: 500;
}

.chevron-icon {
    color: var(--text-light);
    transition: transform 0.2s;
}

.chevron-open {
    transform: rotate(180deg);
}

/* ── Status Dropdown ────────────────── */
.status-dropdown {
    position: absolute;
    top: calc(100% + 6px);
    left: 0;
    right: 0;
    background: #ffffff;
    border: 1.5px solid var(--border);
    border-radius: 16px;
    padding: 6px;
    z-index: 50;
    box-shadow: 0 8px 24px rgba(10,11,13,0.12);
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.status-opt {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border: none;
    background: none;
    border-radius: 12px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 400;
    color: var(--text-muted);
    transition: background 0.12s, color 0.12s;
    text-align: left;
    width: 100%;
}

.status-opt:hover {
    background: var(--bg);
    color: var(--text);
}

.status-opt.active {
    background: var(--bg);
    color: var(--text);
    font-weight: 500;
}

.status-opt-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.status-opt-label {
    flex: 1;
}

.status-opt-count {
    font-size: 12.5px;
    font-weight: 600;
    color: var(--text-muted);
    background: var(--bg);
    border-radius: 999px;
    padding: 1px 8px;
}

.tasks-loading {
    display: flex;
    gap: 6px;
    justify-content: center;
    padding: 32px 0;
}

.loading-dot {
    width: 8px;
    height: 8px;
    background: var(--border-strong);
    border-radius: 50%;
    animation: pulse 1.2s ease-in-out infinite;
}

.loading-dot:nth-child(2) {
    animation-delay: 0.2s;
}
.loading-dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes pulse {
    0%,
    80%,
    100% {
        opacity: 0.3;
        transform: scale(0.8);
    }
    40% {
        opacity: 1;
        transform: scale(1);
    }
}

.tasks-empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 32px 0;
    color: var(--text-muted);
    text-align: center;
}

.tasks-empty p {
    font-size: 13px;
}

.btn-sm-primary {
    padding: 7px 16px;
    background: #1c1c1e;
    color: #fff;
    border: none;
    border-radius: var(--radius-full);
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s;
}

.btn-sm-primary:hover {
    opacity: 0.85;
}

.task-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
    flex: 1;
    overflow-y: auto;
    max-height: 540px;
    padding-right: 2px;
}

.task-card {
    border: 1.5px solid rgba(0, 0, 0, 0.05);
    border-radius: 18px;
    padding: 18px 18px 20px 20px;
    cursor: pointer;
    transition: box-shadow 0.15s, transform 0.15s;
}

.task-card:hover {
    box-shadow: 0 6px 20px rgba(10, 11, 13, 0.08);
    transform: translateY(-1px);
}

.task-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.task-proj-chip {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 700;
    flex-shrink: 0;
}

.task-check {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    border: 1.5px solid var(--border-strong);
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: transparent;
    flex-shrink: 0;
    transition: border-color 0.15s, background 0.15s, color 0.15s;
}

.task-check:hover {
    border-color: #10B981;
    color: #10B981;
}

.task-check.done {
    color: #ffffff;
}

.task-proj-name {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
    margin-bottom: 5px;
    letter-spacing: 0.1px;
}

.task-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 10px;
    line-height: 1.4;
}

.task-desc {
    font-size: 14px;
    color: var(--text-muted);
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ── Projects Overview ──────────────── */
.ov-stats {
    display: flex;
    align-items: stretch;
    border: 1.5px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 20px;
}

.ov-stat {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    padding: 14px 10px;
}

.ov-stat-divider {
    width: 1px;
    background: var(--border);
    flex-shrink: 0;
}

.ov-num {
    font-size: 26px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.5px;
    line-height: 1;
}

.ov-lbl {
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 500;
    letter-spacing: 0.1px;
}

.overview-body {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 24px;
}

.donut-wrap {
    flex-shrink: 0;
}

.donut-svg {
    width: 148px;
    height: 148px;
    display: block;
}

.donut-legend {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.legend-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--text-muted);
}

.legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}

.legend-text strong {
    color: var(--text);
}

.ov-recent {
    margin-top: 16px;
    border-top: 1.5px solid var(--border);
    padding-top: 14px;
}

.ov-recent-hdr {
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 0.5px;
    text-transform: uppercase;
    display: block;
    margin-bottom: 10px;
}

.ov-proj-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.12s;
}
.ov-proj-row:hover { background: var(--bg); }

.ov-proj-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.ov-proj-name {
    flex: 1;
    font-size: 13.5px;
    font-weight: 500;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.ov-empty {
    margin-top: 12px;
    font-size: 13px;
    color: var(--text-muted);
    text-align: center;
    padding: 12px 0;
}

/* ── Quick Actions Panel ────────────── */
.qa-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.qa-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 16px;
    border: 1.5px solid var(--border);
    border-radius: 14px;
    background: #ffffff;
    cursor: pointer;
    text-align: left;
    width: 100%;
    transition: border-color 0.14s, box-shadow 0.14s;
}
.qa-card:hover {
    border-color: var(--border-strong);
    box-shadow: 0 3px 14px rgba(10,11,13,0.07);
}

.qa-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #1c1c1e;
    flex-shrink: 0;
}

.qa-text {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.qa-title {
    font-size: 14.5px;
    font-weight: 700;
    color: var(--text);
    line-height: 1.3;
}

.qa-desc {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 400;
    line-height: 1.4;
}

.qa-arrow {
    color: var(--text-light);
    flex-shrink: 0;
    transition: color 0.12s, transform 0.12s;
}
.qa-card:hover .qa-arrow {
    color: var(--text);
    transform: translateX(2px);
}

/* ── Workspaces Panel ───────────────── */
.create-new-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 9px 18px;
    background: #1c1c1e;
    color: #fff;
    border: none;
    border-radius: var(--radius-full);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s;
    white-space: nowrap;
}
.create-new-btn:hover { opacity: 0.8; }

.ws-empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 24px 0;
    color: var(--text-muted);
    font-size: 13.5px;
}

.ws-cards-grid {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding-bottom: 4px;
}
.ws-cards-grid::-webkit-scrollbar { height: 4px; }
.ws-cards-grid::-webkit-scrollbar-track { background: transparent; }
.ws-cards-grid::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

.ws-card {
    flex: 1;
    min-width: 160px;
    border-radius: 18px;
    padding: 18px 18px 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-height: 140px;
    cursor: pointer;
    transition: box-shadow 0.15s, transform 0.15s;
    border: none;
}
.ws-card:hover {
    box-shadow: 0 8px 24px rgba(10,11,13,0.12);
    transform: translateY(-2px);
}

.ws-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.ws-card-count {
    font-size: 11px;
    font-weight: 600;
    color: rgba(0,0,0,0.45);
    letter-spacing: 0.2px;
}

.ws-card-menu {
    background: none;
    border: none;
    font-size: 16px;
    color: rgba(0,0,0,0.35);
    cursor: pointer;
    padding: 0 2px;
    line-height: 1;
}

.ws-card-body { flex: 1; }

.ws-card-name {
    font-size: 17px;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1.3;
    margin-bottom: 4px;
}

.ws-card-sub {
    font-size: 12.5px;
    color: rgba(0,0,0,0.45);
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.ws-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: auto;
}

.ws-card-initial {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: rgba(0,0,0,0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 800;
    color: rgba(0,0,0,0.55);
}

.ws-card-cta {
    font-size: 12px;
    font-weight: 600;
    color: rgba(0,0,0,0.45);
}

/* ── Deadlines Panel ─────────────────── */
.deadlines-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 32px 0 24px;
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
    gap: 7px;
}

.deadline-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 12px;
    border: 1.5px solid transparent;
    cursor: pointer;
    transition: filter 0.12s, transform 0.12s;
}
.deadline-row:hover { filter: brightness(0.97); transform: translateX(2px); }

.urgency-overdue { background: #FFF2F2; border-color: #FECACA; }
.urgency-today   { background: #FFFBEB; border-color: #FDE68A; }
.urgency-soon    { background: #EFF6FF; border-color: #BFDBFE; }
.urgency-later   { background: var(--bg); border-color: var(--border); }

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
.dl-badge-overdue { background: #FEE2E2; color: #DC2626; }
.dl-badge-today   { background: #FEF3C7; color: #D97706; }
.dl-badge-soon    { background: #DBEAFE; color: #1D4ED8; }
.dl-badge-later   { background: #F3F4F6; color: #6B7280; }

.deadline-info { flex: 1; min-width: 0; }

.deadline-title {
    font-size: 13.5px;
    font-weight: 600;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 3px;
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
.deadline-type-dot.task    { background: #3B82F6; }
.deadline-type-dot.project { background: #F59E0B; }

/* ── Workspace dropdown ─────────────── */
.ws-menu-wrap {
    position: relative;
}

.ws-dropdown {
    position: absolute;
    top: calc(100% + 4px);
    right: 0;
    background: #ffffff;
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 4px;
    z-index: 100;
    box-shadow: 0 8px 24px rgba(10,11,13,0.14);
    min-width: 130px;
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.ws-dd-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 9px 12px;
    border: none;
    background: none;
    border-radius: 9px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text);
    cursor: pointer;
    transition: background 0.1s;
    text-align: left;
    width: 100%;
}
.ws-dd-item:hover { background: var(--bg); }
.ws-dd-danger { color: #EF4444; }
.ws-dd-danger:hover { background: #FEF2F2; }

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

/* ── Comment card (Open-Tickets style) ── */
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

/* ── Owner actions ── */
.comment-card-actions {
    display: flex;
    gap: 8px;
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

/* ── Responsive ─────────────────────── */
@media (max-width: 1300px) {
    .dash-grid {
        grid-template-columns: 300px minmax(0, 1fr) 300px;
    }
}

@media (max-width: 960px) {
    .dash-grid {
        grid-template-columns: 1fr 1fr;
        grid-template-rows: auto;
    }
    .tasks-panel {
        grid-column: 1 / 3;
        grid-row: 1;
    }
    .overview-panel {
        grid-column: 1;
        grid-row: 2;
    }
    .quickactions-panel {
        grid-column: 2;
        grid-row: 3;
    }
    .workspaces-panel {
        grid-column: 1 / 3;
        grid-row: 3;
    }
    .deadlines-panel {
        grid-column: 1;
        grid-row: 4;
    }
    .comments-panel {
        grid-column: 2;
        grid-row: 4;
    }
}

@media (max-width: 640px) {
    .home-view {
        padding: 16px;
    }
    .dash-grid {
        grid-template-columns: 1fr;
    }
    .tasks-panel,
    .overview-panel,
    .workspaces-panel,
    .quickactions-panel,
    .deadlines-panel,
    .comments-panel {
        grid-column: 1;
        grid-row: auto;
    }
    .search-bar {
        width: 200px;
    }
    .page-title {
        font-size: 20px;
    }
}
</style>
