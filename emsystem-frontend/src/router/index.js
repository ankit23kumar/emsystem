import { createRouter, createWebHistory } from "vue-router";

const LoginView = () => import("../views/LoginView.vue");
const RegisterView = () => import("../views/RegisterView.vue");
const DashboardView = () => import("../views/DashboardView.vue");
const UserListView = () => import("../views/UserListView.vue");
const RoleManagementPanel = () => import("../components/dashboard/RoleManagementPanel.vue");
import { useAuthStore } from "../stores/authStore";
import { isAuthenticated } from "../services/auth";

const routes = [
  {
    path: "/",
    name: "login",
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: "/register",
    name: "register",
    component: RegisterView,
    meta: { guestOnly: true },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: "/users",
    name: "users",
    component: UserListView,
    meta: { requiresAuth: true },
  },
  {
    path: "/role-panel-preview",
    name: "role-panel-preview",
    component: RoleManagementPanel,
    meta: {
      requiresAuth: true,
      requiredPermission: "roles.read",
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Global navigation guard
router.beforeEach(async (to) => {
  const authStore = useAuthStore();
  const authenticated = isAuthenticated();

  // No valid saved session
  if (!authenticated) {
    authStore.logout();

    if (to.meta.requiresAuth) {
      return { name: "login" };
    }

    return true;
  }

  // Restore profile and permissions after browser refresh
  if (!authStore.profileLoaded.value) {
    try {
      await authStore.initializeAuth();
    } catch (error) {
      console.error("Authentication initialization failed:", error);

      authStore.logout();
      return { name: "login" };
    }
  }

  // Prevent authenticated users from visiting guest pages
  if (to.meta.guestOnly) {
    return { name: "dashboard" };
  }

  // Check route-level permission
  if (
    to.meta.requiredPermission &&
    !authStore.hasPermission(to.meta.requiredPermission)
  ) {
    return { name: "dashboard" };
  }

  return true;
});

export default router;
