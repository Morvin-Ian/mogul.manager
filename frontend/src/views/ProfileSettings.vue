<template>
  <div class="settings-page">

    <!-- Page header -->
    <div class="page-header">
      <div class="page-header-avatar">
        <img v-if="auth.user?.profile_path" :src="auth.user.profile_path" class="header-avatar-img" alt="Profile" />
        <div v-else class="header-avatar-fallback">{{ initials }}</div>
      </div>
      <div>
        <h1>{{ auth.user?.username }}</h1>
        <p class="header-meta">{{ auth.user?.email }}</p>
      </div>
    </div>

    <!-- Profile section -->
    <section class="settings-section">
      <div class="section-heading">
        <h2>Profile</h2>
        <p>Update your display name, email address, and profile photo.</p>
      </div>
      <div class="card">
        <!-- Avatar row -->
        <div class="card-row avatar-row">
          <div class="avatar-group">
            <div class="avatar-wrap">
              <img v-if="auth.user?.profile_path" :src="auth.user.profile_path" class="avatar-img" alt="Profile" />
              <div v-else class="avatar-fallback">{{ initials }}</div>
              <label class="avatar-camera" :class="{ loading: picLoading }" title="Change photo">
                <svg v-if="!picLoading" viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                  <path fill-rule="evenodd" d="M4 5a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V7a2 2 0 00-2-2h-1.586a1 1 0 01-.707-.293l-1.121-1.121A2 2 0 0011.172 3H8.828a2 2 0 00-1.414.586L6.293 4.707A1 1 0 015.586 5H4zm6 9a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
                </svg>
                <span v-else class="spinner spinner-sm"></span>
                <input type="file" accept="image/*" @change="handlePicUpload" :disabled="picLoading" style="display:none" />
              </label>
            </div>
            <div class="avatar-meta">
              <span class="avatar-name">{{ auth.user?.username }}</span>
              <div class="avatar-btns">
                <button
                  v-if="auth.user?.profile_path"
                  class="btn btn-sm btn-ghost text-danger"
                  :disabled="picLoading"
                  @click="handlePicDelete"
                >
                  Remove photo
                </button>
              </div>
            </div>
          </div>
          <div class="feedback-inline">
            <p v-if="picError" class="inline-error">{{ picError }}</p>
            <p v-if="picSuccess" class="inline-success">{{ picSuccess }}</p>
          </div>
        </div>

        <div class="card-divider" />

        <!-- Info form -->
        <form @submit.prevent="handleProfileSave" novalidate class="card-row">
          <div class="form-row">
            <div class="form-group">
              <label for="username">Username</label>
              <input id="username" v-model="profileForm.username" type="text" minlength="2" maxlength="50" placeholder="Your username" />
            </div>
            <div class="form-group">
              <label for="email">Email address</label>
              <input id="email" v-model="profileForm.email" type="email" placeholder="name@example.com" />
            </div>
          </div>
          <p v-if="profileError" class="form-error">{{ profileError }}</p>
          <p v-if="profileSuccess" class="inline-success">{{ profileSuccess }}</p>
          <div class="card-footer">
            <button type="submit" class="btn btn-primary" :disabled="profileLoading">
              <span v-if="profileLoading" class="spinner spinner-white"></span>
              {{ profileLoading ? 'Saving…' : 'Save changes' }}
            </button>
          </div>
        </form>
      </div>
    </section>

    <!-- Password section -->
    <section class="settings-section">
      <div class="section-heading">
        <h2>Password</h2>
        <p>Change your password. You'll need your current password to update it.</p>
      </div>
      <div class="card">
        <form @submit.prevent="handlePasswordSave" novalidate class="card-row">
          <div class="form-group">
            <label for="current-pw">Current password</label>
            <input id="current-pw" v-model="pwForm.current" type="password" autocomplete="current-password" placeholder="Enter your current password" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="new-pw">New password</label>
              <input id="new-pw" v-model="pwForm.next" type="password" autocomplete="new-password" placeholder="At least 8 characters" minlength="8" />
            </div>
            <div class="form-group">
              <label for="confirm-pw">Confirm new password</label>
              <input id="confirm-pw" v-model="pwForm.confirm" type="password" autocomplete="new-password" placeholder="Repeat your new password" />
            </div>
          </div>
          <p v-if="pwError" class="form-error">{{ pwError }}</p>
          <p v-if="pwSuccess" class="inline-success">{{ pwSuccess }}</p>
          <div class="card-footer">
            <button type="submit" class="btn btn-primary" :disabled="pwLoading">
              <span v-if="pwLoading" class="spinner spinner-white"></span>
              {{ pwLoading ? 'Updating…' : 'Update password' }}
            </button>
          </div>
        </form>
      </div>
    </section>

    <!-- Danger zone -->
    <section class="settings-section">
      <div class="section-heading danger-heading">
        <h2>Danger zone</h2>
        <p>These actions are irreversible. Please proceed with caution.</p>
      </div>
      <div class="card card-danger">
        <div class="danger-row">
          <div class="danger-text">
            <p class="danger-title">Delete account</p>
            <p class="danger-desc">Permanently removes your account, all workspaces, projects, tasks, and chat history.</p>
          </div>
          <button class="btn btn-danger" @click="confirmDelete = true">Delete account</button>
        </div>
      </div>
    </section>

    <!-- Delete confirmation modal -->
    <div v-if="confirmDelete" class="modal-overlay" @click.self="confirmDelete = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Delete account?</h2>
          <button class="modal-close" @click="confirmDelete = false">×</button>
        </div>
        <p class="modal-body-text">
          This will permanently delete your account and all associated data — workspaces, projects, tasks, and chat history. <strong>There is no way to undo this.</strong>
        </p>
        <p v-if="deleteError" class="form-error">{{ deleteError }}</p>
        <div class="form-actions">
          <button class="btn" @click="confirmDelete = false">Cancel</button>
          <button class="btn btn-danger" :disabled="deleteLoading" @click="handleDeleteAccount">
            <span v-if="deleteLoading" class="spinner spinner-danger"></span>
            {{ deleteLoading ? 'Deleting…' : 'Yes, delete my account' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const initials = computed(() => (auth.user?.username ?? '').slice(0, 2).toUpperCase())

// Profile form
const profileForm = ref({ username: '', email: '' })
const profileLoading = ref(false)
const profileError = ref<string | null>(null)
const profileSuccess = ref<string | null>(null)

function syncProfile() {
  if (!auth.user) return
  profileForm.value.username = auth.user.username
  profileForm.value.email = auth.user.email
}

onMounted(syncProfile)
watch(() => auth.user, syncProfile)

async function handleProfileSave() {
  profileError.value = null
  profileSuccess.value = null
  profileLoading.value = true
  try {
    await auth.updateProfile({
      username: profileForm.value.username || undefined,
      email: profileForm.value.email || undefined,
    })
    profileSuccess.value = 'Profile updated successfully.'
  } catch (e) {
    profileError.value = (e as Error).message
  } finally {
    profileLoading.value = false
  }
}

// Profile picture
const picLoading = ref(false)
const picError = ref<string | null>(null)
const picSuccess = ref<string | null>(null)

async function handlePicUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  picError.value = null
  picSuccess.value = null
  picLoading.value = true
  try {
    await auth.uploadProfilePicture(file)
    picSuccess.value = 'Photo updated.'
  } catch (err) {
    picError.value = (err as Error).message
  } finally {
    picLoading.value = false
  }
}

async function handlePicDelete() {
  picError.value = null
  picSuccess.value = null
  picLoading.value = true
  try {
    await auth.deleteProfilePicture()
    picSuccess.value = 'Photo removed.'
  } catch (err) {
    picError.value = (err as Error).message
  } finally {
    picLoading.value = false
  }
}

// Password form
const pwForm = ref({ current: '', next: '', confirm: '' })
const pwLoading = ref(false)
const pwError = ref<string | null>(null)
const pwSuccess = ref<string | null>(null)

async function handlePasswordSave() {
  pwError.value = null
  pwSuccess.value = null
  if (pwForm.value.next.length < 8) {
    pwError.value = 'New password must be at least 8 characters.'
    return
  }
  if (pwForm.value.next !== pwForm.value.confirm) {
    pwError.value = 'Passwords do not match.'
    return
  }
  pwLoading.value = true
  try {
    await auth.changePassword(pwForm.value.current, pwForm.value.next)
    pwSuccess.value = 'Password updated successfully.'
    pwForm.value = { current: '', next: '', confirm: '' }
  } catch (e) {
    pwError.value = (e as Error).message
  } finally {
    pwLoading.value = false
  }
}

// Delete account
const confirmDelete = ref(false)
const deleteLoading = ref(false)
const deleteError = ref<string | null>(null)

async function handleDeleteAccount() {
  deleteError.value = null
  deleteLoading.value = true
  try {
    await auth.deleteAccount()
    router.push('/login')
  } catch (e) {
    deleteError.value = (e as Error).message
    deleteLoading.value = false
  }
}
</script>

<style scoped>
.settings-page {
  max-width: 680px;
  margin: 0 auto;
  padding: 40px 32px 100px;
}

/* ── Page header ── */
.page-header {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 44px;
}

.header-avatar-img {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-full);
  object-fit: cover;
  border: 2.5px solid var(--border);
}

