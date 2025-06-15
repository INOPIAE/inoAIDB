<template>
  <v-container>
    <v-row class="justify-space-between align-center mb-4">
      <v-col cols="12" md="6">
        <h2>Applications</h2>
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="selectedManufacturer"
          :items="manufacturerFilterItems"
          item-title="name"
          item-value="id"
          label="Filter manufacturer"
          clearable
        />
      </v-col>
      <v-col cols="auto" v-if="authStore.isAuthenticated">
        <v-btn color="primary" @click="openDialog()">Neu</v-btn>
      </v-col>
    </v-row>

    <v-data-table
      :headers="visibleHeaders"
      :items="filteredApplications"
      item-value="id"
      class="elevation-1"
    >
      <template v-slot:item.is_active="{ item }">
        <span>{{ item.is_active ? 'Ja' : 'Nein' }}</span>
      </template>

      <template v-if="authStore.isAuthenticated" v-slot:item.actions="{ item }">
        <v-btn @click="openDialog(item)" size="small" color="primary">Edit</v-btn>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-title>
          {{ form.id ? 'Edit application' : 'New application' }}
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="form.name" label="Name" />
          <v-textarea v-model="form.description" label="Description" />
          <v-select
            v-model="form.manufacturer_id"
            :items="manufacturers"
            item-title="name"
            item-value="id"
            label="Manufacturer"
          />
          <v-switch v-model="form.is_active" label="Active?" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="closeDialog()">Cancel</v-btn>
          <v-btn color="primary" @click="submit()">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const applications = ref([])
const manufacturers = ref([])
const dialog = ref(false)
const selectedManufacturer = ref(null)

const headers = [
  { title: 'Name', key: 'name' },
  { title: 'Description', key: 'description' },
  { title: 'Manufacturer', key: 'manufacturer_name' },
  { title: 'Active', key: 'is_active' },
  { title: 'Actions', key: 'actions', sortable: false },
]

const visibleHeaders = computed(() => {
  return authStore.isAuthenticated
    ? headers
    : headers.filter(h => h.key !== 'actions')
})

const manufacturerFilterItems = computed(() => [
  { id: null, name: 'All' },
  ...manufacturers.value,
])

const filteredApplications = computed(() => {
  if (!selectedManufacturer.value) return applications.value
  return applications.value.filter(app => app.manufacturer_id === selectedManufacturer.value)
})

const form = ref({
  id: null,
  name: '',
  description: '',
  manufacturer_id: null,
  is_active: true,
})

const loadApplications = async () => {
  const res = await axios.get('/api/applications/with-manufacturer')
  applications.value = res.data
}

const loadManufacturers = async () => {
  const res = await axios.get('/api/manufacturers')
  manufacturers.value = res.data
}

const openDialog = (item = null) => {
  if (item) {
    form.value = { ...item }
  } else {
    form.value = {
      id: null,
      name: '',
      description: '',
      manufacturer_id: null,
      is_active: true,
    }
  }
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
}

const submit = async () => {
  try {
    const config = { headers: authStore.authHeader }
    if (form.value.id) {
      await axios.put(`/api/applications/${form.value.id}`, form.value, config)
    } else {
      await axios.post('/api/applications', form.value, config)
    }
    await loadApplications()
    closeDialog()
  } catch (e) {
    console.error('Error while saving:', e)
  }
}

onMounted(() => {
  loadApplications()
  loadManufacturers()
})
</script>
