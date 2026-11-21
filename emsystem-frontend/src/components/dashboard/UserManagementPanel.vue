
<script setup>
import {
  computed,
  defineAsyncComponent,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
import { useRouter } from "vue-router";

import { useUsers } from "../../composables/useUsers";
import { useAuthStore } from "../../stores/authStore";
import { useToast } from "../../composables/useToast";

import { deleteUser } from "../../services/userService";
import {
  getRoles,
  assignUserRole,
} from "../../services/roleService";

import UserFormModal from "../UserFormModal.vue";
import ConfirmationModal from "../ConfirmationModal.vue";

const emit = defineEmits(["stats-update"]);

const UserGrid = defineAsyncComponent(
  () => import("../UserGrid.vue"),
);

const router = useRouter();
const authStore = useAuthStore();
const { showToast } = useToast();

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

// --------------------------------------------------
// Permissions
// --------------------------------------------------

const canCreateUsers = computed(() =>
  authStore.hasPermission("users.create"),
);

const canReadUsers = computed(() =>
  authStore.hasPermission("users.read"),
);

const canUpdateUsers = computed(() =>
  authStore.hasPermission("users.update"),
);

const canDeleteUsers = computed(() =>
  authStore.hasPermission("users.delete"),
);

const canAssignRoles = computed(
  () =>
    authStore.hasPermission("users.update") &&
    authStore.hasPermission("roles.read"),
);

// --------------------------------------------------
// User statistics
// --------------------------------------------------

function isAccountValid(item) {
  if (!item.valid_until) return false;

  const expiry = new Date(item.valid_until);

  if (Number.isNaN(expiry.getTime())) return false;

  // The account remains valid through its expiry date.
  expiry.setHours(23, 59, 59, 999);

  return expiry >= new Date();
}

const validOnPage = computed(() =>
  users.value.filter(isAccountValid).length,
);

const invalidOnPage = computed(() =>
  users.value.filter((item) => !isAccountValid(item)).length,
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

watch(
  [totalUsers, validOnPage, invalidOnPage, newThisMonthOnPage],
  ([total, valid, invalid, recent]) => {
    emit("stats-update", {
      totalUsers: total,
      validOnPage: valid,
      invalidOnPage: invalid,
      newThisMonthOnPage: recent,
    });
  },
  { immediate: true },
);

// --------------------------------------------------
// API error notification
// --------------------------------------------------

watch(errorMessage, (message) => {
  if (message) {
    showToast(message, "error");
  }
});

// --------------------------------------------------
// User form modal
// --------------------------------------------------

const showUserModal = ref(false);
const userFormMode = ref("create");
const selectedUser = ref(null);


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

function closeUserModal() {
  showUserModal.value = false;
  selectedUser.value = null;
}

async function handleUserSaved() {
    const message =
    userFormMode.value === "create"
      ? "User created successfully."
      : "User updated successfully.";

  showUserModal.value = false;
  selectedUser.value = null;

  showToast(message, "success");

  await loadUsers(currentPage.value);
}

// --------------------------------------------------
// Delete user
// --------------------------------------------------

const showDeleteConfirmation = ref(false);
const userToDelete = ref(null);
const deletingUser = ref(false);

function handleDeleteUser(item) {
  userToDelete.value = item;
  showDeleteConfirmation.value = true;
}

function closeDeleteConfirmation() {
  if (deletingUser.value) return;

  showDeleteConfirmation.value = false;
  userToDelete.value = null;
}

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

    showToast(
      response.data.message || "User deleted successfully.",
      "success",
    );

    showDeleteConfirmation.value = false;
    userToDelete.value = null;
  } catch (error) {
    if (error.response?.status === 401) {
      authStore.logout();
      router.replace("/");
      return;
    }

    showToast(
      error.response?.data?.error ||
        error.response?.data?.message ||
        "Unable to delete this user.",
      "error",
    );

    console.error(
      "Delete failed:",
      error.response?.data || error.message,
    );
  } finally {
    deletingUser.value = false;
  }
}

// --------------------------------------------------
// Role assignment
// --------------------------------------------------

const showAssignRoleModal = ref(false);
const selectedUserForRole = ref(null);
const availableRoles = ref([]);
const selectedRoleId = ref("");
const loadingRoles = ref(false);
const assigningRole = ref(false);

