<script setup>
import { reactive, ref, computed } from "vue";
import { resetPassword } from "../services/authService.js";
import { useToast } from "../composables/useToast";
import PasswordInput from "./PasswordInput.vue";

const emit = defineEmits(["close", "reset-success"]);

const { showToast } = useToast();

const form = reactive({
  email: "",
  new_password: "",
  confirm_password: "",
});

const errors = reactive({
  email: "",
  password: "",
  confirmPassword: "",
});

const passwordsMismatch = computed(() => {
  return (
    form.confirm_password.length > 0 &&
    form.new_password !== form.confirm_password
  );
});

const loading = ref(false);

function clearErrors() {
  errors.email = "";
  errors.password = "";
  errors.confirmPassword = "";
}

function closeModal() {
  if (loading.value) return;
  emit("close");
}

async function handlePasswordReset() {
  clearErrors();

  const email = form.email.trim();

  if (!email) {
    errors.email = "Please enter your email address.";
    return;
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = "Please enter a valid email address.";
    return;
  }

  if (form.new_password.length < 8 || form.new_password.length > 128) {
    errors.password = "Password must be between 8 and 128 characters.";
    return;
  }

  if (form.new_password !== form.confirm_password) {
    errors.confirmPassword = "Passwords do not match.";
    return;
  }

  loading.value = true;

  try {
    await resetPassword({
      email,
      new_password: form.new_password,
      confirm_password: form.confirm_password,
    });

    form.new_password = "";
    form.confirm_password = "";

    // LoginView handles closing the modal and showing the success toast.
    emit("reset-success");
  } catch (error) {
    const data = error.response?.data;

    if (data?.error || data?.message) {
      showToast(data.error || data.message, "error");
    } else if (error.response) {
      showToast(
        `Password reset failed (HTTP ${error.response.status}).`,
        "error",
      );
    } else if (error.code === "ECONNABORTED") {
      showToast("The request timed out. Please try again.", "error");
    } else {
      showToast(
        "Unable to connect to the server. Check that Django is running.",
        "error",
      );
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="closeModal" @keydown.esc="closeModal">
    <section
      class="reset-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="reset-title"
    >
      <button
        type="button"
        class="close-button"
        aria-label="Close password reset dialog"
        :disabled="loading"
        @click="closeModal"
      >
        ×
      </button>

      <div class="modal-heading">
        <div class="modal-icon" aria-hidden="true">E</div>
        <h2 id="reset-title">Reset password</h2>
        <p>Enter your email and choose a new password.</p>
      </div>

      <form @submit.prevent="handlePasswordReset" novalidate>
        <div class="form-group">
          <label for="reset-email">Email address</label>
          <input
            id="reset-email"
            v-model="form.email"
            type="email"
            name="email"
            placeholder="you@example.com"
            autocomplete="email"
            required
            :disabled="loading"
            :class="{ 'input-error': errors.email }"
            :aria-invalid="Boolean(errors.email)"
            @input="errors.email = ''"
          />

          <small v-if="errors.email" class="field-error" role="alert">
            {{ errors.email }}
          </small>
        </div>

        <div class="form-group">
          <label for="reset-new-password">New password</label>
          <PasswordInput
            id="reset-new-password"
            v-model="form.new_password"
            name="new_password"
            placeholder="Enter new password"
            autocomplete="new-password"
            :required="true"
            :disabled="loading"
          />

          <small v-if="errors.password" class="field-error" role="alert">
            {{ errors.password }}
          </small>
        </div>

        <div class="form-group">
          <label for="reset-confirm-password"> Confirm new password </label>

          <PasswordInput
            id="reset-confirm-password"
            v-model="form.confirm_password"
            name="confirm_password"
            placeholder="Re-enter new password"
            autocomplete="new-password"
            :required="true"
            :disabled="loading"
          />

          <small
            v-if="errors.confirmPassword || passwordsMismatch"
            class="field-error"
            role="alert"
          >
            {{ errors.confirmPassword || "Passwords do not match." }}
          </small>
        </div>

        <button type="submit" class="reset-button" :disabled="loading">
          {{ loading ? "Resetting password..." : "Reset password" }}
        </button>
      </form>

      <button
        type="button"
        class="back-button"
        :disabled="loading"
        @click="closeModal"
      >
        Back to login
      </button>
    </section>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  overflow-y: auto;
  padding: 24px 16px;
  background: rgb(15 23 42 / 55%);
}

.reset-modal {
  position: relative;
  width: 100%;
  max-width: 440px;
  padding: 32px;
  border: 1px solid #e5eaf2;
  border-radius: 16px;
  background: #fff;
  color: #172033;
  box-shadow: 0 20px 60px rgb(0 0 0 / 20%);
}

.close-button {
  position: absolute;
  top: 12px;
  right: 16px;
  border: 0;
  background: transparent;
  color: #697386;
  font-size: 28px;
  cursor: pointer;
}

.modal-heading {
  margin-bottom: 24px;
  text-align: center;
}

.modal-icon {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin: 0 auto 14px;
  border-radius: 12px;
  background: #2457d6;
  color: white;
  font-size: 22px;
  font-weight: 700;
}

.modal-heading h2 {
  margin: 0 0 8px;
  font-size: 23px;
}

.modal-heading p {
  margin: 0;
  color: #697386;
  font-size: 14px;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
}

.form-group input {
  box-sizing: border-box;
  width: 100%;
  min-height: 46px;
  padding: 11px 12px;
  border: 1px solid #cfd6e2;
  border-radius: 9px;
  background: #fff;
  color: #172033;
  font: inherit;
  font-size: 14px;
}

.form-group input:focus-visible {
  outline: 3px solid rgb(36 87 214 / 18%);
  border-color: #2457d6;
}

.form-group input:disabled {
  background: #f3f5f8;
}

.feedback {
  padding: 11px 12px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.error {
  background: #fff0f0;
  color: #a51d2d;
}

.success {
  background: #eaf8ef;
  color: #176b38;
}

.reset-button {
  width: 100%;
  min-height: 46px;
  margin-top: 4px;
  border: 0;
  border-radius: 9px;
  background: #2457d6;
  color: white;
  font: inherit;
  font-weight: 650;
  cursor: pointer;
}

.reset-button:hover:not(:disabled) {
  background: #1946b8;
}

.reset-button:disabled,
.back-button:disabled,
.close-button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.back-button {
  display: block;
  margin: 18px auto 0;
  padding: 6px;
  border: 0;
  background: transparent;
  color: #2457d6;
  font: inherit;
  font-size: 14px;
  cursor: pointer;
}

.password-warning {
  margin: 8px 0 0;
  color: #a51d2d;
  font-size: 13px;
  line-height: 1.4;
}

@media (max-width: 480px) {
  .reset-modal {
    padding: 28px 20px;
  }
}

.input-error {
  border-color: #d92d20 !important;
}

.field-error {
  display: block;
  margin-top: 6px;
  color: #b42318;
  font-size: 13px;
  line-height: 1.4;
}
</style>
