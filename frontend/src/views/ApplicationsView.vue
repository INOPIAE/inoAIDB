<template>
  <v-container>
    <v-row class="justify-space-between align-center mb-4">
      <v-col cols="12" md="4">
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
      <v-col cols="12" md="4">
        <v-text-field
          v-model="searchText"
          :label="$t('searchApplications')"
          clearable
          dense
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="4" v-if="authStore.isAuthenticated">
        <v-btn color="primary" @click="saveChanges">{{ $t('saveSelection') }}</v-btn>
      </v-col>
      <v-col cols="12" md="4" v-if="authStore.isAuthenticated">
        <v-btn color="primary" @click="downloadCSV">{{ $t('exportCSV') }}</v-btn>
      </v-col>
      <v-col cols="12" md="4" class="text-right" v-if="authStore.user?.is_admin">
        <v-btn color="secondary" @click="openDialog()">{{ $t('new') }}</v-btn>
      </v-col>
    </v-row>

    <p v-if="loading">{{ t('loading') }}</p>
    <p v-else-if="error" class="text-red-600">{{ t('loadingError', { error }) }}</p>

    <v-data-table
      v-if="!loading && !error"
      :headers="visibleHeaders"
      :items="filteredApplications"
      item-value="id"
      class="elevation-1"
    >
      <template v-slot:item.modelchoice_name="{ item }">
        {{ $t('mc_' + item.modelchoice_name) }}
      </template>

      <template #item.applicationuser_selected="{ item }">
        <v-checkbox
          v-model="item.applicationuser_selected"
          :true-value="true"
          :false-value="false"
          hide-details
          density="compact"
        />
      </template>

      <template v-slot:item.risk_id="{ item }">
        <v-select
          v-model="item.risk_id"
          :items="risks"
          :item-title="translateRisk"
          item-value="id"
          dense
          hide-details
          style="max-width: 150px"
        />
      </template>

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
          <v-text-field v-model="form.name" :label="$t('name')" @input="checkForSimilarNames" />
          <div v-if="similarApplications.length > 0" class="mt-2">
          <v-alert type="warning" dense>
            {{ t('similarApplicationsFound') }}:
            <ul>
              <li v-for="m in similarApplications" :key="m.id">
                {{ m.name }}
              </li>
            </ul>
          </v-alert>
        </div>
          <v-textarea v-model="form.description" :label="$t('description')" />
          <v-select
            v-model="form.manufacturer_id"
            :items="manufacturers"
            :item-title="translateManufacturer"
            item-value="id"
            :label="$t('manufacturer')"
          />
          <v-select
            v-model="form.languagemodel_id"
            :items="languageModels"
            item-title="name"
            item-value="id"
            :label="$t('languageModel')"
          />
          <v-select
            v-model="form.modelchoice_id"
            :items="modelChoices"
            :item-title="translateModelChoice"
            item-value="id"
            :label="$t('modelChoice')"
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
const originalApplications = ref([])
const manufacturers = ref([])
const languageModels = ref([])
const modelChoices = ref([])
const risks = ref([])

const dialog = ref(false)
const selectedManufacturer = ref(null)
const searchText = ref('')

const loading = ref(false)
const error = ref(null)

const similarApplications = ref([])

const checkForSimilarNames = async () => {
  if (!form.value.name || form.value.name.length < 2) {
    similarApplications.value = []
    return
  }
  try {
    const res = await axios.get('/api/applications/search', {
      params: { q: form.value.name }
    })
    similarApplications.value = res.data.filter(
      m => m.id !== form.value.id
    )
  } catch (err) {
    console.error('Error similarity search', err)
  }
}


