import { ref } from 'vue'

// Shared toast state
const toast = ref({
  show: false,
  type: 'success',
  message: '',
  duration: 4000,
})

let timeoutId = null

function clearTimer() {
  if (timeoutId) {
    clearTimeout(timeoutId)
    timeoutId = null
  }
}

function showToast(message, type = 'success', duration = 4000) {
  clearTimer()

  toast.value = {
    show: true,
    type,
    message,
    duration,
  }

  if (duration > 0) {
    timeoutId = setTimeout(() => {
      hideToast()
    }, duration)
  }
}

function hideToast() {
  clearTimer()
  toast.value.show = false
}

export function useToast() {
  return {
    toast,
    showToast,
    hideToast,
  }
}