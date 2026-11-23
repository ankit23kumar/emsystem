
<script setup>
const props = defineProps({
  activeTab: {
    type: String,
    required: true,
  },
  showRoles: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:activeTab"]);

function selectTab(tab) {
  if (tab === "roles" && !props.showRoles) return;

  emit("update:activeTab", tab);
}
</script>

<template>
  <nav class="dashboard-tabs" aria-label="Dashboard sections">
    <!-- Users tab -->
    <button
      type="button"
      class="tab-button"
      :class="{ active: activeTab === 'users' }"
      :aria-current="activeTab === 'users' ? 'page' : undefined"
      @click="selectTab('users')"
    >
      Users
    </button>

    <!-- Roles tab: always visible -->
    <button
      type="button"
      class="tab-button"
      :class="{
        active: activeTab === 'roles' && showRoles,
        'tab-locked': !showRoles,
      }"
      :disabled="!showRoles"
      :aria-disabled="!showRoles"
      :title="showRoles ? 'Manage roles' : 'You do not have permission to access roles'"
      @click="selectTab('roles')"
    >
      Roles
      <!-- <span v-if="!showRoles" class="lock-indicator">
        🔒
      </span> -->
    </button>
  </nav>
</template>

<style scoped>
.dashboard-tabs {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  margin-bottom: 0;
  border-bottom: 1px solid #cbd5e1;
}

.tab-button {
  position: relative;
  padding: 11px 24px;
  border: 1px solid #cbd5e1;
  border-bottom: none;
  border-radius: 9px 9px 0 0;
  background: #cfd8e8;
  color: #374151;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.tab-button:hover {
  background: #dbe4f1;
}

.tab-button.active {
  background: #e4eaf4;
  color: #2563eb;
  border-color: #cbd5e1;
}

.tab-locked {
  opacity: 0.55;
  filter: blur(0.3px);
  cursor: not-allowed;
  background: #e5e7eb;
  color: #667085;
}

.tab-locked:hover {
  background: #e5e7eb;
}

.lock-indicator {
  margin-left: 5px;
  font-size: 11px;
}

@media (max-width: 600px) {
  .tab-button {
    padding: 10px 18px;
    font-size: 13px;
  }
}
</style>
