import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import axios from 'axios'

import vuetify from './plugins/vuetify'

axios.defaults.baseURL = 'http://localhost:8000'
axios.defaults.withCredentials = false

const app = createApp(App)

app.config.globalProperties.$axios = axios

app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')
