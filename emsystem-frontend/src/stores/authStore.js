
import { ref, computed } from 'vue'
import {
  getToken,
  getUser,
  clearSession,
} from '../services/auth'
import { getMyProfile } from '../services/userService'

// Shared authentication state
const user = ref(null)
const token = ref(null)
const profileLoaded = ref(false)
const profileLoading = ref(false)

export function useAuthStore() {
  const isAuthenticated = computed(() => Boolean(token.value))

  // Get current user's permissions
  const permissions = computed(() => {
    return user.value?.permissions ?? []
  })

  // Check whether the user has a particular permission
  function hasPermission(codename) {
    return permissions.value.includes(codename)
  }

  // Load the latest user profile from Django
  async function loadCurrentUser() {
    if (!getToken()) {
      logout()
      return null
    }

    profileLoading.value = true

    try {
      const response = await getMyProfile()

      user.value = response.data.user
      token.value = getToken()
      profileLoaded.value = true

      return user.value
    } finally {
      profileLoading.value = false
    }
  }

  // Initialize authentication from saved session
  async function initializeAuth() {
    token.value = getToken()
    user.value = getUser()

    if (!token.value) {
      profileLoaded.value = true
      return null
    }

    return loadCurrentUser()
  }

  // Update authentication state after login
  function setSession(session) {
    user.value = session?.user ?? null
    token.value = getToken()
    profileLoaded.value = false
  }

  // Clear authentication state
  function logout() {
    clearSession()
    user.value = null
    token.value = null
    profileLoaded.value = false
    profileLoading.value = false
  }

  return {
    user,
    token,
    permissions,
    isAuthenticated,
    profileLoaded,
    profileLoading,
    hasPermission,
    loadCurrentUser,
    initializeAuth,
    setSession,
    logout,
  }
}
