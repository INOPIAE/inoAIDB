<template>
  <v-container class="mt-10" max-width="500px">
    <v-card>
      <v-card-title class="text-h6">{{ t('paymentTitle') }}</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="submit" ref="formRef" v-model="valid">
          <v-text-field
            :label="t('email')"
            v-model="form.email"
            :rules="[rules.required, rules.email]"
            type="email"
          />
          <v-text-field
            :label="t('token')"
            v-model="form.token"
            :rules="[rules.required]"
          />
          <v-text-field
            :label="t('totpCode')"
            v-model="form.otp"
            :rules="[rules.required]"
          />
          <v-btn
            :disabled="!valid || loading"
            type="submit"
            color="primary"
            class="mt-4"
          >
            {{ t('redeem') }}
          </v-btn>
        </v-form>

        <v-alert v-if="newExpiry" type="success" class="mt-4">
          {{ t('paymentSuccess') }} <strong>{{ formatDate(newExpiry) }}</strong>
        </v-alert>
        <v-alert v-if="error" type="error" class="mt-4">
          {{ error }}
        </v-alert>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()

const form = reactive({
  email: '',
  token: '',
  otp: '',
})
const valid = ref(false)
const loading = ref(false)
const newExpiry = ref(null)
const error = ref(null)
const formRef = ref(null)

onMounted(() => {
  const tokenFromUrl = route.query.token
  if (tokenFromUrl) {
    form.token = tokenFromUrl
  }
})

const rules = {
  required: v => !!v || t('validationRequired'),
  email: v => /.+@.+\..+/.test(v) || t('validationEmail'),
}

const submit = async () => {
  loading.value = true
  error.value = null
  newExpiry.value = null
  try {
    const response = await axios.put('/api/users/payments', form)
    if (response.data.success) {
      newExpiry.value = response.data.new_expiry
    }
  } catch (err) {
    error.value =
      err.response?.data?.detail || t('paymentError')
    console.error(err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString()
}
</script>
