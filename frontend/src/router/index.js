import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', redirect: '/profile' },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue'), meta: { guest: true } },
  { path: '/profile', name: 'profile', component: () => import('@/views/ProfileView.vue'), meta: { requiresAuth: true } },

  // Dahej inspection
  { path: '/plants', name: 'plants', component: () => import('@/views/dahej/PlantsView.vue'), meta: { requiresAuth: true } },
  { path: '/job-types', name: 'job-types', component: () => import('@/views/dahej/JobTypesView.vue'), meta: { requiresAuth: true } },
  { path: '/jobs', name: 'jobs', component: () => import('@/views/dahej/JobsView.vue'), meta: { requiresAuth: true } },
  { path: '/overtimes', name: 'overtimes', component: () => import('@/views/dahej/OverTimesView.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { next: to.fullPath } }
  }
  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'profile' }
  }
})

export default router
