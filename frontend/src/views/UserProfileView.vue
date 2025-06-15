<template>
  <v-container>
    <h2>My Profile</h2>

    <v-card class="pa-4">
      <p><strong>Name:</strong> {{ user?.username }}</p>
      <p><strong>E-Mail:</strong> {{ user?.email }}</p>
      <p><strong>Active:</strong> {{ user?.is_active ? 'Yes' : 'No' }}</p>

      <v-divider class="my-4" />

      <h3>Change Password</h3>
      <v-text-field v-model="form.old_password" label="Old Password" type="password" />
      <v-text-field v-model="form.new_password" label="New Password" type="password" />
      <v-text-field v-model="form.totp" label="TOTP Code" />
      <v-btn @click="changePassword" color="primary">Change</v-btn>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const user = ref(null)
const form = ref({
  old_password: '',
  new_password: '',
  totp: '',
})

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
    alert('Password changed successfully')
    form.value = { old_password: '', new_password: '', totp: '' }
  } catch (e) {
    alert('Error: ' + e.response?.data?.detail)
  }
}
</script>