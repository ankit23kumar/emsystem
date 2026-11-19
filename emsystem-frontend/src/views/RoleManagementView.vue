<script setup>
import { ref, computed, onMounted } from "vue";
import {
  getRoles,
  getPermissions,
  createRole,
  getRoleDetails,
  updateRole,
  deleteRole,
} from "../services/roleService";
import { useAuthStore } from "../stores/authStore";

const authStore = useAuthStore();

// Role list state
const roles = ref([]);
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

// Create role state
const showCreateForm = ref(false);
const creatingRole = ref(false);
const permissions = ref([]);
const permissionLoading = ref(false);
const permissionError = ref("");

const roleForm = ref({
  role_name: "",
  description: "",
  permissions: [],
});

const canCreateRoles = computed(() => authStore.hasPermission("roles.create"));

// Only show permissions the logged-in user personally possesses.
const availablePermissions = computed(() => {
  return permissions.value.filter((permission) =>
    authStore.permissions.value.includes(permission.codename),
  );
});

async function loadRoles() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await getRoles();
    roles.value = response.data.roles || [];
  } catch (error) {
    const status = error.response?.status;

    if (status === 403) {
      errorMessage.value =
        error.response.data?.error ||
        "You do not have permission to view roles.";
    } else if (!error.response) {
      errorMessage.value = "Unable to connect to the server. Please try again.";
    } else {
      errorMessage.value =
        error.response.data?.error ||
        error.response.data?.message ||
        "Failed to load roles.";
    }
  } finally {
    loading.value = false;
  }
}

async function loadPermissions() {
  permissionLoading.value = true;
  permissionError.value = "";

  try {
    const response = await getPermissions();
    permissions.value = response.data.permissions || [];
  } catch (error) {
    permissionError.value =
      error.response?.data?.error ||
      error.response?.data?.message ||
      "Failed to load permissions.";
  } finally {
    permissionLoading.value = false;
  }
}

function resetRoleForm() {
  roleForm.value = {
    role_name: "",
    description: "",
    permissions: [],
  };
}

async function openCreateForm() {
  successMessage.value = "";
  permissionError.value = "";
  showCreateForm.value = true;

  if (permissions.value.length === 0) {
    await loadPermissions();
  }
}

function closeCreateForm() {
  if (creatingRole.value) return;

  showCreateForm.value = false;
  resetRoleForm();
}

async function submitCreateRole() {
  if (!roleForm.value.role_name.trim()) {
    return;
  }

  creatingRole.value = true;
  successMessage.value = "";
  errorMessage.value = "";

  try {
    const payload = {
      role_name: roleForm.value.role_name.trim(),
      description: roleForm.value.description.trim(),
      permissions: [...roleForm.value.permissions],
    };

    const response = await createRole(payload);

    successMessage.value =
      response.data.message || "Role created successfully.";

    closeCreateForm();
    await loadRoles();
  } catch (error) {
    errorMessage.value =
      error.response?.data?.error ||
      error.response?.data?.message ||
      "Failed to create role.";
  } finally {
    creatingRole.value = false;
  }
}

// Role details
const selectedRole = ref(null);
const showDetails = ref(false);
const detailsLoading = ref(false);
const detailsError = ref("");

// Edit role
const showEditForm = ref(false);
const savingRole = ref(false);

const editForm = ref({
  role_name: "",
  description: "",
  permissions: [],
});

const canUpdateRoles = computed(() => authStore.hasPermission("roles.update"));

// Prevent editing permissions that the current user cannot manage.
const canEditSelectedPermissions = computed(() => {
  if (!selectedRole.value) return false;

  return (selectedRole.value.permissions || []).every((codename) =>
    availablePermissions.value.some(
      (permission) => permission.codename === codename,
    ),
  );
});

async function openRoleDetails(roleId) {
  showDetails.value = true;
  showEditForm.value = false;
  selectedRole.value = null;
  detailsError.value = "";
  detailsLoading.value = true;

  try {
    const response = await getRoleDetails(roleId);
    selectedRole.value = response.data.role;
  } catch (error) {
    detailsError.value =
      error.response?.data?.error ||
      error.response?.data?.message ||
      "Unable to load role details.";
  } finally {
    detailsLoading.value = false;
  }
}

async function openEditForm() {
  if (!selectedRole.value || !canUpdateRoles.value) return;

  if (permissions.value.length === 0) {
    await loadPermissions();
  }

  if (permissionError.value) return;

  editForm.value = {
    role_name: selectedRole.value.role_name,
    description: selectedRole.value.description || "",
    permissions: [...(selectedRole.value.permissions || [])],
  };

  showEditForm.value = true;
}

