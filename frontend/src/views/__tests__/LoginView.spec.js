import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createI18n } from 'vue-i18n'
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import { nextTick } from 'vue'
import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import { VTextField, VBtn, VAlert, VContainer, VForm } from 'vuetify/components'

// Vuetify einrichten
const vuetify = createVuetify({
  components: {
    VTextField,
    VBtn,
    VAlert,
    VContainer,
    VForm
  }
})

// AuthStore mocken
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    login: vi.fn(() => Promise.resolve()),
    verifyOTP: vi.fn(() => Promise.resolve())
  }),
}))

// I18n
const messages = {
  en: {
    email: 'Email',
    password: 'Password',
    totpCode: 'TOTP Code',
    login: 'Login',
    forgotPassword: 'Reset Password',
    loginFailed: 'Login failed',
    resetLinkSent: 'Reset link sent',
    pleaseLoginToContinue: 'Please log in to continue',
    emailRequiredForReset: 'Email required to reset password'
  }
}

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages
})

// Router
const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/home', name: 'home', component: { template: '<div>Home</div>' } }]
})

// Factory-Funktion
function factory(routeQuery = {}) {
  router.push({ path: '/login', query: routeQuery })
  return mount(LoginView, {
    global: {
      plugins: [vuetify, i18n, createTestingPinia(), router]
    }
  })
}

// Test Suite
describe('LoginView.vue', () => {
  it('renders the login form', async () => {
    const wrapper = factory()
    await router.isReady()
    await nextTick()

    const fields = wrapper.findAllComponents(VTextField)
    expect(fields).toHaveLength(3)

    expect(fields[0].props('label')).toBe('Email')
    expect(fields[1].props('label')).toBe('Password')
    expect(fields[2].props('label')).toBe('TOTP Code')

    const buttons = wrapper.findAllComponents(VBtn)
    expect(buttons[0].text()).toContain('Login')
    expect(buttons[1].text()).toContain('Reset Password')
  })

  it('shows info message if redirected', async () => {
    const wrapper = factory({ redirect: '/home' })
    await router.isReady()
    await nextTick()

    expect(wrapper.text()).toContain('Please log in to continue')
  })

  it('logs in successfully and redirects', async () => {
    const wrapper = factory()
    await router.isReady()
    await nextTick()

    const fields = wrapper.findAllComponents(VTextField)
    await fields[0].vm.$emit('update:modelValue', 'user@example.com')
    await fields[1].vm.$emit('update:modelValue', 'secret')
    await fields[2].vm.$emit('update:modelValue', '123456')

    await wrapper.find('form').trigger('submit.prevent')
    await nextTick()

    expect(router.currentRoute.value.path).toBe('/home')
  })

  it('shows error message if login fails', async () => {
    const errorMsg = 'Invalid credentials'

    vi.mocked((await import('@/stores/auth')).useAuthStore).mockReturnValue({
      login: vi.fn(() => Promise.reject({ response: { data: { detail: errorMsg } } })),
      verifyOTP: vi.fn()
    })

    const wrapper = factory()
    await router.isReady()
    await nextTick()

    const fields = wrapper.findAllComponents(VTextField)
    await fields[0].vm.$emit('update:modelValue', 'wrong@example.com')
    await fields[1].vm.$emit('update:modelValue', 'wrongpass')
    await wrapper.find('form').trigger('submit.prevent')
    await nextTick()

    expect(wrapper.text()).toContain(errorMsg)
  })
})
