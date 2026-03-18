/**认证状态管理（Pinia） */
import { defineStore } from 'pinia'
import { ref } from 'vue'

interface AuthUser {
  id: string
  username: string
  email?: string | null
}

function loadStoredUser(): AuthUser | null {
  const raw = localStorage.getItem('user')
  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw) as AuthUser
  } catch {
    localStorage.removeItem('user')
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<AuthUser | null>(loadStoredUser())
  const isAuthenticated = ref<boolean>(!!token.value)

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    isAuthenticated.value = true
  }

  const logout = () => {
    token.value = null
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const setUser = (newUser: AuthUser) => {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  return {
    token,
    user,
    isAuthenticated,
    setToken,
    logout,
    setUser,
  }
})
