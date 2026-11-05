<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { registerUser } from "../services/authService.js";
import { useToast } from "../composables/useToast";
import PasswordInput from "../components/PasswordInput.vue";

const router = useRouter();
const { showToast } = useToast();

const firstName = ref("");
const lastName = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");

const loading = ref(false);
const errors = reactive({
  email: "",
});

async function handleRegister() {
  errors.email = "";

  const first = firstName.value.trim();
  const last = lastName.value.trim();
  const normalizedEmail = email.value.trim().toLowerCase();

  // Client-side validation
  if (
    !first ||
    !last ||
    !normalizedEmail ||
    !password.value ||
    !confirmPassword.value
  ) {
    showToast("Please fill in all fields.", "warning");
    return;
  }

  if (first.length > 30 || last.length > 30) {
    showToast(
      "First and last names must be 30 characters or fewer.",
      "warning",
    );
    return;
  }

  if (password.value.length < 8 || password.value.length > 128) {
    showToast("Password must be between 8 and 128 characters.", "warning");
    return;
  }

  if (password.value !== confirmPassword.value) {
    showToast("Passwords do not match.", "warning");
    return;
  }

  loading.value = true;

  try {
    const response = await registerUser({
      first_name: first,
      last_name: last,
      email: normalizedEmail,
      password: password.value,
    });

    showToast(
      response.data.message || "Registration successful! You can now log in.",
      "success",
    );

    // Registration does not automatically log in the user.
    password.value = "";
    confirmPassword.value = "";

    // Return to login after displaying the success notification.
    setTimeout(() => {
      router.push("/");
    }, 1500);
  } catch (error) {
    const status = error.response?.status;
    const data = error.response?.data;

    const message =
      data?.error || data?.message || "Registration failed. Please try again.";

    if (status === 409) {
      // Duplicate email: keep the error associated with the email field.
      errors.email =
        data?.error || "An account with this email already exists.";
    } else if (status === 400) {
      showToast(message, "warning");
    } else if (error.code === "ECONNABORTED") {
      showToast("The request timed out. Please try again.", "error");
    } else if (!error.response) {
      showToast("Cannot connect to the server. Please try again.", "error");
    } else {
      showToast(message, "error");
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card">
      <div class="brand">
        <div class="brand-icon">E</div>
        <h1>EMSystem</h1>
        <p>Create your employee account</p>
      </div>

      <form @submit.prevent="handleRegister">
        <div class="name-row">
          <div class="form-group">
            <label for="firstName">First name</label>
            <input
              id="firstName"
              v-model="firstName"
              type="text"
              maxlength="30"
              autocomplete="given-name"
              placeholder="First name"
              required
            />
          </div>

          <div class="form-group">
            <label for="lastName">Last name</label>
            <input
              id="lastName"
              v-model="lastName"
              type="text"
              maxlength="30"
              autocomplete="family-name"
              placeholder="Last name"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="email">Email address</label>
          <input
            id="email"
            v-model="email"
            :class="{ 'input-error': errors.email }"
            type="email"
            autocomplete="email"
            placeholder="you@example.com"
            required
            :aria-invalid="Boolean(errors.email)"
            @input="errors.email = ''"
          />

          <small v-if="errors.email" class="field-error" role="alert">
            {{ errors.email }}
          </small>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <PasswordInput
            id="password"
            v-model="password"
            name="password"
            type="password"
            autocomplete="new-password"
            placeholder="At least 8 characters"
            :required="true"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm password</label>
          <PasswordInput
            id="confirmPassword"
            v-model="confirmPassword"
            name="confirmPassword"
            type="password"
            autocomplete="new-password"
            placeholder="Re-enter your password"
            :required="true"
          />
        </div>


        <button type="submit" :disabled="loading">
          {{ loading ? "Creating account..." : "Create account" }}
        </button>
      </form>

      <p class="footer-text">
        Already have an account?
        <RouterLink to="/">Sign in</RouterLink>
      </p>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  background: #f3f6fb;
  font-family: Arial, Helvetica, sans-serif;
}

.auth-card {
  width: 100%;
  max-width: 460px;
  padding: 36px;
  background: #fff;
  border: 1px solid #e5eaf2;
  border-radius: 16px;
  box-shadow: 0 12px 35px rgba(24, 45, 80, 0.08);
}

.brand {
  text-align: center;
  margin-bottom: 28px;
}

.brand-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  display: grid;
  place-items: center;
  color: #fff;
  background: #2563eb;
  border-radius: 12px;
  font-size: 25px;
  font-weight: 700;
}

.brand h1 {
  margin: 0;
  color: #172b4d;
  font-size: 26px;
}

.brand p {
  margin: 8px 0 0;
  color: #718096;
  font-size: 14px;
}

.name-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 7px;
  color: #344054;
  font-size: 14px;
  font-weight: 600;
}

.form-group input {
  box-sizing: border-box;
  width: 100%;
  padding: 12px 13px;
  border: 1px solid #d5dce7;
  border-radius: 8px;
  outline: none;
  font-size: 14px;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.form-group input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.message {
  padding: 11px 12px;
  margin: 0 0 16px;
  border-radius: 7px;
  font-size: 13px;
  line-height: 1.5;
}

.error {
  color: #b42318;
  background: #fef3f2;
  border: 1px solid #fecdca;
}

.success {
  color: #067647;
  background: #ecfdf3;
  border: 1px solid #abefc6;
}

button {
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 8px;
  color: #fff;
  background: #2563eb;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover:not(:disabled) {
  background: #1d4ed8;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.footer-text {
  margin: 24px 0 0;
  text-align: center;
  color: #667085;
  font-size: 14px;
}

.footer-text a {
  color: #2563eb;
  font-weight: 600;
  text-decoration: none;
}

.footer-text a:hover {
  text-decoration: underline;
}

@media (max-width: 420px) {
  .auth-card {
    padding: 26px 20px;
  }

  .name-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}

.input-error {
  border-color: #d92d20;
}

.field-error {
  display: block;
  margin-top: 6px;
  color: #b42318;
  font-size: 12px;
}

</style>
