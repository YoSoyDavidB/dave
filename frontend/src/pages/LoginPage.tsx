import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Mail, Lock, LogIn, Loader2 } from 'lucide-react'

// Smoke orb component matching the main app design
function SmokeOrb() {
  return (
    <div className="w-24 h-24 avatar-orb-large relative">
      <div className="smoke-particle smoke-particle-1" />
      <div className="smoke-particle smoke-particle-2" />
      <div className="smoke-particle smoke-particle-3" />
      <div className="avatar-inner-ring" />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-6 h-6 rounded-full bg-[#F0FF3D]/30 blur-md animate-pulse" />
      </div>
    </div>
  )
}

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { login, error, clearError, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    try {
      await login({ email, password })
      navigate('/')
    } catch (err) {
      // Error is handled by the store
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo and welcome */}
        <div className="flex flex-col items-center mb-8">
          <div className="relative mb-6 animate-float">
            <div className="glow-primary rounded-full">
              <SmokeOrb />
            </div>
            <div className="absolute -inset-4 rounded-full border border-[#F0FF3D]/20 animate-pulse" style={{ animationDuration: '3s' }} />
          </div>
          <h1 className="text-3xl font-semibold text-white mb-2">Welcome back</h1>
          <p className="text-zinc-500 text-center">Sign in to continue with Dave</p>
        </div>

        {/* Login form card */}
        <div className="glass-card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email field */}
            <div>
              <label className="block mb-2 text-sm font-medium text-zinc-400">Email</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail size={18} className="text-zinc-500" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full pl-11 pr-4 py-3 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-[#F0FF3D]/40 focus:shadow-[0_0_0_3px_rgba(240,255,61,0.08)] transition-all duration-300"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password field */}
            <div>
              <label className="block mb-2 text-sm font-medium text-zinc-400">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock size={18} className="text-zinc-500" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-3 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-[#F0FF3D]/40 focus:shadow-[0_0_0_3px_rgba(240,255,61,0.08)] transition-all duration-300"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Error message */}
            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm">
                {error}
              </div>
            )}

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading || !email.trim() || !password.trim()}
              className="w-full py-3 btn-gradient rounded-xl font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <LogIn size={18} />
                  Sign in
                </>
              )}
            </button>
          </form>
        </div>

        {/* Footer */}
        <p className="text-center text-zinc-600 text-sm mt-6">
          Your AI friend for productivity and learning
        </p>
      </div>
    </div>
  )
}
