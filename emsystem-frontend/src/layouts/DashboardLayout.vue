
<script setup>
import DashboardTopbar from "../components/DashboardTopbar.vue";
</script>

<template>
  <div class="dashboard-layout">
    <DashboardTopbar />

    <main class="dashboard-main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  background: #f3f4f6;
  color: #111827;
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Arial, sans-serif;
}

.dashboard-main {
  width: 100%;
  max-width: 1480px;
  margin: 0 auto;
  padding: 24px 20px 40px;
}

@media (max-width: 600px) {
  .dashboard-main {
    padding: 20px 12px 30px;
  }
}
</style>
