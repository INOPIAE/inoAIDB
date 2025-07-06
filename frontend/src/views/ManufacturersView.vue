<template>
  <div>
    <v-container>
      <v-row class="justify-space-between align-center mb-4">
        <v-col cols="12" sm="6">
          <h2>{{ t('manufacturer') }}</h2>
        </v-col>
        <v-col cols="12" sm="6" class="text-right">
          <v-text-field
            v-model="search"
            :label="t('searchManufacturer')"
            class="mb-4"
            prepend-inner-icon="mdi-magnify"
            clearable
          />
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" class="text-right" v-if="authStore.user?.is_admin">
          <v-btn @click="createItem" color="secondary">
            {{ t('new') }}
          </v-btn>
        </v-col>
      </v-row>

      <v-data-table
        :headers="headers"
        :items="filteredManufacturers"
        :items-per-page="10"
        class="elevation-1"
      >
        <template #item.is_active="{ item }" v-if="authStore.user?.is_admin">
          {{ item.is_active ? t('yes') : t('no') }}
        </template>

        <template #item.actions="{ item }" v-if="authStore.user?.is_admin">
          <v-btn @click="editItem(item)" size="small" color="primary">
            {{ t('edit') }}
          </v-btn>
        </template>
      </v-data-table>
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
          <v-btn text @click="dialog = false">{{ t('cancel') }}</v-btn>
          <v-btn color="primary" @click="saveManufacturer">{{ t('save') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const authStore = useAuthStore()

const manufacturers = ref([])
const search = ref('')
const dialog = ref(false)

const editedItem = ref({
  id: null,
  name: '',
  description: '',
  is_active: true,
})

const headers = computed(() => {
  const base = [
    { title: t('name'), key: 'name' },
    { title: t('description'), key: 'description' }
  ]
  if (authStore.user?.is_admin) {
    base.push(
      { title: t('active'), key: 'is_active' },
      { title: t('actions'), key: 'actions', sortable: false }
    )
  }
  return base
})

const filteredManufacturers = computed(() => {
  if (!search.value) return manufacturers.value
  const lower = search.value.toLowerCase()
  return manufacturers.value.filter(m => m.name.toLowerCase().includes(lower))
})

const fetchManufacturers = async () => {
  const res = await axios.get('/api/manufacturers')
  manufacturers.value = res.data
}

const saveManufacturer = async () => {
  if (!authStore.isAuthenticated || !authStore.token) {
    alert(t('errorsNotLoggedIn'))
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
    alert(t('errorSaveFailed'))
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
