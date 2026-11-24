
<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import DashboardLayout from "../layouts/DashboardLayout.vue";
import DashboardTabs from "../components/dashboard/DashboardTabs.vue";
import UserManagementPanel from "../components/dashboard/UserManagementPanel.vue";

import { useAuthStore } from "../stores/authStore";
import { useToast } from "../composables/useToast";
import { updateUser } from "../services/userService";

import RoleManagementPanel from '../components/dashboard/RoleManagementPanel.vue'

const router = useRouter();
const authStore = useAuthStore();
const { showToast } = useToast();

const user = authStore.user;
const profileLoaded = authStore.profileLoaded;
const loading = authStore.profileLoading;

// const activeTab = ref("users");
const showProfileForm = ref(false);
const savingProfile = ref(false);
const profileErrors = ref({});
// Tracks whether the user has opened the Roles tab.
const savedTab = localStorage.getItem("emsystem_active_tab");

const activeTab = ref(
  savedTab === "roles" ? "roles" : "users"
);

const hasVisitedRoles = ref(false);

const canReadRoles = computed(() =>
  authStore.hasPermission("roles.read"),
);
// Save the selected tab.
watch(activeTab, (newTab) => {
  localStorage.setItem("emsystem_active_tab", newTab);
});

// Load Roles only after the user's permissions are available.
watch(
  [activeTab, profileLoaded, canReadRoles],
  ([tab, loaded, allowed]) => {
    if (tab === "roles" && loaded && allowed) {
      hasVisitedRoles.value = true;
    }

    if (loaded && !allowed && tab === "roles") {
      activeTab.value = "users";
    }
  },
  { immediate: true }
);

const userStats = ref({
  totalUsers: 0,
  validOnPage: 0,
  invalidOnPage: 0,
  newThisMonthOnPage: 0,
});

const profileForm = ref({
  first_name: "",
  last_name: "",
  email: "",
});

const initials = computed(() => {
  const first = user.value?.first_name?.[0] || "";
  const last = user.value?.last_name?.[0] || "";

  return (first + last).toUpperCase() || "U";
});

function handleStatsUpdate(stats) {
  userStats.value = stats;
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}


async function loadProfile() {
  if (profileLoaded.value) return;

  try {
    await authStore.loadCurrentUser();
  } catch (error) {
    if (error.response?.status === 401) {
      authStore.logout();
      router.replace("/");
      return;
    }

    showToast(
      error.response?.data?.error ||
        error.response?.data?.message ||
        "Unable to load your profile.",
      "error",
    );
  }
}

function openProfileForm() {
  profileErrors.value = {};

  profileForm.value = {
    first_name: user.value?.first_name || "",
    last_name: user.value?.last_name || "",
    email: user.value?.email || "",
  };

  showProfileForm.value = true;
}

function validateProfile() {
  const errors = {};

  const firstName = profileForm.value.first_name.trim();
  const lastName = profileForm.value.last_name.trim();
  const email = profileForm.value.email.trim();

  if (!firstName) {
    errors.first_name = "First name is required.";
  } else if (firstName.length > 40) {
    errors.first_name = "First name cannot exceed 40 characters.";
  }

  if (!lastName) {
    errors.last_name = "Last name is required.";
  } else if (lastName.length > 40) {
    errors.last_name = "Last name cannot exceed 40 characters.";
  }

  if (!email) {
    errors.email = "Email is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = "Enter a valid email address.";
  }

  profileErrors.value = errors;

  return Object.keys(errors).length === 0;
}

async function saveProfile() {
  if (!validateProfile()) return;

  const userId = user.value?.user_id;

  if (!userId) {
    showToast(
      "Your user ID is unavailable. Please log in again.",
      "error",
    );
    return;
  }

  savingProfile.value = true;

  try {
    const payload = {
      first_name: profileForm.value.first_name.trim(),
      last_name: profileForm.value.last_name.trim(),
      email: profileForm.value.email.trim(),
    };

    const response = await updateUser(userId, payload);

    // Update the profile held by the authentication store.
    user.value = {
      ...user.value,
      ...(response.data.user || response.data),
      ...payload,
    };

    showProfileForm.value = false;

    showToast(
      response.data.message || "Profile updated successfully.",
      "success",
    );
  } catch (error) {
    if (error.response?.status === 401) {
      authStore.logout();
      router.replace("/");
      return;
    }

    const message =
      error.response?.data?.error ||
      error.response?.data?.message ||
      "Unable to update your profile.";

    if (error.response?.status === 409) {
      profileErrors.value = {
        ...profileErrors.value,
        email: message,
      };
    } else {
      showToast(message, "error");
    }
  } finally {
    savingProfile.value = false;
  }
}

function closeUserModal() {
  showUserModal.value = false;
  selectedUser.value = null;
}

onMounted(() => {
  loadProfile();
});
</script>

