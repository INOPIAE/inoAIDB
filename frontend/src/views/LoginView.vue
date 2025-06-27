<template>
  <v-container>
    <v-form @submit.prevent="handleLogin">
      <v-alert v-if="infoMessage" type="info" class="mb-4">
        {{ t('pleaseLoginToContinue') }}
      </v-alert>

      <v-text-field :label="t('email')" v-model="email" />
      <v-text-field :label="t('password')" v-model="password" type="password" />
      <v-text-field :label="t('totpCode')" v-model="otp" />

      <v-btn type="submit" color="primary" class="mr-4">
        {{ t('login') }}
      </v-btn>

      <v-btn
        color="secondary"
        @click="requestPasswordReset"
      >
        {{ t('forgotPassword') }}
      </v-btn>

      <v-alert v-if="errorMessage" type="error" class="mt-4">
        {{ errorMessage }}
      </v-alert>

      <v-alert v-if="resetMessage" type="success" class="mt-4">
        {{ resetMessage }}
      </v-alert>
    </v-form>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const otp = ref('')
const errorMessage = ref('')
const infoMessage = ref('')
const resetMessage = ref('')

onMounted(() => {
  if (route.query.redirect) {
    infoMessage.value = true
  }
})

const handleLogin = async () => {
  try {
    await authStore.login(email.value, password.value, otp.value)
    await authStore.verifyOTP(email.value, otp.value)

    const redirect = route.query.redirect || '/home'
    router.push(redirect)
  } catch (err) {
    console.error('Login failed', err)
    if (err.response?.data?.detail) {
      errorMessage.value = err.response.data.detail
    } else {
      errorMessage.value = t('loginFailed')
    }
  }
}

const requestPasswordReset = async () => {
  errorMessage.value = ''
  resetMessage.value = ''

  if (!email.value) {
    errorMessage.value = t('emailRequiredForReset')
    return
  }

  try {
    const response = await axios.post('/api/auth/forgot-password', {
      email: email.value
    })
    resetMessage.value = t('resetLinkSent')
  } catch (err) {
    console.error('Password reset request failed', err)
    errorMessage.value = t('resetLinkSent')
  }
}
</script>
