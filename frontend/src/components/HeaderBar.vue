<template>
  <v-app-bar app color="primary" dark>
    <v-app-bar-nav-icon @click="$emit('toggle-drawer')" />

    <v-app-bar-title>inoAIDB</v-app-bar-title>

    <v-spacer />

    <v-menu offset-y>
      <template #activator="{ props }">
        <v-btn
          v-bind="props"
          icon
          class="d-flex align-center"
          aria-label="$t('changeLanguage')"
        >
          <span :class="`fi fi-${currentFlag}`" style="font-size: 1.8rem;"></span>
        </v-btn>
      </template>

      <v-list>
        <v-list-item
          v-for="(lang, code) in languages"
          :key="code"
          @click="changeLanguage(code)"
        >
          <v-list-item-icon>
            <span :class="`fi fi-${lang.flag}`" style="font-size: 1.8rem;"></span>
          </v-list-item-icon>
          <v-list-item-title>{{ lang.label }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const languages = {
  de: { label: 'Deutsch', flag: 'de' },
  en: { label: 'English', flag: 'gb' },
}

const currentFlag = ref(languages[locale.value]?.flag || 'gb')

function changeLanguage(lang) {
  locale.value = lang
  localStorage.setItem('lang', lang)
  currentFlag.value = languages[lang].flag
}
</script>
