<template>
  <v-container class="max-w-md mx-auto mt-10 p-6 bg-white rounded shadow">
    <h2 class="text-2xl font-bold mb-4">{{ $t('resetPasswordTitle') }}</h2>
    <v-form @submit.prevent="resetPassword">
      <v-text-field
        v-model="newPassword"
        :type="showPassword ? 'text' : 'password'"
        :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
        @click:append="showPassword = !showPassword"
        :rules="[v => !!v || $t('passwordRequired')]"
        :label="$t('newPassword')"
        required
      ></v-text-field>

      <v-btn type="submit" color="primary" class="mt-4">
        {{ $t('reset') }}
      </v-btn>

      <p v-if="message" class="mt-4 text-green-600">{{ message }}</p>
      <p v-if="error" class="mt-4 text-red-600">{{ error }}</p>
    </v-form>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const token = ref('')
const newPassword = ref('')
const message = ref('')
const error = ref('')
const showPassword = ref(false)

onMounted(() => {
  token.value = route.query.token || ''
})

const resetPassword = async () => {
  error.value = ''
  message.value = ''

  if (!token.value) {
    error.value = 'Invalid or missing token.'
    return
  }

  try {
    const response = await axios.post('/api/auth/reset-password', {
      token: token.value,
      new_password: newPassword.value
    })
    message.value = response.data.message

    setTimeout(() => {
      router.push('/login')
    }, 2000)

  } catch (err) {
    error.value = err.response?.data?.detail || 'An error occurred'
  }
}
</script>
