import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'


import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { de, en } from 'vuetify/locale'

const vuetify = createVuetify({components, directives,
//   theme: {
//     defaultTheme: 'dark',
//   },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
//   defaults: {
//     VBtn: {
//       color: '#AAAAAA',
//     },
//     VSelect: {
//       style: {
//         backgroundColor: '#AAAAAA',
//       },
//     },
//     VTextarea: {
//       style: {
//         backgroundColor: '#AAAAAA',
//       },
//     },
//     VTextField: {
//       style: {
//         backgroundColor: '#AAAAAA',
//       },
//     },
//   },
  locale: {
    locale: localStorage.getItem('lang') || 'de',
    fallback: 'en',
    messages: { de, en }
  }
})

export default vuetify

export { vuetify } 
