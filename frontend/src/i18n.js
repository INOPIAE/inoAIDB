import { createI18n } from 'vue-i18n'

import de from './i18n/locales/de.js'
import en from './i18n/locales/en.js'

const messages = {
  de,
  en,
}

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('lang') || 'de',
  fallbackLocale: 'en',
  messages,
})

export default i18n
