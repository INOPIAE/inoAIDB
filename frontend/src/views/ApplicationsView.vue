<template>
  <v-container>
    <v-row class="justify-space-between align-center mb-4">
      <v-col cols="12" md="6">
        <h2>{{ $t('applications') }}</h2>
      </v-col>
      <v-col cols="12" md="2" v-if="authStore.isAuthenticated">
        <v-btn color="primary" @click="saveChanges">{{ $t('saveSelection') }}</v-btn>
      </v-col>
      <v-col cols="12" md="2" v-if="authStore.isAuthenticated">
        <v-btn color="primary" @click="downloadCSV">{{ $t('exportCSV') }}</v-btn>
      </v-col>
      <v-col cols="12" md="2" class="text-right" v-if="authStore.user?.is_admin">
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
      <template v-slot:header.name>
        <div>
          {{ t('name') }}
          <v-text-field
            v-model="filterName"
            dense
            hide-details
            placeholder="Filter"
            clearable
          />
        </div>
      </template>

      <template v-slot:header.manufacturer_name>
        <div>
          {{ t('manufacturer') }}
          <v-select
            v-model="filterManufacturer"
            :items="manufacturers"
            :item-title="translateManufacturer"
            item-value="id"
            dense
            clearable
            hide-details
            placeholder="Filter"
          />
        </div>
      </template>

      <template v-slot:header.languagemodel_name>
        <div>
          {{ t('languageModel') }}
          <v-select
            v-model="filterLanguageModel"
            :items="languageModels"
            :item-title="translateLanguageModel"
            item-value="id"
            dense
            clearable
            hide-details
            placeholder="Filter"
          />
        </div>
      </template>
      <template v-slot:header.modelchoice_name>
        <div>
          {{ t('modelChoice') }}
          <v-select
            v-model="filterModelChoice"
            :items="modelChoices"
            :item-title="translateModelChoice"
            item-value="id"
            dense
            clearable
            hide-details
            placeholder="Filter"
          />
        </div>
      </template>
      <template v-slot:header.area_ids>
        <div>
          {{ t('areas') }}
          <v-select
            v-model="filterArea"
            :items="areas"
            item-title="area"
            item-value="id"
            dense
            clearable
            hide-details
            placeholder="Filter"
            multiple
            chips
          />
        </div>
      </template>

      <template v-slot:header.applicationuser_selected>
        <div>
          {{ t('selectedApp') }}
          <v-select
            v-model="filterSelectedApp"
            :items="[{ id: null, name: t('all') }, { id: true, name: t('yes') }, { id: false, name: t('no') }]"
            item-title="name"
            item-value="id"
            dense
            clearable
            hide-details
            placeholder="Filter"
          />
        </div>
      </template>
      <template v-slot:header.risk_id>
        <div>
          {{ t('risk') }}
          <v-select
            v-model="filterRisk"
            :items="risks"
            :item-title="translateRisk"
            item-value="id"
            dense
            clearable
            hide-details
            placeholder="Filter"
          />
        </div>
      </template>
      <template v-if="authStore.isAuthenticated" v-slot:header.is_active>
        <div>
          {{ t('active') }}
          <v-select
            v-model="filterActive"
            :items="[{ id: null, name: t('all') }, { id: true, name: t('yes') }, { id: false, name: t('no') }]"
            item-title="name"
            item-value="id"
            dense
            clearable
            hide-details
            placeholder="Filter"
          />
        </div>
      </template>

      <template #item.description="{ item }">
        <div v-html="sanitizedDescriptions.get(item.id)" />
      </template>

      <template #item.manufacturer_name="{ item }">
        {{ $t(item.manufacturer_name) }}
      </template>

      <template #item.languagemodel_name="{ item }">
        {{ $t(item.languagemodel_name) }}
      </template>

      <template #item.modelchoice_name="{ item }">
        {{ $t('mc_' + item.modelchoice_name) }}
      </template>

      <template #item.area_ids="{ item }">
        <span v-if="item.areas && item.areas.length">
          {{ item.areas
            .map(a => {
              const key = 'a_' + (a?.area ?? '')
              const translation = $t(key)

              return translation === key ? a.area : translation
            })
            .join(', ')
          }}
        </span>
        <span v-else>
          {{ $t('none') }}
        </span>
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

      <template #item.risk_id="{ item }">
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

      <template v-if="authStore.isAuthenticated" #item.is_active="{ item }">
        <span>{{ item.is_active ? $t('yes') : $t('no') }}</span>
      </template>

      <template v-if="authStore.isAuthenticated" #item.actions="{ item }">
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
          <v-select
            v-model="form.area_ids"
            :items="areas"
            item-title="area"
            item-value="id"
            :label="$t('areas')"
            multiple
            chips
            clearable
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
import { useSanitizedHtml } from '@/composables/useSanitizedHtml'

const { t } = useI18n()
const authStore = useAuthStore()

const applications = ref([])
const originalApplications = ref([])
const manufacturers = ref([])
const languageModels = ref([])
const modelChoices = ref([])
const areas = ref([])
const risks = ref([])

const dialog = ref(false)
const similarApplications = ref([])
const sanitizedDescriptions = new Map()

const filterName = ref('')
const filterManufacturer = ref(null)
const filterLanguageModel = ref(null)
const filterModelChoice = ref(null)
const filterArea = ref([])
const filterSelectedApp = ref(null)
const filterRisk = ref(null)
const filterActive = ref(null)

