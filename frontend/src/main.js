import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import axios from 'axios'
import i18n from './i18n'
import 'flag-icons/css/flag-icons.min.css'

import vuetify from './plugins/vuetify'

axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL
axios.defaults.withCredentials = false

const app = createApp(App)

app.config.globalProperties.$axios = axios

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(i18n)

app.mount('#app')
