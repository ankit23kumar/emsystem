<script setup>
import { onMounted, ref } from 'vue'
import { useUsers } from '../composables/useUsers'
import { useRouter } from 'vue-router'
import { clearSession } from '../services/auth'
import { deleteUser as deleteUserRequest } from '../services/userService'

const router = useRouter()

const {
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
} = useUsers(router)


const successMessage = ref('')
const deletingUserId = ref(null)

// async function loadUsers(page = 1) {
//     loading.value = true
//     errorMessage.value = ''

//     try {
//         const response = await getUsers( {
//             params: {
//                 page,
//                 page_size: pageSize,
//             },
//         })

//         const data = response.data

//         users.value = data.users || []
//         currentPage.value = data.pagination.current_page
//         totalUsers.value = data.pagination.total_users
//         totalPages.value = data.pagination.total_pages
//         hasNext.value = data.pagination.has_next
//         hasPrevious.value = data.pagination.has_previous
//     } catch (error) {
//         const status = error.response?.status

//         if (status === 401) {
//             errorMessage.value = 'Your session has expired. Please log in again.'
//             clearSession()
//             router.replace('/')
//         } else if (status === 403) {
//             errorMessage.value =
//                 error.response.data?.error ||
//                 'Your account is not permitted to access this information.'
//         } else if (!error.response) {
//             errorMessage.value = 'Cannot connect to the server. Please try again.'
//         } else {
//             errorMessage.value =
//                 error.response.data?.error || 'Failed to load the user list.'
//         }
//     } finally {
//         loading.value = false
//     }
// }

function previousPage() {
    if (hasPrevious.value && !loading.value) {
        loadUsers(currentPage.value - 1)
    }
}

function nextPage() {
    if (hasNext.value && !loading.value) {
        loadUsers(currentPage.value + 1)
    }
}

function goToDashboard() {
    router.push('/dashboard')
}

function createUser() {
    router.push({ name: 'user-create' })
}

function editUser(user) {
    router.push({
        name: 'user-edit',
        params: { userId: user.user_id },
        state: {
            selectedUser: {
                user_id: user.user_id,
                first_name: user.first_name,
                last_name: user.last_name,
                email: user.email,
                created_at: user.created_at,
                valid_until: user.valid_until,
            },
        },
    })
}


async function deleteUser(user) {
    const fullName = `${user.first_name} ${user.last_name}`.trim()

    const confirmed = window.confirm(
        `Are you sure you want to delete ${fullName} (${user.email})? This action cannot be undone.`
    )

    if (!confirmed) return

    errorMessage.value = ''
    successMessage.value = ''
    deletingUserId.value = user.user_id

    try {
        const response = await deleteUserRequest(user.user_id)

        const message =
            response.data.message || 'User deleted successfully.'

        // Move to the previous page if this was the only user on the current page.
        const pageToLoad =
            users.value.length === 1 && currentPage.value > 1
                ? currentPage.value - 1
                : currentPage.value

        await loadUsers(pageToLoad)

        // Set the message after refreshing the list.
        successMessage.value = message
    } catch (error) {
        if (error.response?.status === 401) {
            clearSession()
            router.push('/')
            return
        }

        errorMessage.value =
            error.response?.data?.error ||
            error.response?.data?.message ||
            'Unable to delete the user. Please try again.'
    } finally {
        deletingUserId.value = null
    }
}

onMounted(() => loadUsers())
</script>

<template>
    <main class="users-page">
        <header class="topbar">
            <div>
                <h1>EMSystem</h1>
                <p>Employee Management System</p>
            </div>

            <button class="back-button" @click="goToDashboard">
                Back to dashboard
            </button>
        </header>

        <section class="content">
            <div class="page-heading">
                <div>
                    <h2>Users</h2>
                    <p>View and manage registered users in the system.</p>
                </div>

                <div class="heading-actions">
                    <span class="user-count">{{ totalUsers }} total users</span>
                    <button class="create-button" @click="createUser">
                        + Create User
                    </button>
                </div>
            </div>

            <p v-if="errorMessage" class="message error" role="alert">
                {{ errorMessage }}
            </p>
            <p v-if="successMessage" class="message success" role="status">
                {{ successMessage }}
            </p>

            <div class="table-card">
                <div v-if="loading" class="empty-state">
                    Loading users...
                </div>

                <div v-else-if="users.length === 0 && !errorMessage" class="empty-state">
                    No users found.
                </div>

                <div v-else-if="users.length > 0" class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>First name</th>
                                <th>Last name</th>
                                <th>Email</th>
                                <th>Created at</th>
                                <th>Valid until</th>
                                <th>Action</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="user in users" :key="user.user_id">
                                <td>{{ user.user_id }}</td>
                                <td>{{ user.first_name }}</td>
                                <td>{{ user.last_name }}</td>
                                <td>{{ user.email }}</td>
                                <td>{{ user.created_at || '—' }}</td>
                                <td>{{ user.valid_until || '—' }}</td>
                                <td>
                                    <div class="action-buttons">
                                        <button type="button" class="edit-button" @click="editUser(user)">
                                            Edit
                                        </button>

                                        <button type="button" class="delete-button" @click="deleteUser(user)"
                                            :disabled="deletingUserId === user.user_id">
                                            {{
                                                deletingUserId === user.user_id
                                                    ? 'Deleting...'
                                            : 'Delete'
                                            }}
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <footer class="pagination">
                    <span>
                        Page {{ currentPage }} of {{ totalPages }}
                    </span>

                    <div class="pagination-buttons">
                        <button class="page-button" :disabled="!hasPrevious || loading" @click="previousPage">
                            Previous
                        </button>

                        <button class="page-button" :disabled="!hasNext || loading" @click="nextPage">
                            Next
                        </button>
                    </div>
                </footer>
            </div>
        </section>
    </main>
