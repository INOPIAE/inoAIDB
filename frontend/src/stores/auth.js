import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(email, password, otp) {
      try {
        const loginRes = await axios.post('/api/auth/login', { email, password, otp })
        this.user = loginRes.data
      } catch (error) {
        console.error('Login failed:', error.response?.data || error.message)
        throw error
      }
    },

    async verifyOTP(email, otp) {
      try {
        const verifyRes = await axios.post('/api/auth/verify', { email, otp_code: otp })
        this.token = verifyRes.data.access_token

        localStorage.setItem('token', this.token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      } catch (error) {
        console.error('OTP verification failed:', error.response?.data || error.message)
        throw error
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },

    async tryAutoLogin() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        try {
          // Optional: hole aktuellen Benutzer vom Backend
          const res = await axios.get('/api/users/me') // falls so ein Endpoint existiert
          this.user = res.data
        } catch (error) {
          console.warn('Auto-Login fehlgeschlagen:', error.response?.data || error.message)
          this.logout()
        }
      }
    }
  },
})