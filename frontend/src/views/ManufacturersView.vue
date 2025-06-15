<template>
  <div>
    <v-container>
      <v-row class="justify-space-between align-center mb-4">
        <v-col>
          <h2>Manufacturer</h2>
        </v-col>
        <v-col class="text-right">
          <v-btn v-if="authStore.isAuthenticated" @click="createItem" color="primary">New</v-btn>
        </v-col>
      </v-row>
      <v-table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Active</th>
            <th v-if="authStore.isAuthenticated">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in manufacturers" :key="m.id">
            <td>{{ m.name }}</td>
            <td>{{ m.description }}</td>
            <td>{{ m.is_active ? 'Yes' : 'No' }}</td>
            <td v-if="authStore.isAuthenticated">
              <v-btn @click="editItem(m)" size="small" color="primary">Edit</v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-container>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ t('editManfucturer') }}</span>
        </v-card-title>

        <v-card-text>
          <v-text-field v-model="editedItem.name" :label="t('name')" />
          <v-textarea v-model="editedItem.description" :label="t('description')" />
          <v-checkbox v-model="editedItem.is_active" :label="t('active')" />
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveManufacturer">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const manufacturers = ref([])
const dialog = ref(false)
const editedItem = ref({
  id: null,
  name: '',
  description: '',
  is_active: true
})


const fetchManufacturers = async () => {
  const res = await axios.get('/api/manufacturers')
  manufacturers.value = res.data
}

const saveManufacturer = async () => {
  if (!authStore.isAuthenticated || !authStore.token) {
    alert('You must be logged in.')
    return
  }

  const config = {
    headers: {
      Authorization: `Bearer ${authStore.token}`
    }
  }

  try {
    if (editedItem.value.id) {
      await axios.put(`/api/manufacturers/${editedItem.value.id}`, editedItem.value, config)
    } else {
      await axios.post('/api/manufacturers', editedItem.value, config)
    }
    dialog.value = false
    await fetchManufacturers()
  } catch (err) {
    console.error(err)
    alert('Fehler beim Speichern')
  }
}

const editItem = (item) => {
  editedItem.value = { ...item }
  dialog.value = true
}

const createItem = () => {
  editedItem.value = {
    id: null,
    name: '',
    description: '',
    is_active: true
  }
  dialog.value = true
}

onMounted(fetchManufacturers)
</script>

<style scoped>
.text-right {
  text-align: right;
}
</style>
