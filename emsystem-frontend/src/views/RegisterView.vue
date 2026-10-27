
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { registerUser } from '../services/authService.js'
import PasswordInput from '../components/PasswordInput.vue'

const router = useRouter()

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''

  const first = firstName.value.trim()
  const last = lastName.value.trim()
  const normalizedEmail = email.value.trim().toLowerCase()

  if (!first || !last || !normalizedEmail || !password.value || !confirmPassword.value) {
    errorMessage.value = 'Please fill in all fields.'
    return
  }

  if (first.length > 30 || last.length > 30) {
    errorMessage.value = 'First and last names must be 30 characters or fewer.'
    return
  }

  if (password.value.length < 8 || password.value.length > 128) {
    errorMessage.value = 'Password must be between 8 and 128 characters.'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  loading.value = true

  try {
    const response = await registerUser( {
      first_name: first,
      last_name: last,
      email: normalizedEmail,
      password: password.value,
    })

    successMessage.value =
      response.data.message || 'Registration successful! You can now log in.'

    // Do not automatically log in or store a token here.
    password.value = ''
    confirmPassword.value = ''

    // Show the success message briefly, then return to login.
    setTimeout(() => {
      router.push('/')
    }, 1500)
  } catch (error) {
    const status = error.response?.status
    const data = error.response?.data

    if (status === 409) {
      errorMessage.value = data?.error || 'An account with this email already exists.'
    } else if (status === 400) {
      errorMessage.value = data?.error || 'Please check the information you entered.'
    } else if (error.code === 'ECONNABORTED') {
      errorMessage.value = 'The request timed out. Please try again.'
    } else if (!error.response) {
      errorMessage.value = 'Cannot connect to the server. Please try again.'
    } else {
      errorMessage.value = data?.error || 'Registration failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card">
      <div class="brand">
        <div class="brand-icon">E</div>
        <h1>EMSystem</h1>
        <p>Create your employee account</p>
      </div>

      <form @submit.prevent="handleRegister">
        <div class="name-row">
          <div class="form-group">
            <label for="firstName">First name</label>
            <input
              id="firstName"
              v-model="firstName"
              type="text"
              maxlength="30"
              autocomplete="given-name"
              placeholder="First name"
              required
            />
          </div>

          <div class="form-group">
            <label for="lastName">Last name</label>
            <input
              id="lastName"
              v-model="lastName"
              type="text"
              maxlength="30"
              autocomplete="family-name"
              placeholder="Last name"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="email">Email address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="you@example.com"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <PasswordInput
            id="password"
            v-model="password"
            name="password"
            type="password"
            autocomplete="new-password"
            placeholder="At least 8 characters"
            :required= "true"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm password</label>
          <PasswordInput
            id="confirmPassword"
            v-model="confirmPassword"
            name="confirmPassword"
            type="password"
            autocomplete="new-password"
            placeholder="Re-enter your password"
            :required = "true"
          />
        </div>

        <p v-if="errorMessage" class="message error" role="alert">
          {{ errorMessage }}
        </p>

        <p v-if="successMessage" class="message success" role="status">
          {{ successMessage }}
        </p>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Create account' }}
        </button>
      </form>

      <p class="footer-text">
        Already have an account?
        <RouterLink to="/">Sign in</RouterLink>
      </p>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  background: #f3f6fb;
  font-family: Arial, Helvetica, sans-serif;
}

.auth-card {
  width: 100%;
  max-width: 460px;
  padding: 36px;
  background: #fff;
  border: 1px solid #e5eaf2;
  border-radius: 16px;
  box-shadow: 0 12px 35px rgba(24, 45, 80, 0.08);
}

.brand {
  text-align: center;
  margin-bottom: 28px;
}

.brand-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  display: grid;
  place-items: center;
  color: #fff;
  background: #2563eb;
  border-radius: 12px;
  font-size: 25px;
  font-weight: 700;
}

.brand h1 {
  margin: 0;
  color: #172b4d;
  font-size: 26px;
}

.brand p {
  margin: 8px 0 0;
  color: #718096;
  font-size: 14px;
}

.name-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 7px;
  color: #344054;
  font-size: 14px;
  font-weight: 600;
}

.form-group input {
  box-sizing: border-box;
  width: 100%;
  padding: 12px 13px;
  border: 1px solid #d5dce7;
  border-radius: 8px;
  outline: none;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.message {
  padding: 11px 12px;
  margin: 0 0 16px;
  border-radius: 7px;
  font-size: 13px;
  line-height: 1.5;
}

.error {
  color: #b42318;
  background: #fef3f2;
  border: 1px solid #fecdca;
}

.success {
  color: #067647;
  background: #ecfdf3;
  border: 1px solid #abefc6;
}

button {
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 8px;
  color: #fff;
  background: #2563eb;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover:not(:disabled) {
  background: #1d4ed8;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.footer-text {
  margin: 24px 0 0;
  text-align: center;
  color: #667085;
  font-size: 14px;
}

.footer-text a {
  color: #2563eb;
  font-weight: 600;
  text-decoration: none;
}

.footer-text a:hover {
  text-decoration: underline;
}

@media (max-width: 420px) {
  .auth-card {
    padding: 26px 20px;
  }

  .name-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
