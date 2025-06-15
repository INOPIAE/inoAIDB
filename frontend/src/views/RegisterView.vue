<template>
  <v-container>
    <h2>{{ t('registerAccount') }}</h2>

    <v-card v-if="!totpUri" class="pa-4">
      <v-text-field
        v-model="form.username"
        :label="t('username')"
      />
      <v-text-field
        v-model="form.email"
        :label="t('email')"
        type="email"
      />
      <v-text-field
        v-model="form.password"
        :label="t('password')"
        type="password"
      />
      <v-text-field
        v-model="form.invite"
        :label="t('invite')"
      />
      <v-btn color="primary" @click="register">
        {{ t('submitRegister') }}
      </v-btn>
    </v-card>

    <v-card v-if="totpUri" class="pa-4 mt-4">
      <h3>{{ t('scanTotp') }}</h3>
      <qrcode-vue :value="totpUri" :size="200" />
      <p class="mt-2">{{ t('scanInstruction') }}</p>
      <p>{{ t('cannotScan') }}</p>
      <p><strong>{{ totpUri }}</strong></p>

      <v-btn color="primary" class="mt-4" @click="goToLogin">
        {{ t('goToLogin') }}
      </v-btn>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import axios from 'axios'
import QrcodeVue from 'qrcode.vue'

const { t } = useI18n()
const router = useRouter()
const totpUri = ref(null)

const form = ref({
  username: '',
  email: '',
  password: '',
  invite: '',
})

const register = async () => {
  try {
    const res = await axios.post('/api/users/register', form.value)
    totpUri.value = res.data.totp_uri
  } catch (e) {
    alert(t('errorRegister') + ': ' + (e.response?.data?.detail || e.message))
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.mt-2 {
  margin-top: 16px;
}
.mt-4 {
  margin-top: 32px;
}
</style>
