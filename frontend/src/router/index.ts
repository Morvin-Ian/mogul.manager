import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guest: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue'),
    meta: { guest: true },
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('../views/ResetPassword.vue'),
    meta: { guest: true },
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('../views/AuthCallback.vue'),
    meta: { guest: true },
  },
  {
    path: '/invitations/:token',
    name: 'InviteAccept',
    component: () => import('../views/InviteAccept.vue'),
  },
  {
    path: '/invite/:token',
    redirect: (to) => ({ path: `/invitations/${to.params.token}` }),
  },
  {
    path: '/',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/HomeView.vue'),
      },
      {
        path: 'workspaces',
        name: 'Workspaces',
        component: () => import('../views/WorkspaceDetail.vue'),
      },
      {
        path: 'workspaces/:id',
        name: 'WorkspaceDetail',
        component: () => import('../views/WorkspaceDetail.vue'),
      },
      {
        path: 'team',
        name: 'TeamHub',
        component: () => import('../views/TeamHub.vue'),
      },
      {
        path: 'team/:id',
        name: 'TeamManagement',
        component: () => import('../views/TeamManagement.vue'),
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('../views/ProjectsView.vue'),
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('../views/ProjectDetail.vue'),
      },
      {
        path: 'tasks/:id',
        name: 'TaskDetail',
        component: () => import('../views/TaskDetail.vue'),
      },
      {
        path: 'review',
        name: 'Review',
        component: () => import('../views/ReviewView.vue'),
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('../views/ChatView.vue'),
      },
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('../views/DocumentsView.vue'),
      },
      {
        path: 'documents/:id',
        name: 'DocumentDetail',
        component: () => import('../views/DocumentDetail.vue'),
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/ProfileSettings.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta?.requiresAuth && !auth.token) {
    next('/login')
  } else if (to.meta?.guest && auth.token) {
    next('/')
  } else {
    next()
  }
})

export default router
