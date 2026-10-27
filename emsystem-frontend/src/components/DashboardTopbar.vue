
<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const auth = useAuthStore()

onMounted(() => {
  auth.initializeAuth()
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="dashboard-topbar">
    <div class="topbar-brand">
      <strong>EMSystem</strong>
    </div>

    <div class="topbar-user">
      <span v-if="auth.user">
        {{ auth.user.first_name }} {{ auth.user.last_name }}
      </span>

      <button type="button" @click="handleLogout">
        Logout
      </button>
    </div>
  </header>
</template>