<template>
  <DashboardLayout>
    <section class="content">
      <header class="page-title">
        <h1>User Dashboard</h1>
        <p>Overview of your account and registered users</p>
      </header>

      <DashboardTabs
        v-model:active-tab="activeTab"
        :show-roles="canReadRoles"
      />

      <!-- Users tab -->
      <div
        v-show="activeTab === 'users'"
        class="dashboard-panel"
      >
        <section class="profile-card">
          <div class="profile-avatar-area">
            <div class="avatar-large">{{ initials }}</div>
            <span>My Profile</span>
          </div>

          <div v-if="loading" class="profile-loading">
            Loading your profile...
          </div>

          <div v-else class="profile-details">
            <div class="detail">
              <span class="detail-label">First name</span>
              <strong>{{ user?.first_name || "—" }}</strong>
            </div>

            <div class="detail">
              <span class="detail-label">Last name</span>
              <strong>{{ user?.last_name || "—" }}</strong>
            </div>

            <div class="detail">
              <span class="detail-label">Email</span>
              <strong class="email-value">
                {{ user?.email || "—" }}
              </strong>
            </div>

            <div class="detail">
              <span class="detail-label">Password</span>
              <strong class="password-dots">••••••••••</strong>
              <small class="password-note">Stored securely</small>
            </div>

            <div class="detail">
              <span class="detail-label">Created date</span>
              <strong>{{ formatDate(user?.created_at) }}</strong>
            </div>

            <div class="detail">
              <span class="detail-label">Valid date</span>
              <strong>{{ formatDate(user?.valid_until) }}</strong>
            </div>
          </div>

          <button
            type="button"
            class="outline-button profile-edit-button"
            :disabled="loading || !user"
            @click="openProfileForm"
          >
            Edit Profile
          </button>
        </section>

        <!-- User statistics -->
        <section class="stats-grid">
          <article class="stat-card">
            <span class="stat-icon blue">●</span>
            <div>
              <strong class="stat-number">
                {{ userStats.totalUsers }}
              </strong>
              <span class="stat-label">Total Users</span>
            </div>
          </article>

          <article class="stat-card">
            <span class="stat-icon green">●</span>
            <div>
              <strong class="stat-number">
                {{ userStats.validOnPage }}
              </strong>
              <span class="stat-label">Valid Users on Page</span>
            </div>
          </article>

          <article class="stat-card">
            <span class="stat-icon red">●</span>
            <div>
              <strong class="stat-number">
                {{ userStats.invalidOnPage }}
              </strong>
              <span class="stat-label">Invalid Users on Page</span>
            </div>
          </article>

          <article class="stat-card">
            <span class="stat-icon amber">●</span>
            <div>
              <strong class="stat-number">
                {{ userStats.newThisMonthOnPage }}
              </strong>
              <span class="stat-label">New This Month on Page</span>
            </div>
          </article>
        </section>

        <!-- User management component -->
        <UserManagementPanel
          @stats-update="handleStatsUpdate"
        />
      </div>

      <!-- Roles tab -->
      <div
        v-if="profileLoaded && hasVisitedRoles"
        v-show="activeTab === 'roles' && canReadRoles"
        class="dashboard-panel"
      >
        <RoleManagementPanel/>
      </div>
    </section>

    <!-- Edit profile modal -->
    <div
      v-if="showProfileForm"
      class="modal-backdrop"
      @click.self="showProfileForm = false"
    >
      <section
        class="profile-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="profile-modal-title"
      >
        <div class="modal-heading">
          <div>
            <h2 id="profile-modal-title">Edit Profile</h2>
            <p>Update your personal information.</p>
          </div>

          <button
            type="button"
            class="close-button"
            aria-label="Close"
            :disabled="savingProfile"
            @click="showProfileForm = false"
          >
            ×
          </button>
        </div>

        <form @submit.prevent="saveProfile" novalidate>
          <div class="form-field">
            <label for="profile-first-name">First name</label>
            <input
              id="profile-first-name"
              v-model="profileForm.first_name"
              :class="{ 'invalid-input': profileErrors.first_name }"
              autocomplete="given-name"
              maxlength="40"
              @input="delete profileErrors.first_name"
            />
            <small
              v-if="profileErrors.first_name"
              class="field-error"
            >
              {{ profileErrors.first_name }}
            </small>
          </div>

          <div class="form-field">
            <label for="profile-last-name">Last name</label>
            <input
              id="profile-last-name"
              v-model="profileForm.last_name"
              :class="{ 'invalid-input': profileErrors.last_name }"
              autocomplete="family-name"
              maxlength="40"
              @input="delete profileErrors.last_name"
            />
            <small
              v-if="profileErrors.last_name"
              class="field-error"
            >
              {{ profileErrors.last_name }}
            </small>
          </div>

          <div class="form-field">
            <label for="profile-email">Email address</label>
            <input
              id="profile-email"
              v-model="profileForm.email"
              :class="{ 'invalid-input': profileErrors.email }"
              type="email"
              autocomplete="email"
              maxlength="254"
              @input="delete profileErrors.email"
            />
            <small
              v-if="profileErrors.email"
              class="field-error"
            >
              {{ profileErrors.email }}
            </small>
          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="cancel-button"
              :disabled="savingProfile"
              @click="showProfileForm = false"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="primary-button"
              :disabled="savingProfile"
            >
              {{ savingProfile ? "Saving..." : "Save Changes" }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </DashboardLayout>
</template>

<style scoped>
.content {
  width: 100%;
  margin: 0;
  padding: 0;
}

.page-title {
  margin-bottom: 12px;
}

.page-title h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 750;
  letter-spacing: -0.4px;
}