async function openAssignRoleModal(item) {
  if (!canAssignRoles.value) return;

  selectedUserForRole.value = item;
  selectedRoleId.value = "";
  availableRoles.value = [];
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
    selectedUserForRole.value = null;
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
  if (
    !selectedUserForRole.value ||
    !selectedRoleId.value ||
    assigningRole.value
  ) {
    return;
  }

  assigningRole.value = true;

  try {
    const roleId =
      selectedRoleId.value === "none"
        ? null
        : Number(selectedRoleId.value);

    const response = await assignUserRole(
      selectedUserForRole.value.user_id,
      roleId,
    );

    showToast(
      response.data.message || "User role updated successfully.",
      "success",
    );

    // Close directly because assigningRole is still true here.
    showAssignRoleModal.value = false;
    selectedUserForRole.value = null;
    selectedRoleId.value = "";

    await loadUsers(currentPage.value);
  } catch (error) {
    if (error.response?.status === 401) {
      authStore.logout();
      router.replace("/");
      return;
    }

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

// --------------------------------------------------
// Sorting and filtering
// --------------------------------------------------

const searchInput = ref("");
let searchTimeout = null;

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
  await updateFilters({ letter });
}

function handleSearch() {
  clearTimeout(searchTimeout);

  searchTimeout = setTimeout(() => {
    updateFilters({
      search: searchInput.value.trim(),
    });
  }, 500);
}

// --------------------------------------------------
// Pagination
// --------------------------------------------------

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

// --------------------------------------------------
// Lifecycle
// --------------------------------------------------

onMounted(() => {
  loadUsers();
});

onBeforeUnmount(() => {
  clearTimeout(searchTimeout);
});
</script>

<template>
  <section class="users-card">
    <div class="table-heading">
      <h2>User Management</h2>

      <button
        v-if="canCreateUsers"
        type="button"
        class="primary-button"
        @click="openCreateUserModal"
      >
        + Add New User
      </button>
    </div>

    <div class="grid-toolbar">
      <input
        v-model="searchInput"
        type="search"
        class="grid-search"
        placeholder="Search name or email..."
        aria-label="Search users"
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

    <!-- Pagination -->
    <footer class="pagination">
      <div class="pagination-info">
        <label for="page-size">Rows per page</label>

        <select
          id="page-size"
          :value="pageSize"
          :disabled="usersLoading"
          @change="changePageSize"
        >
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>

        <span>
          Showing
          {{
            totalUsers === 0
              ? 0
              : (currentPage - 1) * pageSize + 1
          }}–{{
            Math.min(currentPage * pageSize, totalUsers)
          }}
          of {{ totalUsers }} users
        </span>
      </div>

      <div class="pagination-actions">
        <button
          type="button"
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
          type="button"
          class="page-button"
          :disabled="!hasNext || usersLoading"
          @click="nextPage"
        >
          Next ›
        </button>
      </div>
    </footer>
  </section>

  <!-- Create and edit user modal -->
  <UserFormModal
    v-if="showUserModal"
    :mode="userFormMode"
    :selected-user="selectedUser"
    @close="closeUserModal"
    @saved="handleUserSaved"
  />

  <!-- Delete confirmation -->
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
    @cancel="closeDeleteConfirmation"
  />

  <!-- Assign role modal -->
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
          type="button"
          class="close-button"
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

      <form
        v-else
        @submit.prevent="submitRoleAssignment"
      >
        <div class="form-field">
          <label for="assign-role">Select Role</label>

          <select
            id="assign-role"
            v-model="selectedRoleId"
            required
          >
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
</template>

<style scoped>
.users-card {
  overflow: hidden;
  border: 1px solid #e1e5eb;
  border-radius: 13px;
  background: #fff;
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

.grid-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px 16px;
}

.grid-search {
  width: min(100%, 320px);
  min-height: 38px;
  padding: 8px 12px;
  border: 1px solid #d0d5dd;
  border-radius: 7px;
  background: #fff;
  color: #344054;
  font-size: 13px;
}

.grid-search:focus {
  outline: 2px solid #2864ed30;
  border-color: #2864ed;
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

.ag-grid-wrapper :deep(.row-actions) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 100%;
}

.ag-grid-wrapper :deep(.row-actions button) {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.ag-grid-wrapper :deep(.row-actions .edit-button) {
  border: 1px solid #2864ed;
  background: #eff6ff;
  color: #2864ed;
}

.ag-grid-wrapper :deep(.row-actions .delete-button) {
  border: 1px solid #ef4444;
  background: #fef2f2;
  color: #dc2626;
}

.ag-grid-wrapper :deep(.status-pill) {
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

.ag-grid-wrapper :deep(.status-valid) {
  color: #15803d;
  background: #dcfce7;
}

.ag-grid-wrapper :deep(.status-invalid) {
  color: #b91c1c;
  background: #fee2e2;
}

.ag-grid-wrapper :deep(.status-dot) {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

/* Pagination */
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
  background: #fff;
  color: #344054;
}

.page-button {
  border: 1px solid #d0d5dd;
  border-radius: 7px;
  background: #fff;
  color: #344054;
  padding: 8px 13px;
  font-size: 12px;
  font-weight: 650;
  cursor: pointer;
}

.page-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.page-indicator {
  color: #344054;
  font-weight: 650;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  z-index: 30;
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

.close-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.form-field select {
  width: 100%;
  padding: 11px 12px;
  border: 1px solid #d0d5dd;
  border-radius: 7px;
  background: #fff;
  color: #151d2e;
  font: inherit;
  font-size: 13px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}

.cancel-button {
  border: 1px solid #d0d5dd;
  border-radius: 7px;
  background: #fff;
  color: #344054;
  padding: 8px 13px;
  font-size: 12px;
  font-weight: 650;
  cursor: pointer;
}

.cancel-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.table-state {
  padding: 35px 20px;
  color: #667085;
  text-align: center;
  font-size: 13px;
}

@media (max-width: 600px) {
  .table-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .grid-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .grid-search {
    width: 100%;
  }

  .ag-grid-wrapper {
    height: 450px;
    padding: 0 8px;
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
</style>
