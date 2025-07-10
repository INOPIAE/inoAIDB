import { useI18n } from 'vue-i18n'

export function useFormat() {
  const { t, locale } = useI18n()

  function formatExpire(value) {
    if (!value) return t('noExpire')
    const date = new Date(value)
    return date.toLocaleString(locale.value, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return { formatExpire }
}
