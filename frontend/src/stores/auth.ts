import { writable } from 'svelte/store'

interface AuthState {
  token: string | null
  user: any | null
  loading: boolean
  error: string | null
}

const initialState: AuthState = {
  token: localStorage.getItem('token'),
  user: null,
  loading: false,
  error: null
}

export const authStore = writable<AuthState>(initialState)

export const login = async (email: string, password: string) => {
  authStore.update(state => ({ ...state, loading: true, error: null }))
  
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    
    if (!response.ok) {
      throw new Error('Falha ao fazer login')
    }
    
    const data = await response.json()
    localStorage.setItem('token', data.access_token)
    
    authStore.set({
      token: data.access_token,
      user: data.user,
      loading: false,
      error: null
    })
  } catch (error: any) {
    authStore.update(state => ({
      ...state,
      loading: false,
      error: error.message
    }))
  }
}

export const register = async (email: string, password: string, nome: string = '') => {
  authStore.update(state => ({ ...state, loading: true, error: null }))
  
  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, nome })
    })
    
    if (!response.ok) {
      throw new Error('Falha ao registrar')
    }
    
    const data = await response.json()
    localStorage.setItem('token', data.access_token)
    
    authStore.set({
      token: data.access_token,
      user: data.user,
      loading: false,
      error: null
    })
  } catch (error: any) {
    authStore.update(state => ({
      ...state,
      loading: false,
      error: error.message
    }))
  }
}

export const logout = () => {
  localStorage.removeItem('token')
  authStore.set({
    token: null,
    user: null,
    loading: false,
    error: null
  })
}

export const loadUser = async () => {
  const token = localStorage.getItem('token')
  if (!token) return

  authStore.update(state => ({ ...state, loading: true }))
  try {
    const response = await fetch('/api/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      const user = await response.json()
      authStore.update(state => ({
        ...state,
        user,
        loading: false
      }))
    } else {
      logout()
    }
  } catch (error) {
    authStore.update(state => ({ ...state, loading: false }))
  }
}