.header-avatar-fallback {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--primary) 0%, #003CBF 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 1px;
  flex-shrink: 0;
}

.page-header h1 {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.6px;
  color: var(--text);
  line-height: 1.2;
  margin-bottom: 3px;
}

.header-meta {
  font-size: 13.5px;
  color: var(--text-muted);
}

/* ── Section layout ── */
.settings-section {
  margin-bottom: 36px;
}

.section-heading {
  margin-bottom: 12px;
  padding-bottom: 0;
}

.section-heading h2 {
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: -0.1px;
  color: var(--text);
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 11px;
  color: var(--text-light);
}

.section-heading p {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
}

.danger-heading h2 {
  color: var(--danger) !important;
}

/* ── Card ── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  overflow: hidden;
}

.card-row {
  padding: 24px 28px;
}

.card-divider {
  height: 1px;
  background: var(--border);
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Danger card */
.card-danger {
  border-color: var(--danger-border);
  background: #fffafa;
}

/* ── Avatar ── */
.avatar-group {
  display: flex;
  align-items: center;
  gap: 18px;
  flex: 1;
}

.avatar-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.avatar-img {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-full);
  object-fit: cover;
  border: 2px solid var(--border);
  display: block;
}

.avatar-fallback {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--primary) 0%, #003CBF 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 1px;
}

