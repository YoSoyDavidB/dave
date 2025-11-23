import { create } from 'zustand'
import {
  login as loginApi,
  logout as logoutApi,
  getMe as getMeApi,
  LoginCredentials,
  RegisterCredentials,
  register as registerApi,
  User,
} from '../services/api' // These will be added to api.ts

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => Promise<void>
  checkAuthStatus: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true, // Start with loading to check auth status
  error: null,

  login: async (credentials: LoginCredentials) => {
    try {
      set({ isLoading: true, error: null })
      const user = await loginApi(credentials)
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed',
      })
      throw error // Re-throw for the component to handle
    }
  },

  register: async (credentials: RegisterCredentials) => {
    try {
      set({ isLoading: true, error: null })
      await registerApi(credentials)
      // Automatically log in after successful registration
      await useAuthStore.getState().login({ email: credentials.email, password: credentials.password })
    } catch (error) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Registration failed',
      })
      throw error // Re-throw for the component to handle
    }
  },

  logout: async () => {
    try {
      set({ isLoading: true, error: null })
      await logoutApi()
      set({ user: null, isAuthenticated: false, isLoading: false })
    } catch (error) {
      // Still log out on the client side even if server fails
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Logout failed',
      })
    }
  },

  checkAuthStatus: async () => {
    try {
      set({ isLoading: true, error: null })
      const user = await getMeApi()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },

  clearError: () => set({ error: null }),
}))
