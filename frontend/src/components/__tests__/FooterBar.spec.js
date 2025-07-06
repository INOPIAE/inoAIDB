import { mount } from '@vue/test-utils'
import Footer from '@/components/FooterBar.vue'
import { createTestingPinia } from '@pinia/testing'
import { useAuthStore } from '@/stores/auth'
import { createI18n } from 'vue-i18n'
import en from '@/i18n/locales/en.js'
import de from '@/i18n/locales/de.js'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createVuetify } from 'vuetify'
import 'vuetify/styles'

const messages = { en, de }

const vuetify = createVuetify()

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages,
})

describe('Footer.vue', () => {
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
    return mount(Footer, {
      global: {
        plugins: [vuetify, pinia, i18n],
      },
    })
  }

  it('shows not logged in message if user is not authenticated', () => {
    const wrapper = factory()
    expect(wrapper.text().toLowerCase()).toContain(i18n.global.t('notLoggedIn').toLowerCase())
  })

  it('shows username when authenticated', () => {
    authStore.isAuthenticated = true
    authStore.user = { username: 'alice' }
    const wrapper = factory()
    expect(wrapper.html()).toContain('alice')
    expect(wrapper.html()).toContain(i18n.global.t('loggedInAs', { username: 'alice' }))
  })

  it('displays the project and company in the footer text', () => {
    const wrapper = factory()
    const year = new Date().getFullYear()
    const displayYear = year > 2025 ? `2025-${year}` : '2025'
    const powered = import.meta.env.VITE_POWEREDBY || 'Unknown'

    const expectedText = i18n.global.t('footerText', {
      project: 'inoAIDB',
      year: displayYear,
      company: 'INOPIAE',
      powered: powered,
    })

    expect(wrapper.text()).toContain(expectedText)
  })
})
