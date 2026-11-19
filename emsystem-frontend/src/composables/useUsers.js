import { ref } from "vue";
import { getUsers } from "../services/userService";
import { clearSession } from "../services/auth";

export function useUsers(router) {
  const users = ref([]);
  const loading = ref(false);
  const errorMessage = ref("");

  const currentPage = ref(1);
  const pageSize = ref(10);
  const totalUsers = ref(0);
  const totalPages = ref(0);
  const hasNext = ref(false);
  const hasPrevious = ref(false);

  // Server-side search, sorting and filtering options
  const filters = ref({
    search: "",
    sort_by: "user_id", //sort_by: 'first_name',
    order: "asc",
    letter: "",
  });
  let abortController = null;
  let requestId = 0;

  async function loadUsers(page = 1) {
    // Cancel the previous request if it is still running.
    abortController?.abort();

    // Create a new controller.
    abortController = new AbortController();

    // Identify this request.
    const currentRequestId = ++requestId;

    loading.value = true;
    errorMessage.value = "";

    try {
      const response = await getUsers(
        {
          page,
          page_size: pageSize.value,
          search: filters.value.search,
          sort_by: filters.value.sort_by,
          order: filters.value.order,
          letter: filters.value.letter,
        },
        abortController.signal,
      );

      // Ignore outdated responses.
      if (currentRequestId !== requestId) return;

      const data = response.data;
      const pagination = data.pagination;

      users.value = data.users || [];
      currentPage.value = pagination.current_page;
      totalUsers.value = pagination.total_users;
      totalPages.value = pagination.total_pages;
      hasNext.value = pagination.has_next;
      hasPrevious.value = pagination.has_previous;
    } catch (error) {
      // Ignore intentionally cancelled requests.
      if (error.code === "ERR_CANCELED") return;

      // Ignore errors from outdated requests.
      if (currentRequestId !== requestId) return;

      const status = error.response?.status;

      if (status === 401) {
        errorMessage.value = "Your session has expired. Please log in again.";

        clearSession();
        router.replace("/");
      } else if (status === 403) {
        errorMessage.value =
          error.response.data?.error ||
          "Your account is not permitted to access this information.";
      } else if (!error.response) {
        errorMessage.value = "Cannot connect to the server. Please try again.";
      } else {
        errorMessage.value =
          error.response.data?.error || "Failed to load the user list.";
      }
    } finally {
      // Only the latest request controls the loading state.
      if (currentRequestId === requestId) {
        loading.value = false;
      }
    }
  }

  // Update filters and reload from page 1
  async function updateFilters(newFilters) {
    filters.value = {
      ...filters.value,
      ...newFilters,
    };

    await loadUsers(1);
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
    filters,
    loadUsers,
    updateFilters,
  };
}
