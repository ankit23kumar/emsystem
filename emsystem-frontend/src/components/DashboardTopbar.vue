
<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/authStore";

const router = useRouter();
const auth = useAuthStore();

const initials = computed(() => {
  const first = auth.user.value?.first_name?.[0] || "";
  const last = auth.user.value?.last_name?.[0] || "";

  return (first + last).toUpperCase() || "U";
});

const fullName = computed(() => {
  return `${auth.user.value?.first_name || ""} ${
    auth.user.value?.last_name || ""
  }`.trim();
});

function handleLogout() {
  auth.logout();
  router.replace("/");
}
</script>

<template>
  <header class="dashboard-topbar">
    <div class="topbar-brand">
      <span class="brand-mark">EM</span>
      <strong>EMSystem</strong>
    </div>

    <div class="topbar-user">
      <span class="user-name">{{ fullName || "User" }}</span>

      <span class="avatar">{{ initials }}</span>

      <button type="button" class="logout-button" @click="handleLogout">
        Log out
      </button>
    </div>
  </header>
</template>

<style scoped>
.dashboard-topbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 0 40px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.topbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #111827;
  font-size: 17px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: #2563eb;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
}

.topbar-user {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #374151;
  font-size: 12px;
}

.avatar {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #dbeafe;
  color: #2563eb;
  font-size: 10px;
  font-weight: 700;
}

.logout-button {
  padding: 8px 16px;
  border: 1px solid #2563eb;
  border-radius: 7px;
  background: #2563eb;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.logout-button:hover {
  background: #1d4ed8;
}

@media (max-width: 600px) {
  .dashboard-topbar {
    padding: 0 15px;
  }

  .user-name {
    display: none;
  }
}
</style>
