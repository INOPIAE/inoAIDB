import { config } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createI18n } from 'vue-i18n'
import { vi } from 'vitest'
import en from '@/i18n/locales/en.js'
import de from '@/i18n/locales/de.js'

// Globale Fetch-Mock
global.fetch = vi.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({}),
  })
)

// Vuetify-CSS-Dateien mocken
vi.mock('vuetify/lib/components/VCode/VCode.css', () => ({}))
vi.mock('vuetify/lib/styles/main.css', () => ({}))

config.global.stubs = {
  VApp: true,
  VAppBar: true,
  VMain: true,
  VContainer: true,
  VRow: true,
  VCol: true,
  VBtn: true,
  VDialog: true,
  VIcon: true,
  VTextField: true,
  VSelect: true,
  VSnackbar: true,
}

// i18n
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en, de },
})

// Globale Plugins einbinden
config.global.plugins = [
  createTestingPinia({ stubActions: false }),
  i18n,
]

afterEach(() => {
  vi.restoreAllMocks()
})
