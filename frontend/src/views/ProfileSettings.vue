<template>
  <div class="profile-page">

    <!-- Page heading -->
    <div class="profile-hdr">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
          <path d="M12 4L6 10l6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <h1 class="profile-hdr-title">My Profile</h1>
    </div>

    <div class="profile-grid">

      <!-- ── LEFT: Profile Card ── -->
      <aside class="profile-card">
        <!-- Avatar -->
        <div class="pc-avatar-wrap">
          <img v-if="auth.user?.profile_path" :src="auth.user.profile_path" class="pc-avatar-img" alt="Profile" />
          <div v-else class="pc-avatar-fallback">{{ initials }}</div>
          <label class="pc-camera-overlay" :class="{ loading: picLoading }" title="Change photo">
            <svg v-if="!picLoading" viewBox="0 0 20 20" fill="currentColor" width="17" height="17">
              <path fill-rule="evenodd" d="M4 5a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V7a2 2 0 00-2-2h-1.586a1 1 0 01-.707-.293l-1.121-1.121A2 2 0 0011.172 3H8.828a2 2 0 00-1.414.586L6.293 4.707A1 1 0 015.586 5H4zm6 9a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
            </svg>
            <span v-else class="spinner spinner-sm"></span>
            <input type="file" accept="image/*" @change="handlePicUpload" :disabled="picLoading" style="display:none" />
          </label>
        </div>

        <!-- Identity -->
        <div class="pc-identity">
          <h2 class="pc-name">{{ auth.user?.username }}</h2>
          <p class="pc-role">Member</p>
        </div>

        <!-- Status -->
        <div class="pc-status">
          <span class="status-dot"></span>
          <span class="status-label">Active now</span>
        </div>

        <!-- Quick action buttons -->
        <div class="pc-actions">
          <button class="pc-action-btn" title="Email" @click="scrollTo('info-section')">
            <svg viewBox="0 0 20 20" fill="none" width="17" height="17">
              <path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
              <path d="M2 5l8 6 8-6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="pc-action-btn" title="Edit profile" @click="scrollTo('info-section')">
            <svg viewBox="0 0 20 20" fill="none" width="17" height="17">
              <path d="M13.586 3.586a2 2 0 112.828 2.828L7 15.828 3 17l1.172-4L13.586 3.586z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="pc-action-btn" title="Security" @click="scrollTo('security-section')">
            <svg viewBox="0 0 20 20" fill="none" width="17" height="17">
              <path d="M5 9V7a5 5 0 0110 0v2M4 9h12a1 1 0 011 1v7a1 1 0 01-1 1H4a1 1 0 01-1-1v-7a1 1 0 011-1z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="pc-action-btn" title="Danger zone" @click="scrollTo('danger-section')">
            <svg viewBox="0 0 20 20" fill="none" width="17" height="17">
              <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM10 7v4M10 13h.01" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>

        <!-- Remove photo -->
        <button
          v-if="auth.user?.profile_path"
          class="pc-remove-photo"
          :disabled="picLoading"
          @click="handlePicDelete"
        >
          Remove photo
        </button>

        <!-- Pic feedback -->
        <p v-if="picError" class="pc-feedback error">{{ picError }}</p>
        <p v-if="picSuccess" class="pc-feedback success">{{ picSuccess }}</p>
      </aside>

      <!-- ── RIGHT: Settings panels ── -->
      <div class="settings-panels">

        <!-- Detailed Information -->
        <div class="settings-card" id="info-section">
          <h3 class="settings-card-title">Detailed Information</h3>

          <div class="info-rows">
            <div class="info-row">
              <span class="info-dot"></span>
              <div class="info-content">
                <span class="info-label">Full Name</span>
                <span class="info-value">{{ auth.user?.username }}</span>
              </div>
              <span class="online-badge">Online</span>
            </div>
            <div class="info-row">
              <span class="info-dot"></span>
              <div class="info-content">
                <span class="info-label">Email Address</span>
                <span class="info-value">{{ auth.user?.email }}</span>
              </div>
              <button class="info-icon-btn" title="Edit email">
                <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
                  <path d="M1 3a1 1 0 011-1h12a1 1 0 011 1v9a1 1 0 01-1 1H2a1 1 0 01-1-1V3z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
                  <path d="M1 3l7 5 7-5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
            <div class="info-row">
              <span class="info-dot"></span>
              <div class="info-content">
                <span class="info-label">Account Type</span>
                <span class="info-value">Free Member</span>
              </div>
              <button class="info-icon-btn" title="Info">
                <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
                  <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.4"/>
                  <path d="M8 7v4M8 5h.01" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
            <div class="info-row no-border">
              <span class="info-dot"></span>
              <div class="info-content">
                <span class="info-label">Google Linked</span>
                <span class="info-value">{{ auth.user?.google_id ? 'Yes' : 'Not linked' }}</span>
              </div>
              <button class="info-icon-btn" title="Account">
                <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
                  <circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.4"/>
                  <path d="M2 14c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="card-sep"></div>

          <!-- Edit form -->
          <form @submit.prevent="handleProfileSave" novalidate class="edit-form">
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
            <div class="form-footer">
              <button type="submit" class="btn btn-primary" :disabled="profileLoading">
                <span v-if="profileLoading" class="spinner spinner-white"></span>
                {{ profileLoading ? 'Saving…' : 'Save changes' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Security / Password -->
        <div class="settings-card" id="security-section">
          <h3 class="settings-card-title">Security</h3>
          <div class="info-rows">
            <div class="info-row no-border">
              <span class="info-dot"></span>
              <div class="info-content">
                <span class="info-label">Password</span>
                <span class="info-value">Update your account password</span>
              </div>
              <button class="info-icon-btn" title="Change password">
                <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
                  <path d="M4 7V5a4 4 0 118 0v2M3 7h10a1 1 0 011 1v6a1 1 0 01-1 1H3a1 1 0 01-1-1V8a1 1 0 011-1z" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="card-sep"></div>
          <form @submit.prevent="handlePasswordSave" novalidate class="edit-form">
            <div class="form-group">
              <label for="current-pw">Current password</label>
              <input id="current-pw" v-model="pwForm.current" type="password" autocomplete="current-password" placeholder="Enter current password" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="new-pw">New password</label>
                <input id="new-pw" v-model="pwForm.next" type="password" autocomplete="new-password" placeholder="At least 8 characters" minlength="8" />
              </div>
              <div class="form-group">
                <label for="confirm-pw">Confirm password</label>
                <input id="confirm-pw" v-model="pwForm.confirm" type="password" autocomplete="new-password" placeholder="Repeat new password" />
              </div>
            </div>
            <p v-if="pwError" class="form-error">{{ pwError }}</p>
            <p v-if="pwSuccess" class="inline-success">{{ pwSuccess }}</p>
            <div class="form-footer">
              <button type="submit" class="btn btn-primary" :disabled="pwLoading">
                <span v-if="pwLoading" class="spinner spinner-white"></span>
                {{ pwLoading ? 'Updating…' : 'Update password' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Danger Zone -->
        <div class="settings-card settings-card-danger" id="danger-section">
          <h3 class="settings-card-title danger-title">Danger Zone</h3>
          <div class="danger-row">
            <div>
              <p class="danger-row-title">Delete account</p>
              <p class="danger-row-desc">Permanently removes your account, workspaces, projects, tasks and chat history.</p>
            </div>
            <button class="btn-delete" @click="confirmDelete = true">Delete account</button>
          </div>
        </div>

      </div>
    </div>

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

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

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
  if (pwForm.value.next.length < 8) { pwError.value = 'New password must be at least 8 characters.'; return }
  if (pwForm.value.next !== pwForm.value.confirm) { pwError.value = 'Passwords do not match.'; return }
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
.profile-page {
  padding: 32px 36px 80px;
  min-height: 100%;
}

/* ── Page heading ── */
.profile-hdr {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 32px;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1.5px solid var(--border);
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text);
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
  flex-shrink: 0;
}
.back-btn:hover { background: var(--bg); border-color: var(--border-strong); }

.profile-hdr-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.5px;
}

/* ── Two-column layout ── */
.profile-grid {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 20px;
  align-items: start;
}

/* ── LEFT: Profile card ── */
.profile-card {
  background: #fff;
  border-radius: 20px;
  border: 1.5px solid var(--border);
  box-shadow: 0 2px 16px rgba(10,11,13,0.07);
  padding: 28px 24px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  position: sticky;
  top: 24px;
}

/* Avatar */
.pc-avatar-wrap {
  position: relative;
  width: 88px;
  height: 88px;
  flex-shrink: 0;
}

.pc-avatar-img {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 0 0 3px var(--border);
  display: block;
}

.pc-avatar-fallback {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ECEBF5 0%, #C2BEE0 100%);
  color: #4A4676;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: 1px;
  border: 3px solid #fff;
  box-shadow: 0 0 0 3px var(--border);
}

.pc-camera-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(10,11,13,0.48);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  cursor: pointer;
  transition: opacity 0.15s;
}
.pc-avatar-wrap:hover .pc-camera-overlay,
.pc-camera-overlay.loading { opacity: 1; }

/* Identity */
.pc-identity {
  text-align: center;
}

.pc-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
  margin-bottom: 3px;
}