.page-title p {
  margin: 6px 0 0;
  color: #667085;
  font-size: 13px;
}

.dashboard-panel {
  padding: 24px;
  background: #e4eaf4;
  border-radius: 0 12px 12px 12px;
}

.profile-card,
.stat-card {
  border: 1px solid #e1e5eb;
  border-radius: 13px;
  background: #fff;
}

.profile-card {
  position: relative;
  display: grid;
  grid-template-columns: 100px minmax(0, 1fr);
  gap: 28px;
  align-items: center;
  min-height: 178px;
  padding: 28px 30px;
}

.profile-avatar-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #667085;
  font-size: 12px;
}

.avatar-large {
  display: grid;
  place-items: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #dbeafe;
  color: #2864ed;
  font-size: 25px;
  font-weight: 750;
}

.profile-details {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px 26px;
  padding-right: 110px;
}

.detail {
  display: flex;
  flex-direction: column;
  gap: 7px;
  min-width: 0;
}

.detail-label {
  color: #667085;
  font-size: 10px;
  font-weight: 750;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.detail strong {
  overflow-wrap: anywhere;
  font-size: 14px;
}

.password-dots {
  letter-spacing: 2px;
}

.password-note {
  color: #98a2b3;
  font-size: 10px;
}

.profile-loading {
  color: #667085;
  font-size: 14px;
}

.profile-edit-button {
  position: absolute;
  top: 15px;
  right: 15px;
}

.outline-button,
.cancel-button {
  border: 1px solid #2864ed;
  border-radius: 7px;
  background: #fff;
  color: #2864ed;
  padding: 8px 13px;
  font-size: 12px;
  font-weight: 650;
  cursor: pointer;
}

.outline-button:hover:not(:disabled) {
  background: #eff6ff;
}

.outline-button:disabled,
.cancel-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin: 20px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
  min-height: 98px;
  padding: 20px 22px;
}

.stat-icon {
  display: grid;
  place-items: center;
  flex: 0 0 48px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  font-size: 16px;
}

.stat-icon.blue {
  color: #2864ed;
  background: #dbeafe;
}

.stat-icon.green {
  color: #16a34a;
  background: #dcfce7;
}

.stat-icon.red {
  color: #dc2626;
  background: #fee2e2;
}

.stat-icon.amber {
  color: #d97706;
  background: #fef3c7;
}

.stat-card > div {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-number {
  font-size: 28px;
  line-height: 1;
}

.stat-label {
  color: #667085;
  font-size: 12px;
}

/* Profile modal */
.modal-backdrop {
  position: fixed;
  z-index: 20;
  inset: 0;
  display: grid;
  place-items: center;
  overflow-y: auto;
  padding: 20px;
  background: #10182880;
}

.profile-modal {
  width: min(100%, 470px);
  padding: 25px;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 20px 50px #10182830;
}

.modal-heading {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
}

.modal-heading h2 {
  margin: 0;
  font-size: 21px;
}

.modal-heading p {
  margin: 6px 0 0;
  color: #667085;
  font-size: 13px;
}

.close-button {
  align-self: flex-start;
  border: 0;
  background: transparent;
  color: #667085;
  font-size: 25px;
  cursor: pointer;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-bottom: 17px;
}

.form-field label {
  color: #344054;
  font-size: 13px;
  font-weight: 650;
}

.form-field input {
  width: 100%;
  padding: 11px 12px;
  border: 1px solid #d0d5dd;
  border-radius: 7px;
  outline: none;
  color: #151d2e;
  font: inherit;
  font-size: 13px;
}

.form-field input:focus {
  border-color: #2864ed;
  box-shadow: 0 0 0 3px #2864ed1c;
}

.form-field input.invalid-input {
  border-color: #dc2626;
}

.field-error {
  color: #b42318;
  font-size: 12px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}

.cancel-button {
  border-color: #d0d5dd;
  color: #344054;
}

.primary-button {
  border: 0;
  border-radius: 7px;
  background: #2864ed;
  color: #fff;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
}

.primary-button:hover:not(:disabled) {
  background: #1d4ed8;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .profile-details {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    padding-right: 0;
    padding-top: 25px;
  }

  .profile-card {
    grid-template-columns: 85px minmax(0, 1fr);
    gap: 18px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .dashboard-panel {
    padding: 14px;
  }

  .page-title h1 {
    font-size: 22px;
  }

  .profile-card {
    grid-template-columns: 1fr;
    padding: 22px 18px;
  }

  .profile-avatar-area {
    align-items: flex-start;
  }

  .profile-details {
    grid-template-columns: 1fr;
    gap: 17px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-card {
    min-height: 82px;
  }
}
</style>
