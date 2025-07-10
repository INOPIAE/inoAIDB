// src/composables/useSanitizedHtml.js
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import linkifyHtml from 'linkify-html'

export function useSanitizedHtml(textRef) {
  const sanitizedHtml = computed(() => {
    const raw = textRef.value ?? ''
    const linkified = linkifyHtml(raw, {
      target: '_blank',
      rel: 'noopener noreferrer',
    })
    return DOMPurify.sanitize(linkified, {
      ALLOWED_TAGS: ['a', 'pre'],
      ALLOWED_ATTR: ['href', 'target', 'rel'],
    })
  })

  return { sanitizedHtml }
}
