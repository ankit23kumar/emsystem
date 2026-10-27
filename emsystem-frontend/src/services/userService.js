import api from './api'

//fetch a page of users
export function getUsers(params = {}){
    return api.get('/user-list', { params })
}

//Create a user
export function createUser(userData){
    return api.post('/user-create',userData)
}

// Complete update: all required fields must be supplied.
export function replaceUser(userId, userData) {
  return api.put(`/update/${userId}`, userData)
}

// Partial update: only supplied fields are changed.
export function updateUser(userId, userData) {
  return api.patch(`/update/${userId}`, userData)
}

// Delete a user.
export function deleteUser(userId) {
  return api.delete(`/delete/${userId}`)
}

// Fetch the currently authenticated user's profile.
export function getMyProfile() {
  return api.get('/me')
}

// Update a user's profile.
export function updateMyProfile(userData) {
  return api.patch('/me', userData)
}
