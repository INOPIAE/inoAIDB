import { mount } from '@vue/test-utils'
import HeaderBar from '@/components/HeaderBar.vue'
import { createI18n } from 'vue-i18n'
import { nextTick } from 'vue'

const messages = {
  en: { footerText: '' },
  de: { footerText: '' },
}

function factory(locale = 'en') {
  const i18n = createI18n({
    legacy: false,
    locale,
    messages,
  })

  const wrapper = mount(HeaderBar, {
    global: {
      plugins: [i18n],
    },
  })

  // Wichtig: locale muss am global-Objekt gesetzt werden
  i18n.global.locale.value = locale

  return { wrapper, i18n }
}

describe('HeaderBar.vue', () => {
  it('shows current flag icon based on "en" locale', async () => {
    const { wrapper } = factory('en')
    await nextTick()
    const flagIcon = wrapper.find('span.fi')
    expect(flagIcon.exists()).toBe(true)
    expect(flagIcon.classes()).toContain('fi-gb') // 🇬🇧
  })

  it('shows current flag icon based on "de" locale', async () => {
    const { wrapper } = factory('de')
    await nextTick()
    const flagIcon = wrapper.find('span.fi')
    expect(flagIcon.exists()).toBe(true)
    expect(flagIcon.classes()).toContain('fi-de') // 🇩🇪
  })
})
