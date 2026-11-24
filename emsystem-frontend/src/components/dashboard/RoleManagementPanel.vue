<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../../stores/authStore";
import { useUsers } from "../../composables/useUsers";
import RoleFormModal from "./RoleFormModal.vue";
import ConfirmationModal from "../../components/ConfirmationModal.vue";
import RoleBadge from "../RoleBadge.vue";
import { useToast } from "../../composables/useToast";

import {
  getRoles,
  getRoleDetails,
  getPermissions,
  createRole,
  updateRole,
  deleteRole,
  assignUserRole,
} from "../../services/roleService";

// --------------------------------------------------
// Router and users
// --------------------------------------------------

const router = useRouter();
const authStore = useAuthStore();
const { showToast } = useToast();

const {
  users,
  loading,
  errorMessage,
  totalUsers,
  currentPage,
  pageSize,
  totalPages,
  hasNext,
  hasPrevious,
  filters,
  loadUsers,
  updateFilters,
} = useUsers(router);

// --------------------------------------------------
// Role state
// --------------------------------------------------

const roles = ref([]);
const loadingRoles = ref(false);
const roleError = ref("");
const roleActionError = ref("");

const totalRoles = computed(() => roles.value.length);

// --------------------------------------------------
// Role List pagination (client-side)
// --------------------------------------------------

const roleCurrentPage = ref(1);
const rolePageSize = ref(10);

const roleTotalPages = computed(() =>
  Math.max(1, Math.ceil(totalRoles.value / rolePageSize.value)),
);

const paginatedRoles = computed(() => {
  const start = (roleCurrentPage.value - 1) * rolePageSize.value;

  return roles.value.slice(start, start + rolePageSize.value);
});

const roleStartRecord = computed(() =>
  totalRoles.value === 0
    ? 0
    : (roleCurrentPage.value - 1) * rolePageSize.value + 1,
);

const roleEndRecord = computed(() =>
  Math.min(roleCurrentPage.value * rolePageSize.value, totalRoles.value),
);

function goToRolePage(page) {
  if (page < 1 || page > roleTotalPages.value) return;

  roleCurrentPage.value = page;
}

function handleRolePageSizeChange() {
  roleCurrentPage.value = 1;
}

watch(roleTotalPages, (newTotalPages) => {
  if (roleCurrentPage.value > newTotalPages) {
    roleCurrentPage.value = newTotalPages;
  }
});

// --------------------------------------------------
// Permissions
// --------------------------------------------------

const canReadRoles = computed(() => authStore.hasPermission("roles.read"));

const canCreateRoles = computed(() => authStore.hasPermission("roles.create"));

const canUpdateRoles = computed(() => authStore.hasPermission("roles.update"));

const canDeleteRoles = computed(() => authStore.hasPermission("roles.delete"));

const canReadUsers = computed(() => authStore.hasPermission("users.read"));

const canUpdateUsers = computed(() => authStore.hasPermission("users.update"));

// Role assignment requires permission to manage users
// and permission to read the available roles.
const canAssignRoles = computed(
  () => canReadRoles.value && canUpdateUsers.value,
);

// --------------------------------------------------
// Role permissions
// --------------------------------------------------

const availablePermissions = ref([]);

const normalizedPermissions = computed(() =>
  availablePermissions.value.map((permission) => ({
    id: permission.permission_id,
    value: permission.codename,
    label: permission.permission_name,
    description: permission.description,
  })),
);

async function loadPermissions() {
  try {
    const response = await getPermissions();

    availablePermissions.value = response.data.permissions || [];
  } catch (error) {
    console.error("Failed to load permissions:", error);

    roleActionError.value =
      error.response?.data?.message || "Failed to load available permissions.";
  }
}

// --------------------------------------------------
// Role statistics
// --------------------------------------------------

const assignedUsersCount = computed(() => {
  return roles.value.reduce(
    (total, role) => total + Number(role.total_users || 0),
    0,
  );
});

const unassignedUsersCount = computed(() => {
  return Math.max(0, totalUsers.value - assignedUsersCount.value);
});

// --------------------------------------------------
// Helpers
// --------------------------------------------------