</template>

<style scoped>
.users-page {
    min-height: 100vh;
    background: #f3f6fb;
    color: #172b4d;
    font-family: Arial, Helvetica, sans-serif;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 20px 5%;
    background: white;
    border-bottom: 1px solid #e5eaf2;
}

.topbar h1 {
    margin: 0;
    font-size: 23px;
}

.topbar p {
    margin: 5px 0 0;
    color: #718096;
    font-size: 13px;
}

.back-button,
.page-button {
    padding: 10px 14px;
    border: 1px solid #d5dce7;
    border-radius: 7px;
    background: white;
    color: #344054;
    cursor: pointer;
}

.back-button:hover,
.page-button:hover:not(:disabled) {
    background: #f8fafc;
}

.content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px 24px;
}

.page-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 24px;
}

.page-heading h2 {
    margin: 0;
    font-size: 26px;
}

.page-heading p {
    margin: 8px 0 0;
    color: #718096;
    font-size: 14px;
}

.user-count {
    color: #344054;
    font-size: 14px;
    font-weight: 600;
}

.table-card {
    overflow: hidden;
    border: 1px solid #e5eaf2;
    border-radius: 12px;
    background: white;
}

.table-wrapper {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    white-space: nowrap;
}

th,
td {
    padding: 15px 18px;
    border-bottom: 1px solid #edf0f5;
    font-size: 13px;
}

th {
    background: #f8fafc;
    color: #475467;
    font-weight: 600;
}

td {
    color: #344054;
}

tbody tr:hover {
    background: #f8fafc;
}

.empty-state {
    padding: 36px 20px;
    text-align: center;
    color: #718096;
    font-size: 14px;
}

.pagination {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 16px 20px;
    color: #667085;
    font-size: 13px;
}

.pagination-buttons {
    display: flex;
    gap: 8px;
}

.page-button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.message {
    padding: 12px 14px;
    margin-bottom: 16px;
    border-radius: 8px;
    font-size: 14px;
}

.error {
    color: #b42318;
    background: #fef3f2;
    border: 1px solid #fecdca;
}

@media (max-width: 600px) {
    .content {
        padding: 24px 12px;
    }

    .page-heading {
        align-items: flex-start;
        flex-direction: column;
    }

    .topbar {
        align-items: flex-start;
    }

    .pagination {
        align-items: flex-start;
        flex-direction: column;
    }
}

.heading-actions {
    display: flex;
    align-items: center;
    gap: 14px;
}

.create-button,
.edit-button {
    padding: 9px 13px;
    border: 0;
    border-radius: 7px;
    background: #2563eb;
    color: white;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}

.create-button:hover,

/* Success and error messages */
.message.success {
    color: #067647;
    background: #ecfdf3;
    border: 1px solid #abefc6;
}

.message.error {
    color: #b42318;
    background: #fef3f2;
    border: 1px solid #fecdca;
}

/* Action buttons inside the table */
.action-buttons {
    display: flex;
    align-items: center;
    gap: 8px;
}

.edit-button,
.delete-button {
    padding: 8px 12px;
    border: none;
    border-radius: 6px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.edit-button {
    background: #2563eb;
}

.edit-button:hover {
    background: #1d4ed8;
}

.delete-button {
    background: #dc2626;
}

.delete-button:hover:not(:disabled) {
    background: #b91c1c;
}

.delete-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

@media (max-width: 600px) {
    .heading-actions {
        align-items: flex-start;
        flex-direction: column;
    }
}
</style>
