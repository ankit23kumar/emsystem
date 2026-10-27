
import { ref, computed } from 'vue'
import { getSession, clearSession } from '../services/auth'

const user = ref(null)
const token = ref(null)

export function useAuthStore() {
  const isAuthenticated = computed(() => Boolean(token.value))

  function initializeAuth() {
    const session = getSession()

    user.value = session?.user ?? null
    token.value = session?.access_token ?? null
  }

  function setSession(session) {
    user.value = session?.user ?? null
    token.value = session?.access_token ?? null
  }

  function logout() {
    clearSession()
    user.value = null
    token.value = null
  }

  return {
    user,
    token,
    isAuthenticated,
    initializeAuth,
    setSession,
    logout,
  }
}