function formatDate(date) {
  if (!date) return "—";

  return new Date(date).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function getErrorMessage(error, fallback) {
  return (
    error.response?.data?.message || error.response?.data?.error || fallback
  );
}

// --------------------------------------------------
// Load roles
// --------------------------------------------------

async function loadRoles() {
  loadingRoles.value = true;
  roleError.value = "";

  try {
    const response = await getRoles();

    roles.value = response.data.roles || [];
  } catch (error) {
    roleError.value = getErrorMessage(
      error,
      "Failed to load role information.",
    );
  } finally {
    loadingRoles.value = false;
  }
}
// --------------------------------------------------
// Create and edit role modal
// --------------------------------------------------

const showRoleFormModal = ref(false);
const roleFormMode = ref("create");
const selectedRoleForEdit = ref(null);
const savingRole = ref(false);
const roleFormError = ref("");

function openCreateRoleModal() {
  selectedRoleForEdit.value = null;
  roleFormMode.value = "create";
  roleFormError.value = "";
  showRoleFormModal.value = true;
}

async function openEditRoleModal(role) {
  roleFormError.value = "";

  try {
    const response = await getRoleDetails(role.role_id);

    selectedRoleForEdit.value = response.data.role;
    roleFormMode.value = "edit";
    showRoleFormModal.value = true;
  } catch (error) {
    roleActionError.value = getErrorMessage(
      error,
      "Unable to load role details for editing.",
    );
  }
}

async function handleRoleSubmit(roleData) {
  savingRole.value = true;
  roleFormError.value = "";

  try {
    if (roleFormMode.value === "edit") {
      await updateRole(selectedRoleForEdit.value.role_id, roleData);

      showToast("Role updated successfully.", "success");
    } else {
      await createRole(roleData);

      showToast("Role created successfully.", "success");
    }

    showRoleFormModal.value = false;
    selectedRoleForEdit.value = null;

    await loadRoles();
  } catch (error) {
    const message = getErrorMessage(
      error,
      "Failed to save role. Please try again.",
    );

    roleFormError.value = message;
    showToast(message, "error");
  } finally {
    savingRole.value = false;
  }
}
// --------------------------------------------------
// Delete role confirmation
// --------------------------------------------------

const showDeleteConfirmation = ref(false);
const roleToDelete = ref(null);
const deletingRole = ref(false);

function openDeleteConfirmation(role) {
  roleToDelete.value = role;
  roleActionError.value = "";
  showDeleteConfirmation.value = true;
}

function cancelDeleteRole() {
  if (deletingRole.value) return;

  showDeleteConfirmation.value = false;
  roleToDelete.value = null;
}

async function confirmDeleteRole() {
  if (!roleToDelete.value) return;

  deletingRole.value = true;
  roleActionError.value = "";

  try {
    const response = await deleteRole(roleToDelete.value.role_id);

    showToast(response.data.message || "Role deleted successfully.", "success");

    showDeleteConfirmation.value = false;
    roleToDelete.value = null;

    await Promise.all([loadRoles(), loadUsers(currentPage.value)]);
  } catch (error) {
    const message = getErrorMessage(error, "Unable to delete this role.");

    roleActionError.value = message;
    showToast(message, "error");
  } finally {
    deletingRole.value = false;
  }
}

// --------------------------------------------------
// Role details modal
// --------------------------------------------------

const showRoleDetails = ref(false);
const selectedRoleDetails = ref(null);
const loadingRoleDetails = ref(false);
const roleDetailsError = ref("");

async function openRoleDetails(roleId) {
  showRoleDetails.value = true;
  loadingRoleDetails.value = true;
  selectedRoleDetails.value = null;
  roleDetailsError.value = "";

  try {
    const response = await getRoleDetails(roleId);

    selectedRoleDetails.value = response.data.role;
  } catch (error) {
    const message = getErrorMessage(
      error,
      "Failed to load role details.",
    );
    roleDetailsError.value = message;
    showToast(message, "error");
  } finally {
    loadingRoleDetails.value = false;
  }
}

function closeRoleDetails() {
  showRoleDetails.value = false;
  selectedRoleDetails.value = null;
  roleDetailsError.value = "";
}

// --------------------------------------------------
// User search, sorting and filtering
// --------------------------------------------------

const searchInput = ref("");
const selectedLetter = ref("");
let searchTimeout = null;

// Debounced search — same behavior as User Management.
function handleSearch() {
  clearTimeout(searchTimeout);

  searchTimeout = setTimeout(() => {
    updateFilters({
      search: searchInput.value.trim(),
    });
  }, 500);
}

// Sort users by first name.
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

// Toggle first-name sorting.
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

// Filter users by first-name initial.
async function handleFirstNameLetter(letter) {
  selectedLetter.value = letter;

  await updateFilters({
    letter,
  });
}

// Clear search and alphabet filter.
async function clearUserFilters() {
  clearTimeout(searchTimeout);

  searchInput.value = "";
  selectedLetter.value = "";

  await updateFilters({
    search: "",
    letter: "",
    sort_by: "user_id",
    order: "asc",
  });
}

// Prevent pending debounce callbacks after unmount.
onBeforeUnmount(() => {
  clearTimeout(searchTimeout);
});

async function handleUserPageSizeChange(event) {
  pageSize.value = Number(event.target.value);
  await loadUsers(1);
}

// --------------------------------------------------
// Assign roles to users
// --------------------------------------------------

const selectedRoles = ref({});
const assigningUserId = ref(null);
// const assignmentMessage = ref("");
// const assignmentError = ref("");

function updateSelectedRole(userId, roleId) {
  selectedRoles.value[userId] = roleId;
}

async function handleAssignRole(user) {
  const roleId = selectedRoles.value[user.user_id];

  if (!roleId) {
    showToast("Please select a role first.", "error");
    return;
  }

  assigningUserId.value = user.user_id;

  try {
    const response = await assignUserRole(
      user.user_id,
      Number(roleId),
    );

    showToast(
      response.data.message ||
        `Role assigned successfully to ${user.first_name}.`,
      "success",
    );

    await Promise.all([
      loadUsers(currentPage.value),
      loadRoles(),
    ]);

    delete selectedRoles.value[user.user_id];
  } catch (error) {
    showToast(
      getErrorMessage(error, "Failed to assign role."),
      "error",
    );
  } finally {
    assigningUserId.value = null;
  }
}

// --------------------------------------------------
// Initial loading
// --------------------------------------------------

// onMounted(async () => {
//   await Promise.all([loadRoles(), loadPermissions(), loadUsers(1)]);
// });
onMounted(async () => {
  const requests = [];

  if (canReadRoles.value) {
    requests.push(loadRoles());
  }

  if (canCreateRoles.value || canUpdateRoles.value) {
    requests.push(loadPermissions());
  }

  if (canReadUsers.value) {
    requests.push(loadUsers(1));
  }

  await Promise.all(requests);
});
</script>

<template>
  <section class="roles-panel">
    <!-- Role Statistics -->
    <section class="stats-grid">
      <article class="stat-card">
        <span class="stat-icon blue">●</span>
        <div>
          <strong class="stat-number">
            {{ loading ? "..." : totalUsers }}
          </strong>
          <span class="stat-label">Total Enrolled Users</span>
        </div>
      </article>

      <article class="stat-card">
        <span class="stat-icon green">●</span>
        <div>
          <strong class="stat-number">
            {{ loadingRoles ? "..." : totalRoles }}
          </strong>
          <span class="stat-label">Total Roles</span>
        </div>
      </article>

      <article class="stat-card">
        <span class="stat-icon amber">●</span>
        <div>
          <strong class="stat-number">
            {{ assignedUsersCount === null ? "..." : assignedUsersCount }}
          </strong>
          <span class="stat-label">Users with a Role</span>
        </div>
      </article>

      <article class="stat-card">
        <span class="stat-icon red">●</span>
        <div>
          <strong class="stat-number">
            {{ unassignedUsersCount === null ? "..." : unassignedUsersCount }}
          </strong>
          <span class="stat-label">Unassigned Users</span>
        </div>
      </article>
    </section>

    <!-- Role List -->
    <div class="role-list-card">
      <div class="section-header">
        <div>
          <h2>Role List</h2>
          <p>Manage roles and their assigned users.</p>
        </div>

        <button
          v-if="canCreateRoles"
          class="primary-button"
          type="button"
          @click="openCreateRoleModal"
        >
          + Create Role
        </button>
      </div>

      <p v-if="roleActionError" class="error-message">
        {{ roleActionError }}
      </p>

      <div v-if="loadingRoles" class="state-message">Loading roles...</div>

      <div v-else-if="roleError" class="error-message">
        {{ roleError }}

        <button type="button" @click="loadRoles">Retry</button>
      </div>

      <div v-else-if="roles.length === 0" class="state-message">
        No roles found.
      </div>

      <div v-else class="table-wrapper">
        <table class="roles-table">
          <thead>
            <tr>
              <th>Role Name</th>
              <th>Description</th>
              <th>Assigned Users</th>
              <th>Created Date</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="role in paginatedRoles" :key="role.role_id">
              <td>
                <!-- <span class="role-name">
                  {{ role.role_name }}
                </span> -->
                <RoleBadge
                  :role-name="role.role_name"
                  :role-id="role.role_id"
                />
              </td>

              <td class="description-cell">
                {{ role.description || "No description available" }}
              </td>

              <td>
                <span class="user-count">
                  {{ role.total_users ?? 0 }}
                </span>
              </td>

              <td>
                {{ formatDate(role.created_at) }}
              </td>

              <td>
                <div class="role-actions">
                  <button
                    v-if="canReadRoles"
                    type="button"
                    class="role-action-btn details-btn"
                    @click="openRoleDetails(role.role_id)"
                  >
                    Details
                  </button>

                  <button
                    v-if="canUpdateRoles"
                    type="button"
                    class="role-action-btn edit-btn"
                    @click="openEditRoleModal(role)"
                  >
                    Edit
                  </button>

                  <button
                    v-if="canDeleteRoles"
                    type="button"
                    class="role-action-btn delete-btn"
                    @click="openDeleteConfirmation(role)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Role List Pagination -->
      <div class="role-list-footer">
        <!-- Rows per page -->
        <div class="pagination-size">
          <label for="role-page-size">Rows per page</label>

          <select
            id="role-page-size"
            v-model.number="rolePageSize"
            class="page-size-select"
            @change="handleRolePageSizeChange"
          >
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </div>

        <!-- Record range -->
        <span class="pagination-info">
          Showing {{ roleStartRecord }}–{{ roleEndRecord }} of
          {{ totalRoles }} roles
        </span>

        <!-- Navigation -->
        <div class="pagination-actions">
          <button
            type="button"
            class="pagination-button"
            :disabled="roleCurrentPage === 1"
            @click="goToRolePage(roleCurrentPage - 1)"
          >
            ‹ Previous
          </button>

          <span class="page-indicator">
            {{ roleCurrentPage }} / {{ roleTotalPages }}
          </span>

          <button
            type="button"
            class="pagination-button"
            :disabled="roleCurrentPage === roleTotalPages"
            @click="goToRolePage(roleCurrentPage + 1)"
          >
            Next ›
          </button>
        </div>
      </div>
    </div>

    <!-- Assign Roles to Users -->
    <div v-if="canReadUsers" class="role-list-card assignment-card">
      <div class="section-header">
        <div>
          <h2>Assign Roles to Users</h2>
          <p>View users and manage their assigned roles.</p>
        </div>
      </div>

      <!-- User Search and Filters -->
      <div class="assignment-toolbar">
        <input
          v-model="searchInput"
          type="search"
          class="search-input"
          placeholder="Search name or email..."
          aria-label="Search users by name or email"
          @input="handleSearch"
        />

        <!-- Alphabetical filter -->
        <select
          v-model="selectedLetter"
          class="filter-select"
          aria-label="Filter users by first name"
          @change="handleFirstNameLetter(selectedLetter)"
        >
          <option value="">All Names</option>

          <option
            v-for="letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"
            :key="letter"
            :value="letter"
          >
            {{ letter }}
          </option>
        </select>

        <!-- Clear filters -->
        <button
          v-if="
            searchInput || selectedLetter || filters.sort_by === 'first_name'
          "
          type="button"
          class="clear-search-button"
          @click="clearUserFilters"
        >
          Clear
        </button>
        <!-- <p v-else class="state-message">
          You do not have permission to view users.
        </p> -->
      </div>

      <!-- <p v-if="assignmentMessage" class="success-message">
        {{ assignmentMessage }}
      </p>

      <p v-if="assignmentError" class="error-message">
        {{ assignmentError }}
      </p> -->

      <div v-if="loading" class="state-message">Loading users...</div>

      <div v-else-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div v-else-if="users.length === 0" class="state-message">
        No users found.
      </div>

      <div v-else class="table-wrapper">
        <table class="roles-table">
          <thead>
            <tr>
              <!-- <th>User</th> -->
              <th>
                <button
                  type="button"
                  class="sortable-header"
                  @click="handleFirstNameSortToggle"
                >
                  User

                  <span v-if="filters.sort_by === 'first_name'">
                    {{ filters.order === "asc" ? "↑" : "↓" }}
                  </span>

                  <span v-else>↕</span>
                </button>
              </th>
              <th>Email</th>
              <th>Current Role</th>
              <th v-if="canAssignRoles">Assign Role</th>
              <th v-if="canAssignRoles">Action</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="user in users" :key="user.user_id">
              <!-- <td>{{ user.first_name }} {{ user.last_name }}</td> -->
              <td>
                <span class="assignment-user-name">
                  {{ user.first_name }} {{ user.last_name }}
                </span>
              </td>

              <td>{{ user.email }}</td>

              <td>
                <!-- {{ user.role?.role_name || "Unassigned" }} -->
                <RoleBadge
                  v-if="user.role"
                  :role-name="user.role.role_name"
                  :role-id="user.role.role_id"
                />
                <RoleBadge v-else role-name="Unassigned" />
              </td>

              <td v-if="canAssignRoles">
                <select
                  class="role-select"
                  :value="selectedRoles[user.user_id] || ''"
                  @change="
                    updateSelectedRole(user.user_id, $event.target.value)
                  "
                >
                  <option value="">Select role</option>

                  <option
                    v-for="role in roles"
                    :key="role.role_id"
                    :value="role.role_id"
                  >
                    {{ role.role_name }}
                  </option>
                </select>
              </td>

              <td v-if="canAssignRoles">
                <button
                  class="action-button"
                  type="button"
                  :disabled="assigningUserId === user.user_id"
                  @click="handleAssignRole(user)"
                >
                  {{
                    assigningUserId === user.user_id ? "Assigning..." : "Assign"
                  }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- User Pagination -->
      <div v-if="users.length > 0" class="assignment-pagination">
        <div class="pagination-size">
          <label for="assignment-page-size">Rows per page:</label>

          <select
            id="assignment-page-size"
            :value="pageSize"
            class="page-size-select"
            @change="handleUserPageSizeChange"
          >
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>
        <span>
          Showing
          {{ totalUsers === 0 ? 0 : (currentPage - 1) * pageSize + 1 }}–{{
            Math.min(currentPage * pageSize, totalUsers)
          }}
          of {{ totalUsers }} users
        </span>

        <div class="pagination-actions">
          <button
            type="button"
            class="pagination-button"
            :disabled="!hasPrevious || loading"
            @click="loadUsers(currentPage - 1)"
          >
            Previous
          </button>

          <span> Page {{ currentPage }} of {{ totalPages }} </span>

          <button
            type="button"
            class="pagination-button"
            :disabled="!hasNext || loading"
            @click="loadUsers(currentPage + 1)"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Role Details Modal -->
    <div
      v-if="showRoleDetails"
      class="modal-overlay"
      @click.self="closeRoleDetails"
    >
      <div class="role-details-modal">
        <div class="modal-header">
          <div>
            <h2>Role Details</h2>
            <p>View role information and assigned users.</p>
          </div>

          <button type="button" class="modal-close" @click="closeRoleDetails">
            &times;
          </button>
        </div>

        <div v-if="loadingRoleDetails" class="state-message">
          Loading role details...
        </div>

        <div v-else-if="roleDetailsError" class="error-message">
          {{ roleDetailsError }}
        </div>

        <div v-else-if="selectedRoleDetails" class="role-details-content">
          <div class="detail-item">
            <span>Role Name</span>
            <strong>{{ selectedRoleDetails.role_name }}</strong>
          </div>

          <div class="detail-item">
            <span>Description</span>
            <strong>
              {{ selectedRoleDetails.description || "No description" }}
            </strong>
          </div>

          <div class="detail-item">
            <span>Total Assigned Users</span>
            <strong>
              {{ selectedRoleDetails.total_users ?? 0 }}
            </strong>
          </div>

          <!-- Permissions -->
          <div class="details-section">
            <h3>Permissions</h3>

            <div
              v-if="selectedRoleDetails.permissions?.length"
              class="permission-list"
            >
              <span
                v-for="permission in selectedRoleDetails.permissions"
                :key="permission"
                class="permission-tag"
              >
                {{ permission }}
              </span>
            </div>

            <p v-else class="empty-details">No permissions assigned.</p>
          </div>

          <!-- Assigned Users -->
          <div class="details-section">
            <h3>Assigned Users</h3>

            <div
              v-if="selectedRoleDetails.assigned_users?.length"
              class="assigned-users-list"
            >
              <div
                v-for="user in selectedRoleDetails.assigned_users"
                :key="user.user_id"
                class="assigned-user"
              >
                <div>
                  <strong> {{ user.first_name }} {{ user.last_name }} </strong>

                  <span>{{ user.email }}</span>
                </div>
              </div>
            </div>

            <p v-else class="empty-details">No users assigned to this role.</p>
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="primary-button"
            @click="closeRoleDetails"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Create / Edit Role Modal -->
    <RoleFormModal
      v-model="showRoleFormModal"
      :mode="roleFormMode"
      :role="selectedRoleForEdit"
      :permissions="normalizedPermissions"
      :saving="savingRole"
      :error="roleFormError"
      @submit="handleRoleSubmit"
    />

    <!-- Delete Role Confirmation -->
    <ConfirmationModal
      v-model="showDeleteConfirmation"
      title="Delete Role?"
      :message="`Are you sure you want to delete the '${roleToDelete?.role_name || ''}' role? This action cannot be undone.`"
      confirm-text="Delete Role"
      cancel-text="Cancel"
      variant="danger"
      :loading="deletingRole"
      @confirm="confirmDeleteRole"
      @cancel="cancelDeleteRole"
    />
  </section>
</template>

<style scoped>
/* ========================================
   Main layout
======================================== */

.roles-panel {
  width: 100%;
}

/* ========================================
   Statistics Cards - Shared Design
======================================== */

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
  background: #ffffff;
  border: 1px solid #e1e5eb;
  border-radius: 13px;
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
  color: #111827;
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  color: #667085;
  font-size: 12px;
}

/* Responsive */

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-card {
    min-height: 82px;
    padding: 16px;
  }
}

