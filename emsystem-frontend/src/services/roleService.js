
import api from './api'

// Fetch the predefined permission catalog.
export function getPermissions() {
    return api.get('/permissions')
}

// Fetch all roles.
export function getRoles() {
    return api.get('/roles')
}

// Fetch one role with its permissions and assigned users.
export function getRoleDetails(roleId) {
    return api.get(`/roles/${roleId}`)
}

// Create a new role.
export function createRole(roleData) {
    return api.post('/roles', roleData)
}

// Update an existing role.
export function updateRole(roleId, roleData) {
  return api.patch(`/roles/${roleId}/update`, roleData)
}

// Delete a role.
export function deleteRole(roleId) {
    return api.delete(`/roles/${roleId}`)
}

// Assign a role to a user or remove their existing role.
export function assignUserRole(userId, roleId) {
    return api.patch(`/user/${userId}/role`, {
        role_id: roleId,
    })
}
