import { Outlet, Link, useLocation } from 'react-router-dom'

export default function Layout() {
  const location = useLocation()

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🤖</span>
          <h1 className="text-xl font-bold text-gray-800">Dave</h1>
        </div>

        <nav className="flex gap-4">
          <Link
            to="/"
            className={`px-3 py-1 rounded-lg transition-colors ${
              location.pathname === '/'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Chat
          </Link>
          <Link
            to="/dashboard"
            className={`px-3 py-1 rounded-lg transition-colors ${
              location.pathname === '/dashboard'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            Dashboard
          </Link>
        </nav>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
