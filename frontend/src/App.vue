<template>
  <v-app>
    <HeaderBar @toggle-drawer="drawer = !drawer" />
    <SideNav :drawer="drawer" @update:drawer="drawer = $event" />
    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>
    <FooterBar />
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import HeaderBar from './components/HeaderBar.vue'
import FooterBar from './components/FooterBar.vue'
import SideNav from './components/NavBar.vue'

const drawer = ref(false)
</script>