async function submitUpdateRole() {
  if (!selectedRole.value || savingRole.value) return;

  const payload = {
    role_name: editForm.value.role_name.trim(),
    description: editForm.value.description.trim(),
  };

  // Only send permissions if the user can safely manage
  // every permission currently assigned to this role.
  if (canEditSelectedPermissions.value) {
    payload.permissions = [...editForm.value.permissions];
  }

  if (!payload.role_name) return;

  savingRole.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const roleId = selectedRole.value.role_id;

    const response = await updateRole(roleId, payload);

    successMessage.value =
      response.data.message || "Role updated successfully.";

    showEditForm.value = false;

    await loadRoles();
    await openRoleDetails(roleId);
  } catch (error) {
    errorMessage.value =
      error.response?.data?.error ||
      error.response?.data?.message ||
      "Failed to update role.";
  } finally {
    savingRole.value = false;
  }
}

const deletingRole = ref(false);

const canDeleteRoles = computed(() => authStore.hasPermission("roles.delete"));

async function handleDeleteRole() {
  if (!selectedRole.value || deletingRole.value) return;

  const roleId = selectedRole.value.role_id;
  const roleName = selectedRole.value.role_name;

  const confirmed = window.confirm(
    `Are you sure you want to delete the "${roleName}" role?`,
  );

  if (!confirmed) return;

  deletingRole.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const response = await deleteRole(roleId);

    successMessage.value =
      response.data.message || "Role deleted successfully.";

    showDetails.value = false;
    selectedRole.value = null;

    await loadRoles();
  } catch (error) {
    errorMessage.value =
      error.response?.data?.error ||
      error.response?.data?.message ||
      "Unable to delete this role.";
  } finally {
    deletingRole.value = false;
  }
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "—";

  return date.toLocaleDateString();
}

onMounted(async () => {
  await loadRoles();
});
</script>