const visibleHeaders = computed(() => {
  let base = [
    { title: t('name'), key: 'name' },
    { title: t('description'), key: 'description' },
    { title: t('manufacturer'), key: 'manufacturer_name' },
    { title: t('languageModel'), key: 'languagemodel_name' },
    { title: t('modelChoice'), key: 'modelchoice_name' },
  ]
  if (authStore.isAuthenticated) {
    base.push({ title: t('selectedApp'), key: 'applicationuser_selected'})
    base.push({ title: t('risk'), key: 'risk_id'})
  }

  if (authStore.isAuthenticated && authStore.user?.is_admin) {
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

  if (searchText.value && searchText.value.trim().length > 0) {
    const search = searchText.value.trim().toLowerCase()
    apps = apps.filter(app => app.name.toLowerCase().includes(search))
  }

  return apps
})

const form = ref({
  id: null,
  name: '',
  description: '',
  manufacturer_id: null,
  languagemodel_id: null,
  modelchoice_id: null,
  is_active: true,
})

const loadApplications = async () => {
  loading.value = true
  error.value = null
  try {
    const url = authStore.isAuthenticated ? '/api/applications/with-manufacturer-user' : '/api/applications/with-manufacturer'
    const config = authStore.isAuthenticated ? { headers: authStore.authHeader } : {}
    const res = await axios.get(url, config)
    applications.value = res.data.map(app => ({ ...app }))
    originalApplications.value = res.data.map(app => ({ ...app }))
  } catch (e) {
    console.error('Error loading applications:', e)
    error.value = e.message || t('errorUnkown')
  } finally {
    loading.value = false
  }
}

const saveChanges = () => {
  const changed = applications.value.filter((app, idx) => {
    const original = originalApplications.value[idx]
    return (
      app.applicationuser_selected !== original?.applicationuser_selected ||
      app.risk_id !== original?.risk_id
    )
  })

  if (changed.length === 0) {
    alert(t('noChanges'))
    return
  }
  const config = { headers: authStore.authHeader }
  Promise.all(
    changed.map(app =>
      axios.post('/api/applications/application_selection', { application_id: app.id, selected: app.applicationuser_selected, risk_id: app.risk_id }, config)
    )
  )
    .then(() => {
      alert(t('saveSuccess'))
      originalApplications.value = applications.value.map(app => ({ ...app }))
    })
    .catch(err => {
      console.error('Save error:', err)
      alert(t('errorSaveFailed'))
    })
}

const downloadCSV = async () => {
  const config = {
    headers: authStore.authHeader,
    responseType: 'blob'
  }

  try {
    const response = await axios.get('/api/applications/export/csv', config)

    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'applications.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error(t('errorCSVFailed'), error)
    alert(t('errorCSVFailed'))
  }
}

const loadManufacturers = async () => {
  try {
    const res = await axios.get('/api/manufacturers')
    manufacturers.value = res.data
  } catch (e) {
    console.error('Error loading manufacturers:', e)
  }
}

const loadLanguageModels = async () => {
  try {
    const res = await axios.get('/api/languagemodels/')
    languageModels.value = res.data
  } catch (e) {
    console.error('Error loading language models:', e)
  }
}

const loadModelChoices = async () => {
  try {
    const res = await axios.get('/api/modelchoices/')
    modelChoices.value = res.data
  } catch (e) {
    console.error('Error loading model choices:', e)
  }
}

function translateModelChoice(item) {
  return t(`mc_${item.name}`) || item.name
}

function translateManufacturer(item) {
  return t(`${item.name}`) || item.name
}

function translateRisk(item) {
  return t(`r_${item.name}`) || item.name
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
      languagemodel_id: null,
      modelchoice_id: null,
      is_active: true,
    }
  }
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
}

const loadRisks = async () => {
  if (!authStore.isAuthenticated) return // nur für angemeldete Nutzer

  try {
    const res = await axios.get('/api/applications/risk')
    risks.value = res.data
  } catch (e) {
    console.error('Error loading risks:', e)
  }
}

const submit = async () => {
  try {
    const config = { headers: authStore.authHeader }
    form.value.languagemodel_id = Number(form.value.languagemodel_id)
    form.value.modelchoice_id = Number(form.value.modelchoice_id)
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
  loadLanguageModels()
  loadModelChoices()
  loadRisks()
})
</script>
