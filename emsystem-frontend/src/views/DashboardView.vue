<script setup>
import {
  computed,
  onMounted,
  onBeforeUnmount,
  ref,
  watch,
  defineAsyncComponent,
} from "vue";
import { useRouter } from "vue-router";
import { useUsers } from "../composables/useUsers";
import UserFormModal from "../components/UserFormModal.vue";
import { deleteUser, updateUser } from "../services/userService";
import { useAuthStore } from "../stores/authStore";
import ConfirmationModal from "../components/ConfirmationModal.vue";
import { useToast } from "../composables/useToast";
import { getRoles, assignUserRole } from "../services/roleService";

const UserGrid = defineAsyncComponent(
  () => import("../components/UserGrid.vue"),
);

const router = useRouter();
const { showToast } = useToast();
const authStore = useAuthStore();

const { user, profileLoaded, profileLoading } = authStore;

const loading = profileLoading;

const {
  users,
  loading: usersLoading,
  errorMessage,
  currentPage,
  pageSize,
  totalUsers,
  totalPages,
  hasNext,
  hasPrevious,
  filters,
  loadUsers,
  updateFilters,
} = useUsers(router);

watch(errorMessage, (message) => {
  if (message) {
    showToast(message, "error");
  }
});

const searchInput = ref("");

// const usersLoading = ref(false)
const savingProfile = ref(false);

const showProfileForm = ref(false);

const showDeleteConfirmation = ref(false);
const userToDelete = ref(null);
const deletingUser = ref(false);

const showUserModal = ref(false);
const userFormMode = ref("create");
const selectedUser = ref(null);

// Role assignment state
const showAssignRoleModal = ref(false);
const selectedUserForRole = ref(null);
const availableRoles = ref([]);
const selectedRoleId = ref("");
const loadingRoles = ref(false);
const assigningRole = ref(false);

const canAssignRoles = computed(() =>
    authStore.hasPermission("users.update") &&
    authStore.hasPermission("roles.read"),
);

const canCreateUsers = computed(() => authStore.hasPermission("users.create"));

const canReadUsers = computed(() => authStore.hasPermission("users.read"));

const canUpdateUsers = computed(() => authStore.hasPermission("users.update"));

const canDeleteUsers = computed(() => authStore.hasPermission("users.delete"));

function openCreateUserModal() {
  selectedUser.value = null;
  userFormMode.value = "create";
  showUserModal.value = true;
}

function openEditUserModal(item) {
  selectedUser.value = { ...item };
  userFormMode.value = "edit";
  showUserModal.value = true;
}

async function handleUserSaved() {
  showUserModal.value = false;
  selectedUser.value = null;
  showToast(
    userFormMode.value === "create"
      ? "User created successfully."
      : "User updated successfully.",
    "success",
  );

  await loadUsers(currentPage.value);
}

const profileForm = ref({
  first_name: "",
  last_name: "",
  email: "",
});

const profileErrors = ref({});

const fullName = computed(() => {
  return `${user.value?.first_name || ""} ${user.value?.last_name || ""}`.trim();
});

const initials = computed(() => {
  const first = user.value?.first_name?.[0] || "";
  const last = user.value?.last_name?.[0] || "";
  return (first + last).toUpperCase() || "U";
});

// These counts describe the users currently loaded on this page.
// Total users comes from the backend's pagination metadata.
const validOnPage = computed(() => users.value.filter(isAccountValid).length);

const invalidOnPage = computed(
  () => users.value.filter((user) => !isAccountValid(user)).length,
);

const newThisMonthOnPage = computed(() => {
  const now = new Date();

  return users.value.filter((item) => {
    if (!item.created_at) return false;

    const date = new Date(item.created_at);

    return (
      !Number.isNaN(date.getTime()) &&
      date.getMonth() === now.getMonth() &&
      date.getFullYear() === now.getFullYear()
    );
  }).length;
});