const form = ref({
  id: null,
  name: '',
  description: '',
  manufacturer_id: null,
  languagemodel_id: null,
  modelchoice_id: null,
  is_active: true,
  area_ids: [],
})

const loading = ref(false)
const error = ref(null)

const visibleHeaders = computed(() => {
  let base = [
    { title: t('name'), key: 'name' },
    { title: t('description'), key: 'description' },
    { title: t('manufacturer'), key: 'manufacturer_name' },
    { title: t('languageModel'), key: 'languagemodel_name' },
    { title: t('modelChoice'), key: 'modelchoice_name' },
    { title: t('areas'), value: 'area_ids' },
  ]
  if (authStore.isAuthenticated) {
    base.push({ title: t('selectedApp'), key: 'applicationuser_selected' })
    base.push({ title: t('risk'), key: 'risk_id' })
  }
  if (authStore.isAuthenticated && authStore.user?.is_admin) {
    base.push({ title: t('active'), key: 'is_active' })
    base.push({ title: t('actions'), key: 'actions', sortable: false })
  }
  return base
})

const filteredApplications = computed(() => {
  let apps = applications.value
  if (!authStore.isAuthenticated) {
    apps = apps.filter(app => app.is_active)
  }

  if (filterName.value && filterName.value.trim() !== '') {
    const search = filterName.value.trim().toLowerCase()
    apps = apps.filter(app => app.name.toLowerCase().includes(search))
  }

  if (filterManufacturer.value) {
    apps = apps.filter(app => app.manufacturer_id === filterManufacturer.value)
  }

  if (filterLanguageModel.value) {
    apps = apps.filter(app => app.languagemodel_id === filterLanguageModel.value)
  }

  if (filterModelChoice.value) {
    apps = apps.filter(app => app.modelchoice_id === filterModelChoice.value)
  }

  if (filterArea.value && filterArea.value.length > 0) {
    apps = apps.filter(app =>
      app.areas?.some(area => filterArea.value.includes(area.id))
    )
  }

  if (filterSelectedApp.value !== null) {
    apps = apps.filter(app => app.applicationuser_selected === filterSelectedApp.value)
  }

  if (filterRisk.value) {
    apps = apps.filter(app => app.risk_id === filterRisk.value)
  }

  if (filterActive.value !== null) {
    apps = apps.filter(app => app.is_active === filterActive.value)
  }

  return apps
})

const loadApplications = async () => {
  loading.value = true
  error.value = null
  try {
    const url = authStore.isAuthenticated
      ? '/api/applications/with-manufacturer-user'
      : '/api/applications/with-manufacturer'
    const config = authStore.isAuthenticated ? { headers: authStore.authHeader } : {}
    const res = await axios.get(url, config)
    applications.value = res.data.map(app => ({ ...app }))
    originalApplications.value = res.data.map(app => ({ ...app }))

    sanitizedDescriptions.clear()
    applications.value.forEach((item) => {
      const textRef = ref(item.description)
      const { sanitizedHtml } = useSanitizedHtml(textRef)
      sanitizedDescriptions.set(item.id, sanitizedHtml.value)
    })
  } catch (e) {
    console.error('Error loading applications:', e)
    error.value = e.message || t('errorUnknown')
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
      axios.post('/api/applications/application_selection', {
        application_id: app.id,
        selected: app.applicationuser_selected,
        risk_id: app.risk_id,
      }, config)
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
    responseType: 'blob',
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

const checkForSimilarNames = async () => {
  if (!form.value.name || form.value.name.length < 2) {
    similarApplications.value = []
    return
  }
  try {
    const res = await axios.get('/api/applications/search', {
      params: { q: form.value.name }
    })
    similarApplications.value = res.data.filter(m => m.id !== form.value.id)
  } catch (err) {
    console.error('Error similarity search', err)
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

const loadAreas = async () => {
  try {
    const res = await axios.get('/api/applications/areas/')
    areas.value = res.data
  } catch (e) {
    console.error('Error loading areas:', e)
  }
}

const loadRisks = async () => {
  if (!authStore.isAuthenticated) return
  try {
    const res = await axios.get('/api/applications/risk')
    risks.value = res.data
  } catch (e) {
    console.error('Error loading risks:', e)
  }
}

const translateModelChoice = (item) => t(`mc_${item.name}`) || item.name
const translateManufacturer = (item) => t(item.name) || item.name
const translateLanguageModel = (item) => t(item.name) || item.name
const translateRisk = (item) => t(`r_${item.name}`) || item.name

const openDialog = (item = null) => {
  form.value = item
    ? {
        ...item,
        area_ids: item.areas?.map(area => area.id) || [],
      }
    : {
        id: null,
        name: '',
        description: '',
        manufacturer_id: null,
        languagemodel_id: null,
        modelchoice_id: null,
        is_active: true,
        area_ids: [],
      }
  dialog.value = true
}


const closeDialog = () => {
  dialog.value = false
}

const submit = async () => {
  try {
    const config = { headers: authStore.authHeader }
    form.value.manufacturer_id = Number(form.value.manufacturer_id)
    form.value.languagemodel_id = Number(form.value.languagemodel_id)
    form.value.modelchoice_id = Number(form.value.modelchoice_id)
    form.value.area_ids = form.value.area_ids.map(Number)
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


console.log(applications.value)
console.log(areas.value)

onMounted(() => {
  loadApplications()
  loadManufacturers()
  loadLanguageModels()
  loadModelChoices()
  loadRisks()
  loadAreas()
})

</script>
