<template>
  <v-container>
    <v-row class="justify-space-between align-center mb-4">
      <v-col cols="12" md="6">
        <h2>{{ $t('applications') }}</h2>
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="selectedManufacturer"
          :items="manufacturerFilterItems"
          item-title="name"
          item-value="id"
          :label="$t('filterManufacturer')"
          clearable
        />
      </v-col>
      <v-col cols="auto" v-if="authStore.isAuthenticated">
        <v-btn color="primary" @click="openDialog()">{{ $t('new') }}</v-btn>
      </v-col>
    </v-row>

    <v-data-table
      :headers="visibleHeaders"
      :items="filteredApplications"
      item-value="id"
      class="elevation-1"
    >

      <template v-slot:item.is_active="{ item }" v-if="authStore.isAuthenticated">
        <span>{{ item.is_active ? $t('yes') : $t('no') }}</span>
      </template>
      <template v-if="authStore.isAuthenticated" v-slot:item.actions="{ item }">
        <v-btn @click="openDialog(item)" size="small" color="primary">
          {{ $t('edit') }}
        </v-btn>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-title>
          {{ form.id ? $t('editApplication') : $t('newApplication') }}
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="form.name" :label="$t('name')" />
          <v-textarea v-model="form.description" :label="$t('description')" />
          <v-select
            v-model="form.manufacturer_id"
            :items="manufacturers"
            item-title="name"
            item-value="id"
            :label="$t('manufacturer')"
          />
          <v-switch v-model="form.is_active" :label="$t('activeQuestion')" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="closeDialog()">{{ $t('cancel') }}</v-btn>
          <v-btn color="primary" @click="submit()">{{ $t('save') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const authStore = useAuthStore()

const applications = ref([])
const manufacturers = ref([])
const dialog = ref(false)
const selectedManufacturer = ref(null)

const headers = computed(() => [
  { title: t('name'), key: 'name' },
  { title: t('description'), key: 'description' },
  { title: t('manufacturer'), key: 'manufacturer_name' },
  { title: t('active'), key: 'is_active' },
  { title: t('actions'), key: 'actions', sortable: false },
])

const visibleHeaders = computed(() => {

  let base = [
    { title: t('name'), key: 'name' },
    { title: t('description'), key: 'description' },
    { title: t('manufacturer'), key: 'manufacturer_name' }
  ]

  if (authStore.isAuthenticated) {
    base.push({ title: t('active'), key: 'is_active' })
    base.push({ title: t('actions'), key: 'actions', sortable: false })
  }

  return base
})

const manufacturerFilterItems = computed(() => [
  { id: null, name: t('all') },
  ...manufacturers.value,
])

const filteredApplications = computed(() => {
  let apps = applications.value

  if (!authStore.isAuthenticated) {
    apps = apps.filter(app => app.is_active)
  }

  if (selectedManufacturer.value) {
    apps = apps.filter(app => app.manufacturer_id === selectedManufacturer.value)
  }

  return apps
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
