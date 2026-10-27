
import { ref } from 'vue'
import { getUsers } from '../services/userService'
import { clearSession } from '../services/auth'

export function useUsers(router) {
  const users = ref([])
  const loading = ref(false)
  const errorMessage = ref('')

  const currentPage = ref(1)
  const pageSize = ref(10)
  const totalUsers = ref(0)
  const totalPages = ref(0)
  const hasNext = ref(false)
  const hasPrevious = ref(false)

  async function loadUsers(page = 1) {
    loading.value = true
    errorMessage.value = ''

    try {
      const response = await getUsers({
        page,
        page_size: pageSize.value,
      })

      const data = response.data
      const pagination = data.pagination

      users.value = data.users || []
      currentPage.value = pagination.current_page
      totalUsers.value = pagination.total_users
      totalPages.value = pagination.total_pages
      hasNext.value = pagination.has_next
      hasPrevious.value = pagination.has_previous
    } catch (error) {
      const status = error.response?.status

      if (status === 401) {
        errorMessage.value =
          'Your session has expired. Please log in again.'
        clearSession()
        router.replace('/')
      } else if (status === 403) {
        errorMessage.value =
          error.response.data?.error ||
          'Your account is not permitted to access this information.'
      } else if (!error.response) {
        errorMessage.value =
          'Cannot connect to the server. Please try again.'
      } else {
        errorMessage.value =
          error.response.data?.error ||
          'Failed to load the user list.'
      }
    } finally {
      loading.value = false
    }
  }

  return {
    users,
    loading,
    errorMessage,
    currentPage,
    pageSize,
    totalUsers,
    totalPages,
    hasNext,
    hasPrevious,
    loadUsers,
  }
}