<template>
  <main class="roles-page">
    <header class="page-header">
      <div>
        <h1>Role Management</h1>
        <p>Manage roles and their permissions in EMSystem.</p>
      </div>

      <div class="header-actions">
        <span class="role-count"> Total Roles: {{ roles.length }} </span>

        <button
          v-if="canCreateRoles"
          type="button"
          class="create-button"
          @click="openCreateForm"
        >
          + Create Role
        </button>
      </div>
    </header>

    <section class="roles-container">
      <!-- Create Role Form -->
      <div v-if="showCreateForm" class="create-role-form">
        <h2>Create New Role</h2>

        <form @submit.prevent="submitCreateRole">
          <div class="form-field">
            <label for="role-name">Role Name</label>

            <input
              id="role-name"
              v-model="roleForm.role_name"
              type="text"
              maxlength="100"
              placeholder="e.g. HR Manager"
              required
            />
          </div>

          <div class="form-field">
            <label for="role-description">Description</label>

            <textarea
              id="role-description"
              v-model="roleForm.description"
              rows="3"
              placeholder="Describe the responsibilities of this role..."
            ></textarea>
          </div>

          <div class="permissions-section">
            <h3>Select Permissions</h3>

            <p class="permission-note">
              You can assign only permissions that you currently possess.
            </p>

            <div v-if="permissionLoading">Loading permissions...</div>

            <div v-else-if="permissionError" class="error-message">
              {{ permissionError }}
              <button type="button" @click="loadPermissions">Retry</button>
            </div>

            <div
              v-else-if="availablePermissions.length === 0"
              class="state-message"
            >
              No assignable permissions are available.
            </div>

            <div v-else class="permissions-grid">
              <label
                v-for="permission in availablePermissions"
                :key="permission.permission_id"
                class="permission-item"
              >
                <input
                  v-model="roleForm.permissions"
                  type="checkbox"
                  :value="permission.codename"
                />

                <span>
                  <strong>{{ permission.permission_name }}</strong>
                  <small>{{ permission.description }}</small>
                  <small class="permission-code">
                    {{ permission.codename }}
                  </small>
                </span>
              </label>
            </div>
          </div>

          <div class="form-actions">
            <button
              type="button"
              class="cancel-button"
              :disabled="creatingRole"
              @click="closeCreateForm"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="create-button"
              :disabled="creatingRole || permissionLoading || !!permissionError"
            >
              {{ creatingRole ? "Creating..." : "Create Role" }}
            </button>
          </div>
        </form>
      </div>

      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div class="section-heading">
        <h2>Available Roles</h2>

        <button
          type="button"
          class="refresh-button"
          :disabled="loading"
          @click="loadRoles"
        >
          {{ loading ? "Loading..." : "Refresh" }}
        </button>
      </div>

      <div v-if="loading" class="state-message">Loading roles...</div>

      <div v-else-if="errorMessage" class="error-message">
        <p>{{ errorMessage }}</p>
        <button type="button" @click="loadRoles">Try Again</button>
      </div>

      <div v-else-if="roles.length === 0" class="state-message">
        No roles found. Create your first role to get started.
      </div>

      <div v-else class="roles-grid">
        <article v-for="role in roles" :key="role.role_id" class="role-card">
          <div class="role-card-header">
            <h3>{{ role.role_name }}</h3>
            <span class="role-id">#{{ role.role_id }}</span>
          </div>

          <p class="role-description">
            {{ role.description || "No description available." }}
          </p>

          <div class="role-meta">
            <span> Created: {{ formatDate(role.created_at) }} </span>
            <span> Updated: {{ formatDate(role.updated_at) }} </span>
          </div>
          <div class="role-card-actions">
            <button
              type="button"
              ,
              class="details-button"
              @click="openRoleDetails(role.role_id)"
            >
              View Details
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- Role Details Modal -->
    <div
      v-if="showDetails"
      class="modal-backdrop"
      @click.self="showDetails = false"
    >
      <section class="role-modal" role="dialog" aria-modal="true">
        <div class="modal-heading">
          <div>
            <h2>Role Details</h2>
            <p>View and manage role information.</p>
          </div>

          <button
            type="button"
            class="close-button"
            @click="showDetails = false"
          >
            ×
          </button>
        </div>

        <div v-if="detailsLoading" class="state-message">
          Loading role details...
        </div>

        <div v-else-if="detailsError" class="error-message">
          {{ detailsError }}
        </div>

        <template v-else-if="selectedRole">
          <div v-if="!showEditForm" class="role-detail-content">
            <h3>{{ selectedRole.role_name }}</h3>

            <p>
              {{ selectedRole.description || "No description available." }}
            </p>

            <h4>Assigned Permissions</h4>

            <div class="permission-tags">
              <span
                v-for="permission in selectedRole.permissions"
                :key="permission"
                class="permission-tag"
              >
                {{ permission }}
              </span>

              <span
                v-if="!selectedRole.permissions?.length"
                class="state-message"
              >
                No permissions assigned.
              </span>
            </div>

            <h4>Assigned Users ({{ selectedRole.total_users || 0 }})</h4>

            <div
              v-if="selectedRole.assigned_users?.length"
              class="assigned-users"
            >
              <div
                v-for="assignedUser in selectedRole.assigned_users"
                :key="assignedUser.user_id"
                class="assigned-user"
              >
                <strong>
                  {{ assignedUser.first_name }}
                  {{ assignedUser.last_name }}
                </strong>
                <span>{{ assignedUser.email }}</span>
              </div>
            </div>

            <p v-else class="state-message">No users assigned to this role.</p>

            <div class="form-actions">
              <button
                v-if="canUpdateRoles"
                type="button"
                class="create-button"
                @click="openEditForm"
              >
                Edit Role
              </button>

              <button
                v-if="canDeleteRoles"
                type="button"
                class="delete-button"
                :disabled="deletingRole"
                @click="handleDeleteRole"
              >
                {{ deletingRole ? "Deleting..." : "Delete Role" }}
              </button>

              <button
                type="button"
                class="cancel-button"
                @click="showDetails = false"
              >
                Close
              </button>
            </div>
          </div>

          <!-- Edit Role Form -->
          <form
            v-else
            class="edit-role-form"
            @submit.prevent="submitUpdateRole"
          >
            <h3>Edit Role</h3>

            <div class="form-field">
              <label for="edit-role-name">Role Name</label>
              <input
                id="edit-role-name"
                v-model="editForm.role_name"
                maxlength="100"
                required
              />
            </div>

            <div class="form-field">
              <label for="edit-role-description">Description</label>
              <textarea
                id="edit-role-description"
                v-model="editForm.description"
                rows="3"
              ></textarea>
            </div>

            <div class="permissions-section">
              <h4>Permissions</h4>

              <p v-if="!canEditSelectedPermissions" class="permission-warning">
                You cannot manage all existing permissions assigned to this
                role. You can still update its name and description.
              </p>

              <template v-else>
                <p class="permission-note">
                  Select the permissions for this role.
                </p>

                <div class="permissions-grid">
                  <label
                    v-for="permission in availablePermissions"
                    :key="permission.permission_id"
                    class="permission-item"
                  >
                    <input
                      v-model="editForm.permissions"
                      type="checkbox"
                      :value="permission.codename"
                    />

                    <span>
                      <strong>{{ permission.permission_name }}</strong>
                      <small>{{ permission.description }}</small>
                    </span>
                  </label>
                </div>
              </template>
            </div>

            <div class="form-actions">
              <button
                type="button"
                class="cancel-button"
                :disabled="savingRole"
                @click="showEditForm = false"
              >
                Cancel
              </button>

              <button
                type="submit"
                class="create-button"
                :disabled="savingRole"
              >
                {{ savingRole ? "Updating..." : "Save Changes" }}
              </button>
            </div>
          </form>
        </template>
      </section>
    </div>
  </main>
