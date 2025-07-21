<template>
  <v-container>
    <h2>{{ pageTitle }}</h2>

    <p v-if="loading">{{ $t('loading') }}</p>

    <v-alert v-else-if="error" type="error" prominent>
    {{ $t('fileNotFound') }}: {{ fileName }}
    </v-alert>
    <iframe
      v-else
      :src="htmlPath"
      width="100%"
      height="600"
      style="border: none"
    ></iframe>

    <p v-if="pageKey === 'about'" class="mt-4 text-caption text-grey">
      {{ $t('currentVersionUsesCommit') }} {{ commit }} ({{ commitDate }})
    </p>
  </v-container>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { locale, t } = useI18n()
const route = useRoute()

const loading = ref(true)
const error = ref(null)

const pageKey = computed(() => route.params.page) 
const fileName = computed(() => `${pageKey.value}_${locale.value}.html`)
const htmlPath = computed(() => `/hdocs/${fileName.value}`)
const pageTitle = computed(() => t(`${pageKey.value}Title`))

const commit = __APP_COMMIT__;
const commitDate = __APP_COMMIT_DATE__;

onMounted(async () => {
  try {
     const response = await fetch(`/api/utils/page-exists?file=${encodeURIComponent(fileName.value)}`)
    if (!response.ok) throw new Error(`Status: ${response.status}`)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>
