
<script setup>
import { ref } from 'vue'

defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  id: {
    type: String,
    default: 'password',
  },
  name: {
    type: String,
    default: 'password',
  },
  placeholder: {
    type: String,
    default: 'Enter password',
  },
  autocomplete: {
    type: String,
    default: 'current-password',
  },
  required: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])
const showPassword = ref(false)

function toggleVisibility() {
  showPassword.value = !showPassword.value
}
</script>

<template>
  <div class="password-field">
    <input
      :id="id"
      :name="name"
      :type="showPassword ? 'text' : 'password'"
      :value="modelValue"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :required="required"
      :disabled="disabled"
      @input="emit('update:modelValue', $event.target.value)"
    />

    <button
      class="password-toggle"
      type="button"
      :aria-label="showPassword ? 'Hide password' : 'Show password'"
      :aria-pressed="showPassword"
      :disabled="disabled"
      @click="toggleVisibility"
    >
      <!-- Eye icon -->
      <svg
        v-if="!showPassword"
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z" />
        <circle cx="12" cy="12" r="3" />
      </svg>

      <!-- Eye-off icon -->
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="m3 3 18 18" />
        <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
        <path d="M9.9 5.2A10.8 10.8 0 0 1 12 5c6.4 0 10 7 10 7a14.8 14.8 0 0 1-3.1 3.9" />
        <path d="M6.2 6.2C3.5 8.1 2 12 2 12s3.6 7 10 7c1.1 0 2.1-.2 3-.5" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.password-field {
  position: relative;
  width: 100%;
}

.password-field input {
  box-sizing: border-box;
  width: 100%;
  padding: 10px 46px 10px 12px;
}

.password-toggle {
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  padding: 0;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #555;
  cursor: pointer;
  z-index: 1;
}

.password-toggle:hover {
  background: #f0f0f0;
  color: #111;
}

.password-toggle:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

.password-toggle:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
