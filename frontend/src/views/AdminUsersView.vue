<template>
  <v-container>
    <h2>User Management</h2>

    <v-data-table :items="users" :headers="headers" item-value="id">
      <template #item.is_active="{ item }">
        <v-chip :color="item.is_active ? 'green' : 'red'" dark>
          {{ item.is_active ? 'Active' : 'Inactive' }}
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
  </v-container>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const users = ref([])
const headers = [
  { title: 'Name', value: 'username' },
  { title: 'E-Mail', value: 'email' },
  { title: 'Active', value: 'is_active' },
  { title: 'Admin', value: 'is_admin' },
  { title: 'Actions', value: 'actions', sortable: false },
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

const editUser = (user) => {
  alert(`Edit user: ${user.username}`)
}
</script>
