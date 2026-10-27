import api from './api'

// Authenticate the existing user
export function loginUser(credentials){
    return api.post('/login',credentials)
}

//register
export function registerUser(userData){
    return api.post('/register',userData)
}

//reset password of a user
export function resetPassword(passwordData){
    return api.post('/password-reset',passwordData)
}
