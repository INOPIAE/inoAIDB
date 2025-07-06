import { mount } from '@vue/test-utils'
import NavBar from '@/components/NavBar.vue'
import { createTestingPinia } from '@pinia/testing'
import { useAuthStore } from '@/stores/auth'
import { createI18n } from 'vue-i18n'
import en from '@/i18n/locales/en.js'
import de from '@/i18n/locales/de.js'
import { createRouter, createWebHistory } from 'vue-router'
import { describe, it, expect, vi, beforeEach } from 'vitest'

const messages = {
  en,
  de
}


function cleanText(wrapper) {
  return wrapper.text().toLowerCase().replace(/\s/g, '')
}

function cleanTextString(text) {
  return text.toLowerCase().replace(/\s/g, '')
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/home', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/login', name: 'login', component: { template: '<div>Login</div>' } },
    { path: '/userprofile', name: 'userprofile', component: { template: '<div>User</div>' } },
    { path: '/register', name: 'register', component: { template: '<div>Register</div>' } },
  ],
})

// i18n
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages,
})

const t = i18n.global.t


describe('NavBar.vue', () => {
  let pinia
  let authStore

  beforeEach(() => {
    pinia = createTestingPinia({
      stubActions: false,
      createSpy: vi.fn,
    })
    authStore = useAuthStore()
    authStore.user = null
    authStore.isAuthenticated = false
  })

  function factory() {
    return mount(NavBar, {
      global: {
        plugins: [pinia, i18n, router],
      },
    })
  }

  it('renders public menu items', () => {
    const wrapper = factory()
    const text = cleanText(wrapper)
    expect(text).toContain('home')
    expect(text).toContain('login')
    expect(text).toContain('register')
    expect(text).not.toContain('logout')
  })

  it('shows logout and account when authenticated', () => {
    authStore.isAuthenticated = true
    const wrapper = factory()
    const text = cleanText(wrapper)
    expect(text).toContain('logout')
    expect(text).toContain('account')
    expect(text).not.toContain('login')
  })

  it('shows admin items when user is admin', () => {
    authStore.isAuthenticated = true
    authStore.user = { is_admin: true }
    const wrapper = factory()
    const text = cleanText(wrapper)

    expect(text).toContain(cleanTextString(t('administration')))
    expect(text).toContain(cleanTextString(t('invite')))
    expect(text).toContain(cleanTextString(t('userAdministration')))
  })

  it('calls logout function when logout clicked', async () => {
    authStore.isAuthenticated = true
    authStore.logout = vi.fn()
    const wrapper = factory()

    const logoutLink = wrapper.findAll('a, .router-link').find(node =>
      node.text().toLowerCase().includes('logout')
    )

    expect(logoutLink).toBeDefined()
    await logoutLink.trigger('click')
    expect(authStore.logout).toHaveBeenCalled()
  })

  it('renders external link to API docs', () => {
    const wrapper = factory()
    const externalLink = wrapper.find('a[href*="/docs"]')
    expect(externalLink.exists()).toBe(true)
    expect(externalLink.attributes('target')).toBe('_blank')
  })
})