/* ========================================
   Cards and section headers
======================================== */

.role-list-card {
  padding: 22px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
}

.assignment-card {
  margin-top: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.section-header h2 {
  margin: 0 0 6px;
  color: #111827;
  font-size: 19px;
}

.section-header p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

/* ========================================
   Buttons
======================================== */

.primary-button {
  padding: 10px 15px;
  color: #ffffff;
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s;
}

.primary-button:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

.primary-button:disabled,
.action-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* ========================================
   Tables
======================================== */

.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.roles-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  white-space: nowrap;
}

.roles-table th {
  padding: 13px 14px;
  color: #6b7280;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-size: 12px;
  font-weight: 600;
}

.roles-table td {
  padding: 15px 14px;
  color: #4b5563;
  border-bottom: 1px solid #f1f2f4;
  font-size: 13px;
  vertical-align: middle;
}

.roles-table tbody tr:hover {
  background: #f9fafb;
}

.role-name,
.assignment-user-name {
  color: #111827;
  font-weight: 600;
}

.description-cell {
  min-width: 220px;
  max-width: 350px;
  white-space: normal;
  line-height: 1.5;
}

.user-count {
  display: inline-block;
  min-width: 28px;
  padding: 5px 9px;
  color: #2563eb;
  background: #eff6ff;
  border-radius: 6px;
  text-align: center;
  font-weight: 600;
}

