import { useEffect, useState } from 'react'
import { Play, Pause, Check, X, Loader2, Clock } from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import {
  startFocusSession,
  getActiveSession,
  pauseSession,
  resumeSession,
  completeSession,
  cancelSession,
  type FocusSession,
} from '../../services/api'

export default function FocusTimer() {
  const { user } = useAuthStore()
  const [session, setSession] = useState<FocusSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [remainingSeconds, setRemainingSeconds] = useState(0)
  const [notes, setNotes] = useState('')
  const [showNotesInput, setShowNotesInput] = useState(false)

  // Load active session on mount
  useEffect(() => {
    loadActiveSession()
  }, [user])

  // Timer countdown
  useEffect(() => {
    if (!session || session.status !== 'active') return

    const interval = setInterval(() => {
      setRemainingSeconds((prev) => {
        const newValue = prev - 1
        if (newValue <= 0) {
          // Session completed - play notification
          playNotification()
          return 0
        }
        return newValue
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [session])

  const loadActiveSession = async () => {
    if (!user) {
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)
      const activeSession = await getActiveSession(user.id)

      if (activeSession) {
        setSession(activeSession)
        setRemainingSeconds(activeSession.remaining_seconds)
      }
    } catch (err) {
      console.error('Failed to load active session:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async () => {
    if (!user) return

    try {
      setLoading(true)
      setError(null)
      const newSession = await startFocusSession(user.id)
      setSession(newSession)
      setRemainingSeconds(newSession.remaining_seconds)
    } catch (err: any) {
      setError(err.message || 'Failed to start session')
    } finally {
      setLoading(false)
    }
  }

  const handlePause = async () => {
    if (!session || !user) return

    try {
      setLoading(true)
      const updated = await pauseSession(session.session_id, user.id)
      setSession(updated)
      setRemainingSeconds(updated.remaining_seconds)
    } catch (err: any) {
      setError(err.message || 'Failed to pause session')
    } finally {
      setLoading(false)
    }
  }

  const handleResume = async () => {
    if (!session || !user) return

    try {
      setLoading(true)
      const updated = await resumeSession(session.session_id, user.id)
      setSession(updated)
      setRemainingSeconds(updated.remaining_seconds)
    } catch (err: any) {
      setError(err.message || 'Failed to resume session')
    } finally {
      setLoading(false)
    }
  }

  const handleComplete = async () => {
    if (!session || !user) return

    try {
      setLoading(true)
      await completeSession(session.session_id, user.id, notes)
      setSession(null)
      setRemainingSeconds(0)
      setNotes('')
      setShowNotesInput(false)

      // Show success message
      alert('Focus session completed! Great work!')
    } catch (err: any) {
      setError(err.message || 'Failed to complete session')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    if (!session || !user) return
    if (!confirm('Are you sure you want to cancel this focus session?')) return

    try {
      setLoading(true)
      await cancelSession(session.session_id, user.id)
      setSession(null)
      setRemainingSeconds(0)
      setNotes('')
      setShowNotesInput(false)
    } catch (err: any) {
      setError(err.message || 'Failed to cancel session')
    } finally {
      setLoading(false)
    }
  }

  const playNotification = () => {
    // Play browser notification sound
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Focus Session Complete!', {
        body: 'Great work! Time for a break.',
        icon: '/favicon.ico',
      })
    }
    // Play sound (you can add an audio file)
    const audio = new Audio('/notification.mp3')
    audio.play().catch(() => {
      // Silently fail if audio doesn't exist
    })
  }

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }, [])

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getProgress = (): number => {
    if (!session) return 0
    const totalSeconds = session.duration_minutes * 60
    return ((totalSeconds - remainingSeconds) / totalSeconds) * 100
  }

  if (loading && !session) {
    return (
      <div className="glass-card p-6">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="animate-spin text-zinc-400" size={32} />
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card p-6">
      <div className="flex items-center gap-2 mb-6">
        <Clock size={24} className="text-[#F0FF3D]" />
        <h2 className="text-xl font-bold text-white">Focus Mode</h2>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {!session ? (
        // No active session - show start button
        <div className="text-center py-8">
          <div className="w-48 h-48 mx-auto mb-6 rounded-full bg-[var(--bg-input)] flex items-center justify-center">
            <Clock size={64} className="text-zinc-600" />
          </div>
          <p className="text-zinc-400 mb-6">Start a 25-minute Pomodoro focus session</p>
          <button onClick={handleStart} disabled={loading} className="btn-primary flex items-center gap-2 mx-auto">
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                Starting...
              </>
            ) : (
              <>
                <Play size={18} />
                Start Focus Session
              </>
            )}
          </button>
        </div>
      ) : (
        // Active session - show timer
        <div className="text-center">
          {/* Circular Progress Timer */}
          <div className="relative w-64 h-64 mx-auto mb-6">
            {/* Background circle */}
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="128"
                cy="128"
                r="120"
                stroke="var(--bg-input)"
                strokeWidth="8"
                fill="none"
              />
              {/* Progress circle */}
              <circle
                cx="128"
                cy="128"
                r="120"
                stroke="url(#gradient)"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 120}`}
                strokeDashoffset={`${2 * Math.PI * 120 * (1 - getProgress() / 100)}`}
                strokeLinecap="round"
                className="transition-all duration-1000"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3B82F6" />
                  <stop offset="100%" stopColor="#F0FF3D" />
                </linearGradient>
              </defs>
            </svg>

            {/* Time display */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className="text-5xl font-bold text-white mb-2">
                {formatTime(remainingSeconds)}
              </div>
              <div className="text-sm text-zinc-400">
                {session.status === 'paused' ? 'Paused' : 'Focus Time'}
              </div>
              {session.interruptions > 0 && (
                <div className="text-xs text-orange-400 mt-2">
                  {session.interruptions} interruption{session.interruptions > 1 ? 's' : ''}
                </div>
              )}
            </div>
          </div>

          {/* Control buttons */}
          <div className="flex items-center justify-center gap-3 mb-6">
            {session.status === 'active' ? (
              <button
                onClick={handlePause}
                disabled={loading}
                className="btn-secondary flex items-center gap-2"
              >
                <Pause size={18} />
                Pause
              </button>
            ) : (
              <button
                onClick={handleResume}
                disabled={loading}
                className="btn-secondary flex items-center gap-2"
              >
                <Play size={18} />
                Resume
              </button>
            )}

            <button
              onClick={() => setShowNotesInput(!showNotesInput)}
              disabled={loading}
              className="btn-primary flex items-center gap-2"
            >
              <Check size={18} />
              Complete
            </button>

            <button
              onClick={handleCancel}
              disabled={loading}
              className="btn-secondary flex items-center gap-2 border-red-500/20 hover:border-red-500/40"
            >
              <X size={18} />
              Cancel
            </button>
          </div>

          {/* Notes input for completion */}
          {showNotesInput && (
            <div className="mt-6 p-4 bg-[var(--bg-input)] rounded-xl">
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Session Notes (optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="What did you accomplish?"
                className="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-[#F0FF3D]/20"
                rows={3}
              />
              <div className="flex gap-2 mt-3">
                <button
                  onClick={handleComplete}
                  disabled={loading}
                  className="btn-primary flex-1"
                >
                  {loading ? (
                    <Loader2 className="animate-spin mx-auto" size={18} />
                  ) : (
                    'Confirm Complete'
                  )}
                </button>
                <button
                  onClick={() => setShowNotesInput(false)}
                  className="btn-secondary"
                >
                  Back
                </button>
              </div>
            </div>
          )}

          {/* Session info */}
          <div className="mt-6 pt-6 border-t border-[var(--border-color)]">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="text-center">
                <div className="text-zinc-400 mb-1">Duration</div>
                <div className="text-white font-semibold">{session.duration_minutes} min</div>
              </div>
              <div className="text-center">
                <div className="text-zinc-400 mb-1">Type</div>
                <div className="text-white font-semibold capitalize">{session.session_type}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
