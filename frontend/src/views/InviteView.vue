<template>
  <v-container>
    <h2>{{ t('inviteTitle') }}</h2>

    <v-card class="pa-4 mb-6">
      <h3>{{ t('inviteCreateTitle') }}</h3>
      <v-text-field
        v-model="newInvite.code"
        :label="t('code')"
        placeholder="$t('optional')"
      />
      <v-text-field
        v-model.number="newInvite.use_max"
        :label="t('useMax')"
        type="number"
        min="1"
      />
      <v-btn @click="createInvite" color="primary">{{ t('create') }}</v-btn>
    </v-card>

    <v-card class="pa-4 mb-6">
      <h3>{{ t('inviteCheckTitle') }}</h3>
      <v-text-field
        v-model="checkCode"
        :label="t('code')"
      />
      <v-btn @click="checkInvite" color="info">{{ t('check') }}</v-btn>
      <p v-if="checkedUsesLeft !== null" class="mt-2">
        {{ t('usesLeft') }}: {{ checkedUsesLeft }}
      </p>
    </v-card>

    <v-card class="pa-4">
      <h3>{{ t('active') }}</h3>
      <v-data-table :items="invites" :headers="headers" item-value="code" />
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

const invites = ref([])
const newInvite = ref({ code: '', use_max: 1 })
const checkCode = ref('')
const checkedUsesLeft = ref(null)

const headers = [
  { title: t('code'), value: 'code' },
  { title: t('usesLeft'), value: 'use_left' },
]

const fetchInvites = async () => {
  const res = await axios.get('/api/auth/invite', {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  invites.value = res.data.invites
}

const createInvite = async () => {
  try {
    const res = await axios.post('/api/auth/invite', newInvite.value, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    alert(t('created') + ': ' + res.data.code)
    newInvite.value = { code: '', use_max: 1 }
    fetchInvites()
  } catch (err) {
    alert(t('error') + ': ' + (err.response?.data?.detail || err.message))
  }
}

const checkInvite = async () => {
  try {
    const res = await axios.get(`/api/auth/invite/${checkCode.value}`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    checkedUsesLeft.value = res.data.use_left
  } catch (err) {
    checkedUsesLeft.value = null
    alert(t('error') + ': ' + (err.response?.data?.detail || err.message))
  }
}

onMounted(() => {
  // Wenn nicht eingeloggt oder kein Admin, umleiten zum Login
  if (!authStore.user || !authStore.user.is_admin) {
    router.push('/login')
  } else {
    fetchInvites()
  }
})

</script>

<style scoped>
.mt-2 {
  margin-top: 16px;
}
.mb-6 {
  margin-bottom: 24px;
}
</style>