.pc-role {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 400;
}

/* Status */
.pc-status {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #EBF5EC;
  border: 1px solid #B4D4BA;
  border-radius: 999px;
  padding: 5px 12px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #285830;
  flex-shrink: 0;
}

.status-label {
  font-size: 12px;
  font-weight: 600;
  color: #285830;
}

/* Action buttons */
.pc-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.pc-action-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1.5px solid var(--border);
  background: var(--bg);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s, color 0.12s;
}
.pc-action-btn:hover {
  background: #ECEBF5;
  border-color: #C2BEE0;
  color: #4A4676;
}

/* Remove photo */
.pc-remove-photo {
  background: none;
  border: none;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-light);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.12s, color 0.12s;
  font-family: inherit;
}
.pc-remove-photo:hover { background: #F5ECEC; color: #682828; }

.pc-feedback {
  font-size: 12.5px;
  font-weight: 500;
  padding: 7px 12px;
  border-radius: 8px;
  width: 100%;
  text-align: center;
}
.pc-feedback.error   { background: #F5ECEC; color: #682828; border: 1px solid #D8BCBC; }
.pc-feedback.success { background: #EBF5EC; color: #285830; border: 1px solid #B4D4BA; }

/* ── RIGHT: Settings panels ── */
.settings-panels {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.settings-card {
  background: #fff;
  border-radius: 18px;
  border: 1.5px solid var(--border);
  box-shadow: 0 2px 12px rgba(10,11,13,0.06);
  overflow: hidden;
}

.settings-card-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
  padding: 20px 24px 14px;
}

/* Info rows */
.info-rows { display: flex; flex-direction: column; }

.info-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 13px 24px;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.info-row:hover { background: var(--bg); }
.info-row.no-border { border-bottom: none; }

.info-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--border-strong);
  flex-shrink: 0;
}

.info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.info-label {
  font-size: 11.5px;
  color: var(--text-light);
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.online-badge {
  flex-shrink: 0;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
  background: #EBF5EC;
  color: #285830;
  border: 1px solid #B4D4BA;
}

.info-icon-btn {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1.5px solid var(--border);
  background: #fff;
  color: var(--text-light);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s, color 0.12s;
}
.info-icon-btn:hover {
  background: #ECEBF5;
  border-color: #C2BEE0;
  color: #4A4676;
}

/* Separator */
.card-sep {
  height: 1px;
  background: var(--border);
  margin: 0 24px;
}

/* Edit forms */
.edit-form {
  padding: 20px 24px 24px;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

/* Override primary button to match homepage dark button style */
.edit-form .btn-primary {
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  padding: 9px 20px;
  box-shadow: none;
  text-shadow: none;
  letter-spacing: 0;
}
.edit-form .btn-primary:hover:not(:disabled) {
  background: #2e2e30;
  box-shadow: none;
}
.edit-form .btn-primary:active:not(:disabled) {
  background: #111113;
}

/* Danger card */
.settings-card-danger {
  border-color: #D8BCBC;
  background: #FDFAF9;
}

.danger-title { color: #682828 !important; }

.danger-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 0 24px 22px;
}

.danger-row-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 3px;
}

.danger-row-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  max-width: 340px;
}

.btn-delete {
  flex-shrink: 0;
  padding: 9px 20px;
  background: #F5DEDE;
  color: #601010;
  border: 1.5px solid #CC8888;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.btn-delete:hover { background: #D07878; color: #fff; border-color: #D07878; }

/* Feedback */
.inline-success {
  font-size: 13px;
  font-weight: 500;
  color: #285830;
  background: #EBF5EC;
  border: 1px solid #B4D4BA;
  padding: 9px 13px;
  border-radius: 9px;
  margin-top: 8px;
}

/* Modal buttons — match homepage rounded pill style */
.modal .btn {
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  padding: 9px 20px;
}
.modal .btn-danger {
  background: #D07878;
  color: #fff;
  border-color: #D07878;
  box-shadow: none;
}
.modal .btn-danger:hover:not(:disabled) {
  background: #B85050;
  border-color: #B85050;
  box-shadow: none;
}

/* Modal */
.modal-body-text {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 24px;
}

/* Spinners */
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
.spinner-white { border-color: rgba(255,255,255,0.3); border-top-color: #fff; }
.spinner-danger { border-color: rgba(104,40,40,0.18); border-top-color: #682828; }
.spinner-sm { width: 11px; height: 11px; }

@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 860px) {
  .profile-grid { grid-template-columns: 1fr; }
  .profile-card { position: static; flex-direction: row; flex-wrap: wrap; justify-content: flex-start; text-align: left; padding: 20px; }
  .pc-identity { text-align: left; }
}
@media (max-width: 600px) {
  .profile-page { padding: 20px 16px 60px; }
}
</style>
