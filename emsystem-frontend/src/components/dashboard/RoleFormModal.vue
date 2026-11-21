
<script setup>
import { computed, reactive, watch } from "vue";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  mode: {
    type: String,
    default: "create",
  },
  role: {
    type: Object,
    default: null,
  },
  permissions: {
    type: Array,
    default: () => [],
  },
  saving: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: "",
  },
});

const emit = defineEmits([
  "update:modelValue",
  "submit",
]);

// --------------------------------------------------
// Form state
// --------------------------------------------------

const form = reactive({
  role_name: "",
  description: "",
  permissions: [],
});

const isEditMode = computed(() => props.mode === "edit");

const modalTitle = computed(() =>
  isEditMode.value ? "Edit Role" : "Create New Role"
);

const submitButtonText = computed(() => {
  if (props.saving) return "Saving...";

  return isEditMode.value ? "Update Role" : "Create Role";
});

// --------------------------------------------------
// Reset form
// --------------------------------------------------

function resetForm() {
  form.role_name = props.role?.role_name || "";
  form.description = props.role?.description || "";

  form.permissions = Array.isArray(props.role?.permissions)
    ? [...props.role.permissions]
    : [];
}

// Reset the form whenever the modal opens.
watch(
  () => props.modelValue,
  (isVisible) => {
    if (isVisible) {
      resetForm();
    }
  }
);

// --------------------------------------------------
// Modal actions
// --------------------------------------------------

function closeModal() {
  if (props.saving) return;

  emit("update:modelValue", false);
}

// --------------------------------------------------
// Submit form
// --------------------------------------------------

function submitForm() {
  const roleName = form.role_name.trim();

  if (!roleName || form.permissions.length === 0) {
    return;
  }

  emit("submit", {
    role_name: roleName,
    description: form.description.trim(),
    permissions: [...form.permissions],
  });
}
</script>

<template>
  <div
    v-if="modelValue"
    class="modal-overlay"
    @click.self="closeModal"
  >
    <div
      class="role-form-modal"
      role="dialog"
      aria-modal="true"
      :aria-label="modalTitle"
    >

      <!-- Header -->
      <div class="modal-header">
        <div>
          <h2>{{ modalTitle }}</h2>

          <p>
            {{
              isEditMode
                ? "Update role information and permissions."
                : "Create a new role and assign permissions."
            }}
          </p>
        </div>

        <button
          type="button"
          class="modal-close"
          :disabled="saving"
          aria-label="Close modal"
          @click="closeModal"
        >
          &times;
        </button>
      </div>

      <!-- Form -->
      <form
        class="role-form"
        @submit.prevent="submitForm"
      >

        <!-- Role Name -->
        <div class="form-group">
          <label for="role-name">
            Role Name
            <span class="required">*</span>
          </label>

          <input
            id="role-name"
            v-model="form.role_name"
            type="text"
            maxlength="50"
            placeholder="Enter role name"
            autocomplete="off"
            required
          />
        </div>

        <!-- Description -->
        <div class="form-group">
          <label for="role-description">
            Description
          </label>

          <textarea
            id="role-description"
            v-model="form.description"
            rows="3"
            placeholder="Enter role description"
          ></textarea>
        </div>

        <!-- Permissions -->
        <div class="form-group">
          <div class="permission-heading">
            <label>Permissions <span class="required">*</span></label>

            <span class="selected-count">
              {{ form.permissions.length }} selected
            </span>
          </div>

          <div
            v-if="permissions.length > 0"
            class="permissions-grid"
          >
            <label
              v-for="permission in permissions"
              :key="permission.id"
              class="permission-checkbox"
              :title="permission.description"
            >
              <input
                v-model="form.permissions"
                type="checkbox"
                :value="permission.value"
              />

              <span class="permission-label">
                {{ permission.label }}

                <small>
                  {{ permission.value }}
                </small>
              </span>
            </label>
          </div>

          <p v-else class="form-hint">
            No permissions are available.
          </p>

          <p
            v-if="form.permissions.length === 0"
            class="form-hint"
          >
            Select at least one permission.
          </p>
        </div>

        <!-- API Error -->
        <div
          v-if="error"
          class="form-error"
          role="alert"
        >
          {{ error }}
        </div>

        <!-- Footer -->
        <div class="modal-actions">
          <button
            type="button"
            class="cancel-button"
            :disabled="saving"
            @click="closeModal"
          >
            Cancel
          </button>

          <button
            type="submit"
            class="submit-button"
            :disabled="
              saving ||
              !form.role_name.trim() ||
              form.permissions.length === 0
            "
          >
            {{ submitButtonText }}
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<style scoped>
/* Modal */

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(17, 24, 39, 0.55);
}

.role-form-modal {
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 24px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

/* Header */

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
  line-height: 1.5;
}

.modal-close {
  padding: 0;
  color: #6b7280;
  background: none;
  border: none;
  font-size: 27px;
  line-height: 1;
  cursor: pointer;
}

.modal-close:hover {
  color: #111827;
}

.modal-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Form */

.role-form {
  padding-top: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin-bottom: 20px;
}

.form-group > label,
.permission-heading > label {
  color: #374151;
  font-size: 13px;
  font-weight: 600;
}

.required {
  color: #dc2626;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 11px 12px;
  color: #374151;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 7px;
  outline: none;
  font-family: inherit;
  font-size: 13px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #2563eb;
}

.form-group textarea {
  resize: vertical;
}

/* Permission selection */

.permission-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.selected-count {
  color: #2563eb;
  font-size: 12px;
  font-weight: 600;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  padding: 14px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.permission-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  min-width: 0;
  padding: 9px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 7px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.permission-checkbox:hover {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.permission-checkbox input {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  margin-top: 2px;
  accent-color: #2563eb;
  cursor: pointer;
}

.permission-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #374151;
  font-size: 12px;
  font-weight: 600;
}

.permission-label small {
  color: #9ca3af;
  font-size: 10px;
  font-weight: 400;
  overflow-wrap: anywhere;
}

.form-hint {
  margin: 0;
  color: #9ca3af;
  font-size: 12px;
}

.form-error {
  padding: 11px 13px;
  margin-bottom: 16px;
  color: #dc2626;
  background: #fef2f2;
  border-radius: 7px;
  font-size: 13px;
}

/* Footer buttons */

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 18px;
  border-top: 1px solid #e5e7eb;
}

.cancel-button,
.submit-button {
  padding: 10px 16px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.cancel-button {
  color: #374151;
  background: #ffffff;
  border: 1px solid #d1d5db;
}

.cancel-button:hover {
  background: #f9fafb;
}

.submit-button {
  color: #ffffff;
  background: #2563eb;
  border: 1px solid #2563eb;
}

.submit-button:hover {
  background: #1d4ed8;
}

.cancel-button:disabled,
.submit-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* Responsive */

@media (max-width: 600px) {
  .role-form-modal {
    padding: 17px;
  }

  .permissions-grid {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .cancel-button,
  .submit-button {
    width: 100%;
  }
}
</style>
