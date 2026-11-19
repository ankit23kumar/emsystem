<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { saveSession } from "../services/auth";
import { loginUser } from "../services/authService.js";
import { useToast } from "../composables/useToast";
import PasswordInput from "../components/PasswordInput.vue";
import PasswordResetModal from "../components/PasswordResetModal.vue";
import { useAuthStore } from "../stores/authStore";

const router = useRouter();
const authStore = useAuthStore();

const { showToast } = useToast();

const email = ref("");
const password = ref("");
const loading = ref(false);
const loggedInUser = ref(null);
const showPasswordResetModal = ref(false);

async function handleLogin() {
  loggedInUser.value = null;

  const normalizedEmail = email.value.trim();

  if (!normalizedEmail || !password.value) {
    showToast("Please enter your email and password.", "warning");
    return;
  }

  loading.value = true;

  try {
    const response = await loginUser({
      email: normalizedEmail,
      password: password.value,
    });

    const data = response.data;

    if (!data.access_token || !data.user) {
      showToast("The server returned an unexpected login response.", "error");
      return;
    }

    // loggedInUser.value = data.user

    // // Store the authenticated session.
    // saveSession(data)

    // password.value = ''
    saveSession(data);

    // Update the reactive authentication store
    authStore.setSession(data);

    // Fetch the latest profile and permissions
    try {
      await authStore.loadCurrentUser();
    } catch (error) {
      authStore.logout();
      throw error;
    }

    loggedInUser.value = authStore.user.value;

    password.value = "";

    showToast(data.message || "Login successful!", "success");

    // Navigate to the dashboard.
    await router.push("/dashboard");
  } catch (error) {
    const responseData = error.response?.data;

    if (responseData?.code === "account_expired") {
      showToast(responseData.error || "Your account has expired.", "warning");
    } else if (responseData?.error || responseData?.message) {
      showToast(responseData.error || responseData.message, "error");
    } else if (error.response) {
      showToast(
        `Request failed with status ${error.response.status}.`,
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

function handlePasswordResetSuccess() {
  showPasswordResetModal.value = false;

  showToast(
    "Password reset successful. Please sign in with your new password.",
    "success",
  );

  password.value = "";
}
</script>

<template>
  <main class="login-page">
    <section class="login-card" aria-labelledby="login-title">
      <div class="brand">
        <div class="brand-icon" aria-hidden="true">E</div>
        <p class="brand-name">EMSystem</p>
        <p class="brand-subtitle">Employee Management System</p>
      </div>

      <div class="form-heading">
        <h1 id="login-title">Welcome back</h1>
        <p>Sign in to continue to your account.</p>
      </div>

      <form @submit.prevent="handleLogin" novalidate>
        <div class="form-group">
          <label for="email">Email address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            name="email"
            placeholder="you@example.com"
            autocomplete="username"
            required
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <PasswordInput
            id="password"
            v-model="password"
            type="password"
            name="password"
            placeholder="Enter your password"
            autocomplete="current-password"
            required
            :disabled="loading"
          />
        </div>
        <div class="forgot-password-row">
          <button
            type="button"
            class="forgot-password-link"
            :disabled="loading"
            @click="showPasswordResetModal = true"
          >
            Forgot Password?
          </button>
        </div>

        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? "Signing in..." : "Sign in" }}
        </button>
      </form>
      <p class="footer-text">
        Don't have an account?
        <RouterLink to="/register">Create account</RouterLink>
      </p>
      <section v-if="loggedInUser" class="user-summary">
        <h2>Authenticated successfully</h2>
        <p>
          Welcome,
          {{ loggedInUser.first_name }}
          {{ loggedInUser.last_name }}.
        </p>
        <p>{{ loggedInUser.email }}</p>
      </section>

      <p class="footer-text">EMSystem · Employee Management</p>
    </section>
    <PasswordResetModal
      v-if="showPasswordResetModal"
      @close="showPasswordResetModal = false"
      @reset-success="handlePasswordResetSuccess"
    />
  </main>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px 16px;
  background: #f3f6fb;
  color: #172033;
}

.login-card {
  width: 100%;
  max-width: 430px;
  padding: 36px;
  background: #ffffff;
  border: 1px solid #e5eaf2;
  border-radius: 18px;
  box-shadow: 0 16px 45px rgb(25 42 70 / 8%);
}

.brand {
  text-align: center;
  margin-bottom: 32px;
}

.brand-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  border-radius: 14px;
  background: #2457d6;
  color: white;
  font-size: 24px;
  font-weight: 700;
}

.brand-name {
  margin: 0;
  font-size: 24px;
  font-weight: 750;
}

.brand-subtitle,
.form-heading p {
  color: #697386;
  font-size: 14px;
}

.brand-subtitle {
  margin: 6px 0 0;
}

.form-heading {
  margin-bottom: 24px;
}

.form-heading h1 {
  margin: 0 0 8px;
  font-size: 25px;
}

.form-heading p {
  margin: 0;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
}

.form-group input {
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

.login-button {
  width: 100%;
  min-height: 46px;
  margin-top: 4px;
  border: 0;
  border-radius: 9px;
  background: #2457d6;
  color: #fff;
  font: inherit;
  font-weight: 650;
  cursor: pointer;
}

.login-button:hover:not(:disabled) {
  background: #1946b8;
}

.login-button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.feedback {
  padding: 11px 12px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.error {
  background: #fff0f0;
  color: #a51d2d;
}

.success {
  background: #eaf8ef;
  color: #176b38;
}

.user-summary {
  margin-top: 20px;
  padding: 16px;
  border: 1px solid #b9e5c7;
  border-radius: 10px;
  background: #f1fbf4;
  overflow-wrap: anywhere;
}

.user-summary h2 {
  margin: 0 0 10px;
  font-size: 16px;
}

.user-summary p {
  margin: 6px 0;
  font-size: 14px;
}

.footer-text {
  margin: 26px 0 0;
  color: #8791a2;
  font-size: 12px;
  text-align: center;
}
.forgot-password-row {
  display: flex;
  justify-content: flex-end;
  margin-top: -8px;
  margin-bottom: 18px;
}

.forgot-password-link {
  padding: 4px 0;
  border: 0;
  background: transparent;
  color: #2457d6;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.forgot-password-link:hover:not(:disabled) {
  text-decoration: underline;
}

.forgot-password-link:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 480px) {
  .login-card {
    padding: 26px 20px;
  }
}
</style>
