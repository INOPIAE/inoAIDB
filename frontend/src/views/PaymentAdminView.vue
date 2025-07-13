<template>
  <v-container>
    <v-row class="mb-4" align="center">
      <v-col cols="12" sm="6">
        <v-text-field
          :label="t('paymentDuration')"
          v-model="newTokenDuration"
          type="number"
          min="1"
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-btn color="primary" @click="createToken" :loading="loading">
          {{ t('create') }}
        </v-btn>
      </v-col>
    </v-row>

    <v-divider class="my-4" />

    <v-card>
      <v-card-title>{{ t('paymentActive_title') }}</v-card-title>
      <v-data-table
        :headers="headers"
        :items="tokens"
        :loading="loading"
        class="elevation-1"
        item-value="token"
      >
        <template #item.used_at="{ item }">
          {{ formatDate(item.used_at) }}
        </template>
        <template #no-data>
          <v-alert type="info">{{ t('paymentNo_data') }}</v-alert>
        </template>
      </v-data-table>
    </v-card>

    <v-snackbar v-model="snackbar" :timeout="-1" color="success" multi-line>
      <div>
        <p>{{ t('paymentCreated') }} <strong>{{ createdToken }}</strong></p>
        <qrcode-vue :value="tokenUrl" :size="128" />
        <p>
          {{ t('cannotScan') }}:
          <a :href="tokenUrl" target="_blank">{{ tokenUrl }}</a>
        </p>
      </div>
      <template #actions>
        <v-btn color="white" text @click="snackbar = false">
          {{ t('close') }}
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import QrcodeVue from 'qrcode.vue'

const { t } = useI18n()

const tokens = ref([])
const newTokenDuration = ref(12)
const loading = ref(false)

const snackbar = ref(false)
const createdToken = ref('')

const baseUrl = window.location.origin
const tokenUrl = computed(() =>
  createdToken.value ? `${baseUrl}/payment?token=${createdToken.value}` : ''
)

const headers = [
  { text: t('id'), value: 'id' },
  { text: t('token'), value: 'token' },
  { text: t('paymentDuration'), value: 'duration' },
  { text: t('user_id'), value: 'user_id' },
  { text: t('paymentUsed_at'), value: 'used_at' }
]

const fetchTokens = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/users/payments')
    tokens.value = response.data
  } catch (err) {
    console.error('Failed to load tokens', err)
  } finally {
    loading.value = false
  }
}

const createToken = async () => {
  if (newTokenDuration.value <= 0) return
  loading.value = true
  try {
    const response = await axios.post('/api/users/payments', {
      duration: newTokenDuration.value
    })
    tokens.value.unshift(response.data)
    createdToken.value = response.data.token
    snackbar.value = true
  } catch (err) {
    console.error('Failed to create token', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

onMounted(() => {
  fetchTokens()
})
</script>
