<template>
  <v-footer app color="primary" dark>
    <v-container class="d-flex justify-space-between align-center">
      <div>
        <span v-if="authStore.isAuthenticated && authStore.user">
          Logged in as <strong>{{ authStore.user.username }}</strong>
        </span>
        <span v-else>
          Not logged in
        </span>
      </div>
      <div>
        &copy; {{ displayYear }} inoAIDB
      </div>
    </v-container>
  </v-footer>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const currentYear = new Date().getFullYear()
const displayYear = currentYear > 2025 ? `2025-${currentYear}` : '2025'
</script>