/* ========================================
   Role action buttons
======================================== */

.role-actions {
  display: flex;
  align-items: center;
  gap: 7px;
}

.role-action-btn {
  padding: 7px 11px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s,
    color 0.2s;
}

.details-btn {
  color: #2563eb;
  background: #eff6ff;
  border-color: #bfdbfe;
}

.details-btn:hover {
  background: #dbeafe;
  border-color: #93c5fd;
}

.edit-btn {
  color: #b45309;
  background: #fffbeb;
  border-color: #fde68a;
}

.edit-btn:hover {
  background: #fef3c7;
  border-color: #fcd34d;
}

.delete-btn {
  color: #dc2626;
  background: #fef2f2;
  border-color: #fecaca;
}

.delete-btn:hover {
  color: #b91c1c;
  background: #fee2e2;
  border-color: #fca5a5;
}

/* ========================================
   User search and filters
======================================== */

.assignment-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.search-input,
.filter-select,
.role-select {
  width: 100%;
  max-width: 320px;
  padding: 10px 12px;
  color: #374151;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 7px;
  outline: none;
  font-size: 13px;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.search-input:focus,
.filter-select:focus,
.role-select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.filter-select {
  width: auto;
  min-width: 140px;
  cursor: pointer;
}

.clear-search-button {
  padding: 9px 13px;
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 7px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s;
}

.clear-search-button:hover {
  background: #fee2e2;
  border-color: #fca5a5;
}

/* Sortable table heading */

.sortable-header {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 0;
  color: inherit;
  background: transparent;
  border: none;
  font: inherit;
  cursor: pointer;
}

.sortable-header:hover {
  color: #2563eb;
}

/* Role assignment action */

.action-button {
  padding: 7px 12px;
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.action-button:hover {
  background: #dbeafe;
}

/* ========================================
   Pagination
======================================== */

.role-list-footer,
.assignment-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 15px;
  padding-top: 16px;
  color: #6b7280;
  font-size: 12px;
}

.pagination-controls,
.pagination-size,
.pagination-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.pagination-info {
  color: #6b7280;
}

.page-size-select {
  min-width: 60px;
  padding: 7px 10px;
  color: #111827;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.page-indicator {
  color: #111827;
  font-weight: 600;
  white-space: nowrap;
}

.pagination-button {
  padding: 7px 12px;
  color: #374151;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.pagination-button.active {
  color: #ffffff;
  background: #2563eb;
  border-color: #2563eb;
}

.pagination-button.active:hover {
  background: #1d4ed8;
}

.pagination-button:disabled {
  color: #9ca3af;
  background: #ffffff;
  opacity: 0.65;
  cursor: not-allowed;
}

/* ========================================
   General states and messages
======================================== */

.state-message {
  padding: 35px 15px;
  color: #6b7280;
  text-align: center;
  font-size: 14px;
}

.error-message {
  padding: 12px 15px;
  margin-bottom: 15px;
  color: #dc2626;
  background: #fef2f2;
  border-radius: 8px;
  font-size: 13px;
}

.error-message button {
  padding: 6px 10px;
  margin-left: 10px;
  color: #2563eb;
  background: transparent;
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.success-message {
  padding: 12px;
  margin-bottom: 15px;
  color: #16a34a;
  background: #f0fdf4;
  border-radius: 7px;
  font-size: 13px;
}

/* ========================================
   Role details modal
======================================== */

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(17, 24, 39, 0.55);
}

.role-details-modal {
  width: 100%;
  max-width: 650px;
  max-height: 85vh;
  overflow-y: auto;
  padding: 24px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 15px;
  padding-bottom: 18px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0 0 6px;
  color: #111827;
  font-size: 20px;
}

.modal-header p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.modal-close {
  color: #6b7280;
  background: none;
  border: none;
  font-size: 26px;
  cursor: pointer;
}

.role-details-content {
  padding-top: 20px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f2f4;
  font-size: 13px;
}

.detail-item span {
  color: #6b7280;
}

.detail-item strong {
  color: #111827;
  text-align: right;
}

.details-section {
  margin-top: 22px;
}

.details-section h3 {
  margin: 0 0 12px;
  color: #111827;
  font-size: 15px;
}

.permission-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.permission-tag {
  padding: 6px 10px;
  color: #2563eb;
  background: #eff6ff;
  border-radius: 6px;
  font-size: 12px;
}

.assigned-users-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.assigned-user {
  padding: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 7px;
}

.assigned-user strong,
.assigned-user span {
  display: block;
  font-size: 13px;
}

.assigned-user strong {
  margin-bottom: 5px;
  color: #111827;
}

.assigned-user span,
.empty-details {
  color: #6b7280;
  font-size: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

/* ========================================
   Responsive layout
======================================== */

@media (max-width: 700px) {
  .role-list-footer,
  .assignment-pagination {
    align-items: flex-start;
    flex-direction: column;
  }

  .pagination-controls,
  .pagination-actions {
    flex-wrap: wrap;
  }
}

@media (max-width: 600px) {
  .role-list-card {
    padding: 15px;
  }

  .section-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .assignment-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .assignment-toolbar .search-input,
  .assignment-toolbar .filter-select {
    max-width: 100%;
  }

  .role-actions {
    flex-wrap: wrap;
  }

  .role-details-modal {
    padding: 16px;
  }

  .detail-item {
    flex-direction: column;
    gap: 5px;
  }

  .detail-item strong {
    text-align: left;
  }
}
</style>
