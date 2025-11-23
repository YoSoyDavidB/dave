import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, type Mock } from 'vitest'
import App from './App'
import { useAuthStore } from './stores/authStore'


// Mock the useAuthStore
vi.mock('./stores/authStore', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./stores/authStore')>()
  return {
    ...actual,
    useAuthStore: vi.fn(),
  }
})

describe('App Routing', () => {
  // Common setup for tests
  const setup = (initialEntries = ['/']) => {
    return render(
      <MemoryRouter initialEntries={initialEntries}>
        <App />
      </MemoryRouter>
    )
  }

  it('renders LoginPage for unauthenticated user', async () => {
    // Mock unauthenticated state
    (useAuthStore as unknown as Mock).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      checkAuthStatus: vi.fn(),
      login: vi.fn(),
      error: null,
      clearError: vi.fn(),
    })

    setup(['/'])

    // Assert that elements from the LoginPage are rendered
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Welcome back/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Sign in/i })).toBeInTheDocument()
    })
  })

  it('renders Chat page for authenticated user', async () => {
    // Mock authenticated state
    (useAuthStore as unknown as Mock).mockReturnValue({
      user: { id: '123', email: 'test@example.com' },
      isAuthenticated: true,
      isLoading: false,
      checkAuthStatus: vi.fn(),
      login: vi.fn(),
      error: null,
      clearError: vi.fn(),
    })

    setup(['/'])

    // Assert that elements from the Chat page are rendered
    await waitFor(() => {
      expect(screen.getByText(/Hey there! What can/i)).toBeInTheDocument()
    })
  })

  it('navigates to Dashboard for authenticated user', async () => {
    // Mock authenticated state
    (useAuthStore as unknown as Mock).mockReturnValue({
      user: { id: '123', email: 'test@example.com' },
      isAuthenticated: true,
      isLoading: false,
      checkAuthStatus: vi.fn(),
      login: vi.fn(),
      error: null,
      clearError: vi.fn(),
    })

    setup(['/dashboard'])

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Dashboard/i })).toBeInTheDocument()
    })
  })

  it('redirects to Login from a protected route if unauthenticated', async () => {
    // Mock unauthenticated state
    (useAuthStore as unknown as Mock).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      checkAuthStatus: vi.fn(),
      login: vi.fn(),
      error: null,
      clearError: vi.fn(),
    })

    // Try to access a protected route directly
    setup(['/dashboard'])

    // Should redirect to login page
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Welcome back/i })).toBeInTheDocument()
    })
  })

  it('renders RegisterPage when navigating to /register', async () => {
    // Mock unauthenticated state for clarity, though /register is usually public
    (useAuthStore as unknown as Mock).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      checkAuthStatus: vi.fn(),
    });

    setup(['/register'])

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Create account/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Create account/i })).toBeInTheDocument()
    })
  });
})
