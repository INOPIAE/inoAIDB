<template>
  <v-app-bar app color="primary" dark>
    <v-app-bar-title>inoAIDB</v-app-bar-title>

    <v-spacer />

    <v-menu offset-y>
      <template #activator="{ props }">
        <v-btn
          v-bind="props"
          icon
          class="d-flex align-center"
          aria-label="Sprache wechseln"
        >
          <span :class="`fi fi-${currentFlag}`" style="font-size: 1.8rem;" />
        </v-btn>
      </template>

      <v-list>
        <v-list-item
          v-for="(lang, code) in languages"
          :key="code"
          @click="changeLanguage(code)"
        >
          <v-list-item-icon>
            <span :class="`fi fi-${lang.flag}`" style="font-size: 1.8rem;" />
          </v-list-item-icon>
          <v-list-item-title>{{ lang.label }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const languages = {
  en: { label: 'English', flag: 'gb' },
  de: { label: 'Deutsch', flag: 'de' },
}

const currentFlag = computed(() => {
  return languages[locale.value]?.flag || 'gb'
})

function changeLanguage(lang) {
  locale.value = lang
  localStorage.setItem('lang', lang)
}
</script>