.avatar-camera {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-full);
  background: rgba(10, 11, 13, 0.42);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  cursor: pointer;
  transition: opacity 0.15s;
}

.avatar-wrap:hover .avatar-camera {
  opacity: 1;
}

.avatar-camera.loading {
  opacity: 1;
}

.avatar-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.avatar-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.avatar-btns {
  display: flex;
  gap: 6px;
}

.text-danger {
  color: var(--danger) !important;
}

.feedback-inline {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* ── Danger row ── */
.danger-row {
  padding: 22px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.danger-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 3px;
}

.danger-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  max-width: 360px;
}

/* ── Feedback messages ── */
.inline-success {
  font-size: 13px;
  font-weight: 500;
  color: #047857;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  padding: 9px 13px;
  border-radius: 9px;
  margin-top: 2px;
}

.inline-error {
  font-size: 13px;
  font-weight: 500;
  color: var(--danger);
  background: var(--danger-bg);
  border: 1px solid var(--danger-border);
  padding: 9px 13px;
  border-radius: 9px;
  margin-top: 2px;
}

/* ── Modal ── */
.modal-body-text {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 24px;
}

/* ── Spinners ── */
.spinner {
  display: inline-block;
  width: 13px;
  height: 13px;
  border: 2px solid rgba(0,0,0,0.12);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.65s linear infinite;
  flex-shrink: 0;
}

.spinner-white {
  border-color: rgba(255,255,255,0.3);
  border-top-color: #fff;
}

.spinner-danger {
  border-color: rgba(207,32,47,0.18);
  border-top-color: var(--danger);
}

.spinner-sm {
  width: 11px;
  height: 11px;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Responsive ── */
@media (max-width: 600px) {
  .settings-page { padding: 24px 16px 80px; }
  .danger-row { flex-direction: column; align-items: flex-start; }
  .card-row { padding: 20px; }
}
</style>
