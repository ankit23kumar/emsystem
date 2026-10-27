
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

  sessionStorage.setItem(TOKEN_KEY, token)
  sessionStorage.setItem(USER_KEY, JSON.stringify(user))
  sessionStorage.setItem(EXPIRY_KEY, String(Date.now() + lifetime * 1000))
}

export function getToken() {
  if (!isAuthenticated()) return null
  return sessionStorage.getItem(TOKEN_KEY)
}

export function getUser() {
  if (!isAuthenticated()) return null

  try {
    return JSON.parse(sessionStorage.getItem(USER_KEY))
  } catch {
    clearSession()
    return null
  }
}

export function isAuthenticated() {
  const token = sessionStorage.getItem(TOKEN_KEY)
  const expiry = Number(sessionStorage.getItem(EXPIRY_KEY))

  if (!token || !Number.isFinite(expiry) || Date.now() >= expiry) {
    clearSession()
    return false
  }

  return true
}

export function clearSession() {
  sessionStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(USER_KEY)
  sessionStorage.removeItem(EXPIRY_KEY)
}
