```vue
<script setup>
import { computed, reactive, ref, watch } from 'vue'
import api from '../services/api'
import PasswordInput from './PasswordInput.vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'create',
    validator: value => ['create', 'edit'].includes(value),
  },
  selectedUser: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close', 'saved'])

const isEditMode = computed(() => props.mode === 'edit')
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const errors = reactive({})

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
})

function clearErrors() {
  Object.keys(errors).forEach(key => delete errors[key])
}

function resetForm() {
  form.first_name = props.selectedUser?.first_name || ''
  form.last_name = props.selectedUser?.last_name || ''
  form.email = props.selectedUser?.email || ''
  form.password = ''
  errorMessage.value = ''
  successMessage.value = ''
  clearErrors()
}

watch(
  () => [props.mode, props.selectedUser],
  resetForm,
  { immediate: true }
)

function validate() {
  clearErrors()

  const first = form.first_name.trim()
  const last = form.last_name.trim()
  const email = form.email.trim()

  if (!first) {
    errors.first_name = 'First name is required.'
  } else if (first.length > 40) {
    errors.first_name = 'Maximum 40 characters allowed.'
  }

  if (!last) {
    errors.last_name = 'Last name is required.'
  } else if (last.length > 40) {
    errors.last_name = 'Maximum 40 characters allowed.'
  }

  if (!email) {
    errors.email = 'Email address is required.'
  } else if (
    email.length > 254 ||
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  ) {
    errors.email = 'Enter a valid email address.'
  }

  if (!isEditMode.value) {
    if (!form.password) {
      errors.password = 'Password is required.'
    } else if (
      form.password.length < 8 ||
      form.password.length > 128
    ) {
      errors.password = 'Password must be between 8 and 128 characters.'
    }
  }

  return Object.keys(errors).length === 0
}

async function submitForm() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!validate()) return

  saving.value = true

  const payload = {
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
    email: form.email.trim().toLowerCase(),
  }

  if (!isEditMode.value) {
    payload.password = form.password
  }

  try {
    if (isEditMode.value) {
      const userId = props.selectedUser?.user_id

      if (!userId) {
        errorMessage.value =
          'Could not identify the selected user. Close this window and try again.'
        return
      }

      await api.put(`/update/${userId}`, payload)
      successMessage.value = 'User updated successfully.'
    } else {
      await api.post('/user-create', payload)
      successMessage.value = 'User created successfully.'
    }

    // Keep the modal open briefly so the user can see the success message.
    await new Promise(resolve => setTimeout(resolve, 600))
    emit('saved')
  } catch (error) {
    const status = error.response?.status
    const data = error.response?.data
    const message =
      data?.error || data?.message || 'Unable to save this user.'

    if (status === 409) {
      errors.email = message
    } else if (status === 400) {
      errorMessage.value = message
    } else if (status === 401) {
      errorMessage.value =
        'Your session has expired. Please log in again.'
    } else if (status === 403) {
      errorMessage.value = message
    } else if (!error.response) {
      errorMessage.value =
        'Cannot connect to the server. Please try again.'
    } else {
      errorMessage.value = message
    }
  } finally {
    saving.value = false
  }
}

function closeModal() {
  if (!saving.value) emit('close')
}

function clearFieldError(field) {
  delete errors[field]
  errorMessage.value = ''
}
</script>

<template>
  <div class="modal-backdrop" @click.self="closeModal">
    <section
      class="user-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <header class="modal-header">
        <div>
          <h2 id="modal-title">
            {{ isEditMode ? 'Edit User' : 'Create User' }}
          </h2>

          <p>
            {{
              isEditMode
                ? 'Update this user’s information.'
                : 'Enter the details for the new user.'
            }}
          </p>
        </div>

        <button
          class="close-button"
          type="button"
          aria-label="Close dialog"
          :disabled="saving"
          @click="closeModal"
        >
          ×
        </button>
      </header>

      <p v-if="errorMessage" class="message error" role="alert">
        {{ errorMessage }}
      </p>

      <p v-if="successMessage" class="message success" role="status">
        {{ successMessage }}
      </p>

      <form @submit.prevent="submitForm" novalidate>
        <div class="form-group">
          <label for="modal-first-name">First name</label>

          <input
            id="modal-first-name"
            v-model="form.first_name"
            :class="{ 'input-error': errors.first_name }"
            type="text"
            maxlength="40"
            autocomplete="given-name"
            placeholder="Enter first name"
            :disabled="saving"
            :aria-invalid="Boolean(errors.first_name)"
            @input="clearFieldError('first_name')"
          />

          <small v-if="errors.first_name" class="field-error">
            {{ errors.first_name }}
          </small>
        </div>

        <div class="form-group">
          <label for="modal-last-name">Last name</label>

          <input
            id="modal-last-name"
            v-model="form.last_name"
            :class="{ 'input-error': errors.last_name }"
            type="text"
            maxlength="40"
            autocomplete="family-name"
            placeholder="Enter last name"
            :disabled="saving"
            :aria-invalid="Boolean(errors.last_name)"
            @input="clearFieldError('last_name')"
          />

          <small v-if="errors.last_name" class="field-error">
            {{ errors.last_name }}
          </small>
        </div>

        <div class="form-group">
          <label for="modal-email">Email address</label>

          <input
            id="modal-email"
            v-model="form.email"
            :class="{ 'input-error': errors.email }"
            type="email"
            maxlength="254"
            autocomplete="email"
            placeholder="name@example.com"
            :disabled="saving"
            :aria-invalid="Boolean(errors.email)"
            @input="clearFieldError('email')"
          />

          <small v-if="errors.email" class="field-error">
            {{ errors.email }}
          </small>
        </div>

        <!-- Password is required only when creating a user. -->
        <div v-if="!isEditMode" class="form-group">
          <label for="modal-password">Password</label>

          <PasswordInput
            id="modal-password"
            v-model="form.password"
            name="password"
            placeholder="Enter 8–128 characters"
            autocomplete="new-password"
            :required="true"
            :disabled="saving"
          />

          <small class="helper-text">
            Password must be 8–128 characters.
          </small>

          <small v-if="errors.password" class="field-error">
            {{ errors.password }}
          </small>
        </div>

        <p v-else class="edit-password-note">
          Passwords are securely hashed and cannot be viewed or retrieved.
        </p>

        <footer class="modal-actions">
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
            class="save-button"
            :disabled="saving"
          >
            {{
              saving
                ? 'Saving...'
                : isEditMode
                  ? 'Save Changes'
                  : 'Create User'
            }}
          </button>
        </footer>
      </form>
    </section>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.modal-backdrop {
  position: fixed;
  z-index: 1000;
  inset: 0;
  display: grid;
  place-items: center;
  overflow-y: auto;
  padding: 20px;
  background: rgba(16, 24, 40, 0.55);
}

.user-modal {
  width: min(100%, 500px);
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  padding: 26px;
  border: 1px solid #e4e7ec;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 20px 60px rgba(16, 24, 40, 0.2);
  color: #172b4d;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.modal-header h2 {
  margin: 0;
  font-size: 22px;
}

.modal-header p {
  margin: 7px 0 0;
  color: #667085;
  font-size: 13px;
  line-height: 1.5;
}

.close-button {
  flex-shrink: 0;
  align-self: flex-start;
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 7px;
  background: #f2f4f7;
  color: #344054;
  font-size: 25px;
  cursor: pointer;
}

.form-group {
  margin-bottom: 17px;
}

.form-group label {
  display: block;
  margin-bottom: 7px;
  color: #344054;
  font-size: 13px;
  font-weight: 650;
}

.form-group > input {
  display: block;
  width: 100%;
  min-width: 0;
  padding: 11px 12px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  outline: none;
  background: #fff;
  color: #172b4d;
  font: inherit;
  font-size: 14px;
}

.form-group > input:focus {
  border-color: #2864ed;
  box-shadow: 0 0 0 3px rgba(40, 100, 237, 0.12);
}

.form-group > input.input-error {
  border-color: #d92d20;
}

.form-group > input:disabled {
  background: #f9fafb;
}

/* PasswordInput.vue manages its own input and eye-button styling. */

.helper-text,
.field-error {
  display: block;
  margin-top: 6px;
  font-size: 12px;
}

.helper-text {
  color: #667085;
}

.field-error {
  color: #b42318;
}

.edit-password-note {
  padding: 11px 12px;
  border-radius: 7px;
  background: #f8fafc;
  color: #667085;
  font-size: 12px;
  line-height: 1.5;
}

.message {
  padding: 11px 12px;
  margin: 0 0 16px;
  border: 1px solid;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
}

.message.error {
  border-color: #fecdca;
  background: #fef3f2;
  color: #b42318;
}

.message.success {
  border-color: #abefc6;
  background: #ecfdf3;
  color: #067647;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 25px;
}

.cancel-button,
.save-button {
  min-height: 40px;
  padding: 10px 15px;
  border: 1px solid;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
}

.cancel-button {
  border-color: #d0d5dd;
  background: #fff;
  color: #344054;
}

.save-button {
  border-color: #2864ed;
  background: #2864ed;
  color: white;
}

.save-button:hover:not(:disabled) {
  background: #1d4ed8;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .user-modal {
    padding: 20px 17px;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}
</style>
```