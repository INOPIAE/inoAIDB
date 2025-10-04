<template>
  <div id="swagger-ui"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import SwaggerUI from 'swagger-ui-dist/swagger-ui-es-bundle'
import 'swagger-ui-dist/swagger-ui.css'

const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

onMounted(() => {
  SwaggerUI({
    dom_id: '#swagger-ui',
    url: `${backendUrl}/openapi.json`,
  })
})
</script>
