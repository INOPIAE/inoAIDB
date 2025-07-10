<template>
  <v-container>
    <h2>{{ t('userManagement') }}</h2>

    <v-data-table :items="users" :headers="headers" item-value="id">
      <template #item.expire="{ item }">
        {{ formatExpire(item.expire) }}
      </template>
      <template #item.is_active="{ item }">
        <v-chip :color="item.is_active ? 'green' : 'red'" dark>
          {{ item.is_active ? t('active') : t('inactive') }}
        </v-chip>
      </template>

      <template #item.is_admin="{ item }">
        <v-icon color="primary" v-if="item.is_admin">mdi-shield-account</v-icon>
        <v-icon v-else>mdi-account</v-icon>
      </template>

      <template #item.actions="{ item }">
        <v-btn icon @click="editUser(item)">
          <v-icon>mdi-pencil</v-icon>
        </v-btn>
      </template>
    </v-data-table>
    <v-dialog v-model="editDialog" max-width="500px">
  <v-card>
  <v-card-title>{{ t('editUser') }}</v-card-title>
    <v-card-text>
      <v-text-field v-model="editedUser.username" :label="t('username')" />
      <v-text-field v-model="editedUser.email" :label="t('email')" />
      <v-text-field v-model="editedUser.expire" :label="t('expire')" />
      <v-switch v-model="editedUser.is_active" :label="t('activeLabel')" />
      <v-switch v-model="editedUser.is_admin" :label="t('admin')" />
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn text @click="editDialog = false">{{ t('cancel') }}</v-btn>
      <v-btn color="primary" @click="saveUser">{{ t('save') }}</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>

  </v-container>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { useFormat } from '@/composables/useFormat'

const { t, locale } = useI18n()
const authStore = useAuthStore()
const users = ref([])

const headers = [
  { title: t('name'), value: 'username' },
  { title: t('email'), value: 'email' },
  { title: t('expire'), value: 'expire' },
  { title: t('activeLabel'), value: 'is_active' },
  { title: t('admin'), value: 'is_admin' },
  { title: t('actions'), value: 'actions', sortable: false },
]

const fetchUsers = async () => {
  const res = await axios.get('/api/users', {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  users.value = res.data
}

onMounted(() => {
  if (authStore.user?.is_admin) {
    fetchUsers()
  }
})

const editDialog = ref(false)
const editedUser = ref({
  id: null,
  username: '',
  email: '',
  is_active: false,
  is_admin: false,
  expire: null,
})

const { formatExpire } = useFormat()

const editUser = (user) => {
  editedUser.value = { ...user }
  editDialog.value = true
}

const saveUser = async () => {
  try {
    await axios.put(`/api/users/${editedUser.value.id}`, editedUser.value, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    editDialog.value = false
    fetchUsers()
  } catch (err) {
    alert(t('errorSavingUser') + ': ' + (err.response?.data?.detail || err.message))
  }
}
</script>
