<template>
  <div class="p-8 text-center">
    <h1 class="text-2xl font-semibold mb-4">inoAIDB</h1>
    <p v-if="loading">{{ t('loading') }}</p>
    <p v-else-if="error" class="text-red-600">{{ t('loadingError', { error }) }}</p>
    <p v-else v-html="t('appstats', { count: stats.active })"></p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const stats = ref({ total: 0, active: 0 })
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const response = await axios.get('/api/applications/stats')
    stats.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
  } finally {
    loading.value = false
  }
})
</script>