</template>

<style scoped>
.roles-page {
  padding: 30px;
  min-height: 100vh;
  background: #f5f7fb;
}

.page-header,
.section-heading,
.role-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.page-header {
  margin-bottom: 28px;
}

.page-header h1 {
  margin: 0 0 8px;
  color: #1e293b;
}

.page-header p,
.role-description {
  color: #64748b;
}

.role-count {
  font-weight: 600;
  color: #334155;
}

.roles-container {
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgb(0 0 0 / 5%);
}

.section-heading {
  margin-bottom: 22px;
}

.section-heading h2 {
  margin: 0;
  color: #1e293b;
}

.refresh-button,
.error-message button {
  padding: 9px 16px;
  border: 0;
  border-radius: 6px;
  background: #2563eb;
  color: white;
  cursor: pointer;
}

.refresh-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}

.role-card {
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.role-card h3 {
  margin: 0;
  color: #1e293b;
}

.role-id {
  color: #64748b;
  font-size: 13px;
}

.role-description {
  min-height: 45px;
  line-height: 1.5;
}

.role-meta {
  display: grid;
  gap: 7px;
  padding-top: 14px;
  border-top: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 12px;
}

.state-message {
  padding: 35px 15px;
  text-align: center;
  color: #64748b;
}

.error-message {
  padding: 20px;
  text-align: center;
  color: #dc2626;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.create-role-form {
  margin-bottom: 25px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
}

.create-role-form h2 {
  margin-top: 0;
  color: #1e293b;
}

.form-field {
  display: grid;
  gap: 8px;
  margin-bottom: 18px;
}

.form-field label {
  font-weight: 600;
  color: #334155;
}

.form-field input,
.form-field textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 11px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font: inherit;
}

.form-field textarea {
  resize: vertical;
}

.permissions-section {
  margin-top: 25px;
}

.permission-note {
  color: #64748b;
  font-size: 13px;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  margin-top: 15px;
}

.permission-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.permission-item input {
  margin-top: 4px;
}

.permission-item span {
  display: grid;
  gap: 5px;
}

.permission-item small {
  color: #64748b;
  line-height: 1.4;
}

.permission-code {
  font-family: monospace;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 25px;
}

.create-button,
.cancel-button {
  padding: 10px 18px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.create-button {
  background: #2563eb;
  color: white;
}

.cancel-button {
  background: #e2e8f0;
  color: #334155;
}

.create-button:disabled,
.cancel-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-message {
  margin-bottom: 15px;
  padding: 12px;
  border-radius: 6px;
  background: #dcfce7;
  color: #166534;
}

.error-message {
  margin-bottom: 15px;
}

.role-card-actions {
  margin-top: 16px;
}

.details-button {
  padding: 9px 15px;
  border: 1px solid #2563eb;
  border-radius: 6px;
  background: white;
  color: #2563eb;
  cursor: pointer;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgb(15 23 42 / 55%);
}

.role-modal {
  width: 100%;
  max-width: 650px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 25px;
  border-radius: 12px;
  background: white;
}

.modal-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.modal-heading h2 {
  margin: 0 0 6px;
}

.modal-heading p {
  color: #64748b;
}

.close-button {
  border: 0;
  background: transparent;
  font-size: 25px;
  cursor: pointer;
}

.role-detail-content h3 {
  color: #1e293b;
}

.role-detail-content h4 {
  margin-top: 24px;
  color: #334155;
}

.permission-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}

.permission-tag {
  padding: 7px 11px;
  border-radius: 6px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 13px;
}

.assigned-users {
  display: grid;
  gap: 10px;
}

.assigned-user {
  display: grid;
  gap: 5px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
}

.assigned-user span {
  color: #64748b;
  font-size: 13px;
}

.permission-warning {
  padding: 12px;
  border-radius: 6px;
  background: #fef3c7;
  color: #92400e;
  font-size: 13px;
}

.delete-button {
  background: #dc2626;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.delete-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