function isAccountValid(item) {
  if (!item.valid_until) return false;

  const expiry = new Date(item.valid_until);
  if (Number.isNaN(expiry.getTime())) return false;

  // Treat an account as valid through its expiry date.
  expiry.setHours(23, 59, 59, 999);
  return expiry >= new Date();
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

function logout() {
  authStore.logout();
  router.replace("/");
}

async function loadProfile() {
  // Avoid another API request if login already loaded the profile.
  if (profileLoaded.value) {
    return;
  }

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
  const first = profileForm.value.first_name.trim();
  const last = profileForm.value.last_name.trim();
  const email = profileForm.value.email.trim();

  if (!first) {
    errors.first_name = "First name is required.";
  } else if (first.length > 40) {
    errors.first_name = "First name cannot exceed 40 characters.";
  }

  if (!last) {
    errors.last_name = "Last name is required.";
  } else if (last.length > 40) {
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
  profileError.value = "";
  profileSuccess.value = "";

  if (!validateProfile()) return;

  const userId = user.value?.user_id;

  if (!userId) {
    showToast(
      "Your user ID is unavailable. Please log out and log in again.",
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

    user.value = {
      ...user.value,
      ...(response.data.user || response.data),
      ...payload,
    };

    // Keep the locally stored session profile in sync with the edit.
    const storedUser = {
      ...getUser(),
      ...user.value,
    };

    sessionStorage.setItem("emsystem_user", JSON.stringify(storedUser));

    showProfileForm.value = false;

    showToast(
      response.data.message || "Profile updated successfully.",
      "success",
    );
  } catch (error) {
    if (error.response?.status === 401) {
      clearSession();
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

// Open confirmation modal when Delete is clicked.
function handleDeleteUser(item) {
  userToDelete.value = item;
  showDeleteConfirmation.value = true;
}

// Execute deletion only after confirmation.
async function confirmDeleteUser() {
  if (!userToDelete.value || deletingUser.value) return;

  const item = userToDelete.value;

  deletingUser.value = true;

  try {
    const response = await deleteUser(item.user_id);

    const nextPage =
      users.value.length === 1 && currentPage.value > 1
        ? currentPage.value - 1
        : currentPage.value;

    await loadUsers(nextPage);

    showToast(response.data.message || "User deleted successfully.", "success");

    showDeleteConfirmation.value = false;
    userToDelete.value = null;
  } catch (error) {
    if (error.response?.status === 401) {
      clearSession();
      router.replace("/");
      return;
    }

    showToast(
      error.response?.data?.error ||
        error.response?.data?.message ||
        "Unable to delete this user.",
      "error",
    );
    console.error("Delete failed:", error.response?.data || error.message);
  } finally {
    deletingUser.value = false;
  }
}

async function openAssignRoleModal(item) {
  if (!canAssignRoles.value) return;

  selectedUserForRole.value = item;
  selectedRoleId.value = "";
  showAssignRoleModal.value = true;
  loadingRoles.value = true;

  try {
    const response = await getRoles();
    availableRoles.value = response.data.roles || [];
  } catch (error) {
    showToast(
      error.response?.data?.error ||
        error.response?.data?.message ||
        "Unable to load available roles.",
      "error",
    );

    showAssignRoleModal.value = false;
  } finally {
    loadingRoles.value = false;
  }
}

function closeAssignRoleModal() {
  if (assigningRole.value) return;

  showAssignRoleModal.value = false;
  selectedUserForRole.value = null;
  selectedRoleId.value = "";
}

async function submitRoleAssignment() {
  if (!selectedUserForRole.value || assigningRole.value) return;

  assigningRole.value = true;

  try {
    if (!selectedRoleId.value) return;

    const roleId =
      selectedRoleId.value === "none" ? null : Number(selectedRoleId.value);

    const response = await assignUserRole(
      selectedUserForRole.value.user_id,
      roleId,
    );

    showToast(
      response.data.message || "User role updated successfully.",
      "success",
    );

    showAssignRoleModal.value = false;
    selectedUserForRole.value = null;
    selectedRoleId.value = "";
    await loadUsers(currentPage.value);
  } catch (error) {
    showToast(
      error.response?.data?.error ||
        error.response?.data?.message ||
        "Unable to assign role.",
      "error",
    );
  } finally {
    assigningRole.value = false;
  }
}

async function handleFirstNameSort(order) {
  if (order === "default") {
    await updateFilters({
      sort_by: "user_id",
      order: "asc",
    });
    return;
  }

  await updateFilters({
    sort_by: "first_name",
    order,
  });
}

async function handleFirstNameSortToggle() {
  if (filters.value.sort_by !== "first_name") {
    await updateFilters({
      sort_by: "first_name",
      order: "asc",
    });
  } else if (filters.value.order === "asc") {
    await updateFilters({
      sort_by: "first_name",
      order: "desc",
    });
  } else {
    await updateFilters({
      sort_by: "user_id",
      order: "asc",
    });
  }
}

async function handleFirstNameLetter(letter) {
  // selectedLetter.value = letter;

  await updateFilters({
    letter,
  });
}

// async function handleSearch() {
//   await updateFilters({
//     search: searchInput.value.trim(),
//   });
// }

let searchTimeout = null;

function handleSearch() {
  // Cancel the previous pending search.
  clearTimeout(searchTimeout);

  // Wait until the user stops typing.
  searchTimeout = setTimeout(() => {
    updateFilters({
      search: searchInput.value.trim(),
    });
  }, 500);
}

// async function handleLetterFilter() {
//   await updateFilters({
//     letter: selectedLetter.value,
//   });
// }

async function changePageSize(event) {
  pageSize.value = Number(event.target.value);
  await loadUsers(1);
}

async function previousPage() {
  if (hasPrevious.value && !usersLoading.value) {
    await loadUsers(currentPage.value - 1);
  }
}

async function nextPage() {
  if (hasNext.value && !usersLoading.value) {
    await loadUsers(currentPage.value + 1);
  }
}

onMounted(async () => {
  await Promise.all([loadProfile(), loadUsers()]);
});

onBeforeUnmount(() => {
  clearTimeout(searchTimeout);
});
</script>

<template>
  <main class="dashboard">
    <header class="topbar">
      <a class="brand" href="#" @click.prevent="loadUsers(1)">
        <span class="brand-mark">EM</span>
        <span>EMSystem</span>
      </a>

      <div class="topbar-user">
        <span>{{ fullName || "User" }}</span>
        <span class="avatar-small">{{ initials }}</span>
        <button class="logout-button" @click="logout">Log out</button>
      </div>
    </header>

    <section class="content">
      <div class="page-title">
        <h1>User Dashboard</h1>
        <p>Overview of your account and registered users</p>
      </div>

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
            <strong class="email-value">{{ user?.email || "—" }}</strong>
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
          class="outline-button profile-edit-button"
          @click="openProfileForm"
          :disabled="loading || !user"
        >
          Edit Profile
        </button>
      </section>

      <section class="stats-grid">
        <article class="stat-card">
          <span class="stat-icon blue">●</span>
          <div>
            <strong class="stat-number">{{ totalUsers }}</strong>
            <span class="stat-label">Total Users</span>
          </div>
        </article>

        <article class="stat-card">
          <span class="stat-icon green">●</span>
          <div>
            <strong class="stat-number">{{ validOnPage }}</strong>
            <span class="stat-label">Valid Users on Page</span>
          </div>
        </article>

        <article class="stat-card">
          <span class="stat-icon red">●</span>
          <div>
            <strong class="stat-number">{{ invalidOnPage }}</strong>
            <span class="stat-label">Invalid Users on Page</span>
          </div>
        </article>

        <article class="stat-card">
          <span class="stat-icon amber">●</span>
          <div>
            <strong class="stat-number">{{ newThisMonthOnPage }}</strong>
            <span class="stat-label">New This Month on Page</span>
          </div>
        </article>
      </section>

      <section class="users-card">
        <div class="table-heading">
          <h2>User Management</h2>

          <button
            class="primary-button"
            v-if="canCreateUsers"
            @click="openCreateUserModal"
          >
            + Add New User
          </button>
        </div>

        <div class="grid-toolbar">
          <input
            v-model="searchInput"
            type="search"
            placeholder="Search name or email..."
            class="grid-search"
            @input="handleSearch"
          />
        </div>

        <div class="ag-grid-wrapper">
          <UserGrid
            :users="users"
            :loading="usersLoading"
            :filters="filters"
            :on-edit="openEditUserModal"
            :on-delete="handleDeleteUser"
            :on-sort-first-name="handleFirstNameSort"
            :on-toggle-first-name-sort="handleFirstNameSortToggle"
            :on-filter-first-name-letter="handleFirstNameLetter"
            :can-read-users="canReadUsers"
            :can-update-users="canUpdateUsers"
            :can-delete-users="canDeleteUsers"
            :can-assign-roles="canAssignRoles"
            :on-assign-role="openAssignRoleModal"
          />
        </div>

        <footer class="pagination">
          <div class="pagination-info">
            <label for="page-size">Rows per page</label>
            <select id="page-size" :value="pageSize" @change="changePageSize">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span>
              Showing
              {{ totalUsers === 0 ? 0 : (currentPage - 1) * pageSize + 1 }}–{{
                Math.min(currentPage * pageSize, totalUsers)
              }}
              of {{ totalUsers }} users
            </span>
          </div>

          <div class="pagination-actions">
            <button
              class="page-button"
              :disabled="!hasPrevious || usersLoading"
              @click="previousPage"
            >
              ‹ Previous
            </button>
            <span class="page-indicator">
              {{ currentPage }} / {{ totalPages || 1 }}
            </span>
            <button
              class="page-button"
              :disabled="!hasNext || usersLoading"
              @click="nextPage"
            >
              Next ›
            </button>
          </div>
        </footer>
      </section>
    </section>

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
            class="close-button"
            type="button"
            aria-label="Close"
            @click="showProfileForm = false"
          >
            ×
          </button>
        </div>

        <form @submit.prevent="saveProfile" novalidate>
          <div class="form-field">
            <label for="first-name">First name</label>
            <input
              id="first-name"
              v-model="profileForm.first_name"
              :class="{ 'invalid-input': profileErrors.first_name }"
              autocomplete="given-name"
              maxlength="40"
              @input="delete profileErrors.first_name"
            />
            <small v-if="profileErrors.first_name" class="field-error">
              {{ profileErrors.first_name }}
            </small>
          </div>

          <div class="form-field">
            <label for="last-name">Last name</label>
            <input
              id="last-name"
              v-model="profileForm.last_name"
              :class="{ 'invalid-input': profileErrors.last_name }"
              autocomplete="family-name"
              maxlength="40"
              @input="delete profileErrors.last_name"
            />
            <small v-if="profileErrors.last_name" class="field-error">
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
            <small v-if="profileErrors.email" class="field-error">
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
    <ConfirmationModal
      v-model="showDeleteConfirmation"
      title="Delete User?"
      :message="
        userToDelete
          ? `Are you sure you want to delete ${userToDelete.first_name} ${userToDelete.last_name} (${userToDelete.email})? This action cannot be undone.`
          : 'Are you sure you want to delete this user?'
      "
      confirm-text="Delete User"
      cancel-text="Cancel"
      variant="danger"
      :loading="deletingUser"
      @confirm="confirmDeleteUser"
      @cancel="userToDelete = null"
    />
    <UserFormModal
      v-if="showUserModal"
      :mode="userFormMode"
      :selected-user="selectedUser"
      @close="showUserModal = false"
      @saved="handleUserSaved"
    />
    <div
      v-if="showAssignRoleModal"
      class="modal-backdrop"
      @click.self="closeAssignRoleModal"
    >
      <section
        class="profile-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assign-role-title"
      >
        <div class="modal-heading">
          <div>
            <h2 id="assign-role-title">Assign User Role</h2>
            <p>
              Select a role for
              <strong>
                {{ selectedUserForRole?.first_name }}
                {{ selectedUserForRole?.last_name }}
              </strong>
            </p>
          </div>

          <button
            class="close-button"
            type="button"
            aria-label="Close"
            :disabled="assigningRole"
            @click="closeAssignRoleModal"
          >
            ×
          </button>
        </div>

        <div v-if="loadingRoles" class="table-state">
          Loading available roles...
        </div>

        <form v-else @submit.prevent="submitRoleAssignment">
          <div class="form-field">
            <label for="assign-role">Select Role</label>

            <select id="assign-role" v-model="selectedRoleId" required>
              <option value="" disabled>Select a role</option>

              <option value="none">No Role</option>

              <option
                v-for="role in availableRoles"
                :key="role.role_id"
                :value="String(role.role_id)"
              >
                {{ role.role_name }}
              </option>
            </select>
          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="cancel-button"
              :disabled="assigningRole"
              @click="closeAssignRoleModal"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="primary-button"
              :disabled="assigningRole || !selectedRoleId"
            >
              {{ assigningRole ? "Saving..." : "Assign Role" }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </main>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.dashboard {
  min-height: 100vh;
  background: #f3f4f6;
  color: #151d2e;
  font-family: Inter, Arial, Helvetica, sans-serif;
}

.topbar {
  min-height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 10px 2.3%;
  background: #fff;
  border-bottom: 1px solid #e4e7ec;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  color: #151d2e;
  text-decoration: none;
  font-size: 19px;
  font-weight: 750;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: #2864ed;
  color: white;
  font-size: 11px;
  font-weight: 800;
}

.topbar-user {
  display: flex;
  align-items: center;
  gap: 14px;
  color: #475467;
  font-size: 13px;
}

.avatar-small,
.avatar-large {
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: #dbeafe;
  color: #2864ed;
  font-weight: 750;
}

.avatar-small {
  width: 34px;
  height: 34px;
}

.logout-button,
.primary-button {
  border: 0;
  border-radius: 7px;
  background: #2864ed;
  color: white;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
}

.logout-button:hover,
.primary-button:hover:not(:disabled) {
  background: #1d4ed8;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px 2.3% 30px;
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

.profile-card,
.stat-card,
.users-card {
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
  align-items: center;
  flex-direction: column;
  gap: 8px;
  color: #667085;
  font-size: 12px;
}

.avatar-large {
  width: 80px;
  height: 80px;
  font-size: 25px;
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

.email-value {
  overflow-wrap: anywhere;
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
.cancel-button,
.page-button {
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

.users-card {
  overflow: hidden;
}

.table-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
}

.table-heading h2 {
  margin: 0;
  font-size: 18px;
}

.table-scroll {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  white-space: nowrap;
}

thead {
  background: #f8fafc;
}

th,
td {
  padding: 12px 18px;
  border-bottom: 1px solid #e8ebf0;
  font-size: 12px;
}

th {
  color: #667085;
  font-size: 10px;
  font-weight: 750;
  text-transform: uppercase;
}

td {
  color: #344054;
}

td strong {
  color: #151d2e;
}

tbody tr:hover {
  background: #f9fafb;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 74px;
  padding: 5px 12px;
  border-radius: 30px;
  font-size: 11px;
  font-weight: 700;
}

.status-badge.valid {
  background: #dcfce7;
  color: #15803d;
}

.status-badge.invalid {
  background: #fee2e2;
  color: #b91c1c;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 9px;
}

.delete-button {
  border: 1px solid #ef4444;
  border-radius: 7px;
  background: #fff;
  color: #dc2626;
  padding: 8px 13px;
  font-size: 12px;
  font-weight: 650;
  cursor: pointer;
}

.delete-button:hover {
  background: #fef2f2;
}

.edit-button {
  border: 1px solid #2864ed;
  border-radius: 7px;
  background: #fff;
  color: #2864ed;
  padding: 8px 13px;
  font-size: 12px;
  font-weight: 650;
  cursor: pointer;
}

.edit-button:hover {
  background: #eff6ff;
}

.edit-button,
.delete-button {
  white-space: nowrap;
}

.password-cell {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #667085;
  letter-spacing: 1px;
}

.eye-button {
  border: 0;
  background: transparent;
  color: #2864ed;
  font-size: 15px;
  cursor: pointer;
}

.password-tooltip {
  position: absolute;
  z-index: 2;
  top: 27px;
  left: 0;
  width: 230px;
  white-space: normal;
  padding: 10px 12px;
  border: 1px solid #e1e5eb;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 6px 20px #10182818;
  color: #344054;
  font-size: 12px;
  letter-spacing: 0;
}

.table-state {
  padding: 35px 20px;
  color: #667085;
  text-align: center;
  font-size: 13px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  padding: 16px 20px;
}

.pagination-info,
.pagination-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  color: #667085;
  font-size: 11px;
}

.pagination select {
  min-width: 65px;
  padding: 7px 9px;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  background: white;
  color: #344054;
}

.page-button {
  border-color: #d0d5dd;
  color: #344054;
}

.page-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.page-indicator {
  color: #344054;
  font-weight: 650;
}

.notice {
  padding: 11px 14px;
  margin: 0 0 14px;
  border: 1px solid;
  border-radius: 8px;
  font-size: 13px;
}

.notice.success {
  color: #067647;
  background: #ecfdf3;
  border-color: #abefc6;
}

.notice.error {
  color: #b42318;
  background: #fef3f2;
  border-color: #fecdca;
}

.modal-backdrop {
  position: fixed;
  z-index: 10;
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
  background: white;
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
  .topbar {
    padding: 12px 15px;
  }

  .topbar-user {
    gap: 8px;
  }

  .topbar-user > span:first-child {
    display: none;
  }

  .content {
    padding: 20px 12px;
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

  .profile-edit-button {
    top: 15px;
    right: 15px;
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

  .table-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .pagination {
    align-items: flex-start;
    flex-direction: column;
  }

  .pagination-info,
  .pagination-actions {
    gap: 8px;
  }
}

.grid-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px 16px;
}

.grid-search,
.letter-filter {
  min-height: 38px;
  padding: 8px 12px;
  border: 1px solid #d0d5dd;
  border-radius: 7px;
  background: #fff;
  color: #344054;
  font-size: 13px;
}

.grid-search {
  width: min(100%, 320px);
}

.letter-filter {
  min-width: 170px;
}

.grid-search:focus,
.letter-filter:focus {
  outline: 2px solid #2864ed30;
  border-color: #2864ed;
}

@media (max-width: 600px) {
  .grid-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .grid-search,
  .letter-filter {
    width: 100%;
  }
}

.ag-grid-wrapper {
  width: 100%;
  height: 500px;
  padding: 0 12px;
}

.ag-grid-wrapper :deep(.ag-root-wrapper) {
  border: 1px solid #e1e5eb;
  border-radius: 8px;
}

.ag-grid-wrapper :deep(.ag-header) {
  background: #f8fafc;
}

.ag-grid-wrapper :deep(.ag-header-cell-text) {
  color: #667085;
  font-size: 11px;
  font-weight: 750;
  text-transform: uppercase;
}

.ag-grid-wrapper :deep(.ag-cell) {
  display: flex;
  align-items: center;
  color: #344054;
  font-size: 12px;
}

@media (max-width: 600px) {
  .ag-grid-wrapper {
    height: 450px;
    padding: 0 8px;
  }
}

/* Action buttons */
:deep(.row-actions) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 100%;
}

:deep(.row-actions button) {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

:deep(.row-actions .edit-button) {
  border: 1px solid #2864ed;
  background: #eff6ff;
  color: #2864ed;
}

:deep(.row-actions .edit-button:hover) {
  background: #dbeafe;
}

:deep(.row-actions .delete-button) {
  border: 1px solid #ef4444;
  background: #fef2f2;
  color: #dc2626;
}

:deep(.row-actions .delete-button:hover) {
  background: #fee2e2;
}

/* Account status badges */
:deep(.status-pill) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 76px;
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.2;
}

:deep(.status-valid) {
  color: #15803d;
  background: #dcfce7;
}

:deep(.status-invalid) {
  color: #b91c1c;
  background: #fee2e2;
}

:deep(.status-dot) {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
.form-field select {
  width: 100%;
  padding: 11px 12px;
  border: 1px solid #d0d5dd;
  border-radius: 7px;
  background: white;
  color: #151d2e;
  font: inherit;
  font-size: 13px;
}
</style>
