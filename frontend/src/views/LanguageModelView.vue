<template>
  <v-container>
    <v-row class="justify-space-between align-center mb-4">
      <v-col cols="6">
        <h1>{{ $t('languageModels') }}</h1>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-btn color="primary" @click="dialog = true">{{ $t('new') }}</v-btn>
      </v-col>
    </v-row>

    <v-data-table
      :headers="headers"
      :items="languageModels"
      :items-per-page="10"
      class="elevation-1"
    >
      <template #item.actions="{ item }">
        <v-btn icon @click="editModel(item)"><v-icon>mdi-pencil</v-icon></v-btn>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="500">
      <v-card>
        <v-card-title>
          <span class="headline">{{ editedModel.id ? $t('edit') : $t('create') }}</span>
        </v-card-title>

        <v-card-text>
          <v-text-field v-model="editedModel.name" :label="$t('name')" required />
          <v-textarea v-model="editedModel.description" :label="$t('description')" rows="3" />
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="blue darken-1" text @click="closeDialog">{{ $t('cancel') }}</v-btn>
          <v-btn color="blue darken-1" text @click="saveModel">{{ $t('save') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { computed } from 'vue'

const { t } = useI18n()
const dialog = ref(false)
const languageModels = ref([])
const editedModel = ref({ name: '', description: '' })

const headers = computed(() => [
  { text: t('name'), value: 'name' },
  { text: t('description'), value: 'description' },
  { text: t('actions'), value: 'actions', sortable: false }
])

const fetchModels = async () => {
  const response = await axios.get('/api/languagemodels/')
  languageModels.value = response.data
}

const saveModel = async () => {
  try {
    if (editedModel.value.id) {
      await axios.put(`/api/languagemodels/${editedModel.value.id}`, editedModel.value)
    } else {
      await axios.post('/api/languagemodels/', editedModel.value)
    }
    fetchModels()
    closeDialog()
  } catch (err) {
    console.error(err)
  }
}

const editModel = (model) => {
  editedModel.value = { ...model }
  dialog.value = true
}

const closeDialog = () => {
  dialog.value = false
  editedModel.value = { name: '', description: '' }
}

onMounted(fetchModels)
</script>

<style scoped>
.headline {
  font-weight: bold;
}
</style>
