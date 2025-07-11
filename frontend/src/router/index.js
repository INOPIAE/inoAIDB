import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ManufacturersView from '@/views/ManufacturersView.vue'
import ApplicationsView from '@/views/ApplicationsView.vue'
import LoginView from '@/views/LoginView.vue'
import AdminUsersView from '@/views/AdminUsersView.vue'
import UserProfileView from '@/views/UserProfileView.vue'
import RegisterView from '@/views/RegisterView.vue'
import InviteView from '@/views/InviteView.vue'
import LanguageModelView from '@/views/LanguageModelView.vue'
import ResetPasswordView from '@/views/ResetPasswordView.vue'
import GeneralView from '@/views/GeneralView.vue'

import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const routes = [
  {
    path: '/hdocs/:catchAll(.*)*',
    beforeEnter: () => {
      window.location.href = window.location.pathname
    },
  },
  { path: '/', component: HomeView },
  { path: '/home', component: HomeView },
  { path: '/manufacturers', component: ManufacturersView },
  { path: '/applications', component: ApplicationsView },
  { path: '/login', component: LoginView },
  { path: '/adminusers', component: AdminUsersView, meta: { requiresAuth: true } },
  { path: '/userprofile', component: UserProfileView, meta: { requiresAuth: true } },
  { path: '/register', component: RegisterView },
  { path: '/invite', component: InviteView, meta: { requiresAuth: true } },
  { path: '/languagemodel', component: LanguageModelView, meta: { requiresAuth: true } },
  { path: '/reset-password', component: ResetPasswordView },
  { path: '/general/:page(about|dataprotection|imprint)', name: 'about', component: GeneralView, },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const { token } = storeToRefs(authStore)

  if (to.meta.requiresAuth && !token.value) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
