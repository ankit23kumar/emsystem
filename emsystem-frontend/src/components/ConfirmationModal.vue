
<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: "Are you sure?",
  },
  message: {
    type: String,
    default: "Please confirm that you want to continue.",
  },
  confirmText: {
    type: String,
    default: "Confirm",
  },
  cancelText: {
    type: String,
    default: "Cancel",
  },
  variant: {
    type: String,
    default: "danger",
    validator: (value) => ["danger", "primary"].includes(value),
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "update:modelValue",
  "confirm",
  "cancel",
]);

function closeModal() {
  if (props.loading) return;

  emit("update:modelValue", false);
  emit("cancel");
}

function confirmAction() {
  if (props.loading) return;

  emit("confirm");
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="confirmation-backdrop"
      @click.self="closeModal"
    >
      <section
        class="confirmation-modal"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirmation-title"
        aria-describedby="confirmation-message"
      >
        <div class="confirmation-icon" :class="variant">
          <span v-if="variant === 'danger'">!</span>
          <span v-else>?</span>
        </div>

        <h2 id="confirmation-title">{{ title }}</h2>
        <p id="confirmation-message">{{ message }}</p>

        <div class="confirmation-actions">
          <button
            type="button"
            class="confirmation-cancel"
            :disabled="loading"
            @click="closeModal"
          >
            {{ cancelText }}
          </button>

          <button
            type="button"
            class="confirmation-submit"
            :class="variant"
            :disabled="loading"
            @click="confirmAction"
          >
            {{ loading ? "Please wait..." : confirmText }}
          </button>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.confirmation-backdrop {
  position: fixed;
  z-index: 1000;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(16, 24, 40, 0.55);
}

.confirmation-modal {
  width: min(100%, 420px);
  padding: 28px;
  border: 1px solid #eaecf0;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 20px 50px rgba(16, 24, 40, 0.2);
  text-align: center;
}

.confirmation-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  border-radius: 50%;
  font-size: 25px;
  font-weight: 700;
}

.confirmation-icon.danger {
  background: #fee2e2;
  color: #dc2626;
}

.confirmation-icon.primary {
  background: #dbeafe;
  color: #2864ed;
}

.confirmation-modal h2 {
  margin: 0 0 10px;
  color: #151d2e;
  font-size: 20px;
}

.confirmation-modal p {
  margin: 0;
  color: #667085;
  font-size: 14px;
  line-height: 1.6;
  overflow-wrap: anywhere;
}

.confirmation-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 25px;
}

.confirmation-actions button {
  min-width: 110px;
  padding: 10px 16px;
  border: 1px solid transparent;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
}

.confirmation-cancel {
  border-color: #d0d5dd !important;
  background: #fff;
  color: #344054;
}

.confirmation-cancel:hover:not(:disabled) {
  background: #f9fafb;
}

.confirmation-submit.danger {
  background: #dc2626;
  color: #fff;
}

.confirmation-submit.danger:hover:not(:disabled) {
  background: #b91c1c;
}

.confirmation-submit.primary {
  background: #2864ed;
  color: #fff;
}

.confirmation-submit.primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.confirmation-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
