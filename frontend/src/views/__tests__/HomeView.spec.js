import { mount, flushPromises } from '@vue/test-utils'
import HomeView from '@/views/HomeView.vue'
import { createI18n } from 'vue-i18n'
import { nextTick } from 'vue'
import axios from 'axios'
import { vi } from 'vitest'

// Axios mocken
vi.mock('axios')

const messages = {
  en: {
    loading: 'Loading...',
    loadingError: 'Error loading data: {error}',
    appstats: '{count} active applications',
  },
}

function createWrapper(locale = 'en') {
  const i18n = createI18n({
    legacy: false,
    locale,
    messages,
  })

  return mount(HomeView, {
    global: {
      plugins: [i18n],
    },
  })
}

describe('HomeView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading initially', () => {
    const wrapper = createWrapper()
    expect(wrapper.text()).toContain('Loading...')
  })

it('shows application stats on successful load', async () => {
axios.get.mockResolvedValueOnce({
data: { total: 10, active: 7 },
})

const wrapper = createWrapper()

// Warte auf Axios und DOM-Update
await flushPromises()
await nextTick()

// Warte, bis loading verschwunden ist
await wrapper.vm.$nextTick()

// Debuggen (falls nötig)
console.log(wrapper.html())

expect(wrapper.text()).toContain('7 active applications')
})


  it('shows error message on failed load', async () => {
    axios.get.mockRejectedValueOnce({
      response: { data: { detail: 'Server error' } },
    })

    const wrapper = createWrapper()
    await flushPromises()
    await nextTick()

    expect(wrapper.text()).toContain('Error loading data: Server error')
  })

  it('shows generic error message if no response.detail', async () => {
    axios.get.mockRejectedValueOnce(new Error('Network error'))

    const wrapper = createWrapper()
    await flushPromises()
    await nextTick()

    expect(wrapper.text()).toContain('Error loading data: Network error')
  })
})
