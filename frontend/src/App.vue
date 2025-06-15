<template>
  <v-app>
    <HeaderBar />
    <SideNav />
    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>
    <FooterBar />
  </v-app>
</template>

<script setup>
import HeaderBar from './components/HeaderBar.vue'
import FooterBar from './components/FooterBar.vue'
import SideNav from './components/NavBar.vue'
</script>