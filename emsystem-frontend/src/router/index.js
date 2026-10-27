
import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import UserListView from '../views/UserListView.vue'
import { isAuthenticated } from '../services/auth'
// import UserFormView from '../views/UserFormView.vue'


const routes = [
  {
    path: '/',
    name: 'login',
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { guestOnly: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/users',
    name: 'users',
    component: UserListView,
    meta: { requiresAuth: true },
  },
  // {
  //   path: '/users/new',
  //   name: 'user-create',
  //   component: UserFormView,
  //   meta: { requiresAuth: true },
  // },
  // {
  //   path: '/users/:userId/edit',
  //   name: 'user-edit',
  //   component: UserFormView,
  //   meta: { requiresAuth: true }, 
  // },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const authenticated = isAuthenticated()

  if (to.meta.requiresAuth && !authenticated) {
    return { name: 'login' }
  }

  if (to.meta.guestOnly && authenticated) {
    return { name: 'dashboard' }
  }
})

export default router