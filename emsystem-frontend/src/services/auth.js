
const TOKEN_KEY = 'emsystem_access_token'
const USER_KEY = 'emsystem_user'
const EXPIRY_KEY = 'emsystem_token_expiry'

export function saveSession(data) {
  const token = data.access_token
  const user = data.user
  const lifetime = Number(data.expire_in ?? data.expires_in)

  if (!token || !user || !Number.isFinite(lifetime) || lifetime <= 0) {
    throw new Error('The server returned an invalid login response.')
  }

  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
  localStorage.setItem(
    EXPIRY_KEY,
    String(Date.now() + lifetime * 1000)
  )
}

export function getSession() {
    if (!isAuthenticated()) return null

    return {
        access_token: localStorage.getItem(TOKEN_KEY),
        user: getUser(),
    }
}

export function getToken() {
  if (!isAuthenticated()) return null

  return localStorage.getItem(TOKEN_KEY)
}

export function getUser() {
  if (!isAuthenticated()) return null

  try {
    return JSON.parse(localStorage.getItem(USER_KEY))
  } catch {
    clearSession()
    return null
  }
}

export function isAuthenticated() {
  const token = localStorage.getItem(TOKEN_KEY)
  const expiry = Number(localStorage.getItem(EXPIRY_KEY))

  if (!token || !Number.isFinite(expiry) || Date.now() >= expiry) {
    clearSession()
    return false
  }

  return true
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  localStorage.removeItem(EXPIRY_KEY)

  // Clean up old sessionStorage data from previous versions.
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(USER_KEY)
  sessionStorage.removeItem(EXPIRY_KEY)
}
