<template>
  <v-container>
    <h2>{{ t('myProfile') }}</h2>

    <v-card class="pa-4">
      <p><strong>{{ t('name') }}:</strong> {{ user?.username }}</p>
      <p><strong>{{ t('email') }}:</strong> {{ user?.email }}</p>
      <p><strong>{{ t('active') }}:</strong> {{ user?.is_active ? t('yes') : t('no') }}</p>
      <p><strong>{{ t('expire') }}:</strong> {{ formatExpire(user?.expire) }}</p>

      <v-divider class="my-4" />

      <h3>{{ t('changePassword') }}</h3>
      <v-text-field v-model="form.old_password" :label="t('oldPassword')" type="password" />
      <v-text-field v-model="form.new_password" :label="t('newPassword')" type="password" />
      <v-text-field v-model="form.totp" :label="t('totpCode')" />
      <v-btn @click="changePassword" color="primary">{{ t('change') }}</v-btn>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { useFormat } from '@/composables/useFormat'

const { t } = useI18n()
const authStore = useAuthStore()
const user = ref(null)
const form = ref({
  old_password: '',
  new_password: '',
  totp: '',
})

const { formatExpire } = useFormat()

onMounted(async () => {
  const res = await axios.get(`/api/users/${authStore.user.id}`, {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  user.value = res.data
})

const changePassword = async () => {
  try {
    await axios.post('/api/users/creds/passwd', form.value, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    alert(t('passwordChangedSuccess'))
    form.value = { old_password: '', new_password: '', totp: '' }
  } catch (e) {
    alert(t('error') + ': ' + (e.response?.data?.detail || ''))
  }
}
</script>
