import { Outlet, Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  HelpCircle,
  User,
  Bell,
  Settings,
  Home,
  BookOpen,
  Folder,
  LogOut,
} from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import { useNavigate } from 'react-router-dom'

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { logout } = useAuthStore()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const sidebarItems = [
    { path: '/', icon: Home, label: 'Chat' },
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/learn', icon: BookOpen, label: 'English' },
    { path: '/vault', icon: Folder, label: 'Vault' },
  ]

  const bottomItems = [
    { path: '/settings', icon: Settings, label: 'Settings' },
    { path: '/help', icon: HelpCircle, label: 'Help' },
  ]

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname.startsWith(path)
  }

  return (
    <div className="h-screen flex overflow-hidden">
      {/* Left Sidebar Navigation */}
      <aside className="sidebar-nav w-[72px] flex flex-col items-center py-4 z-20">
        {/* Logo */}
        <div className="mb-6">
          <div className="w-11 h-11 rounded-xl avatar-gradient flex items-center justify-center glow-primary">
            <span className="text-white font-bold text-lg">D</span>
          </div>
        </div>

        {/* Main navigation */}
        <nav className="flex-1 flex flex-col items-center gap-2">
          {sidebarItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`sidebar-nav-item ${isActive(item.path) ? 'active' : ''}`}
                title={item.label}
              >
                <Icon size={22} />
              </Link>
            )
          })}
        </nav>

        {/* Bottom navigation */}
        <div className="flex flex-col items-center gap-2 mt-auto">
          {bottomItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`sidebar-nav-item ${isActive(item.path) ? 'active' : ''}`}
                title={item.label}
              >
                <Icon size={22} />
              </Link>
            )
          })}
          
          <button
            onClick={handleLogout}
            className="sidebar-nav-item"
            title="Logout"
          >
            <LogOut size={22} />
          </button>

          {/* User avatar */}
          <div className="mt-4 relative group">
            <div className="w-10 h-10 rounded-xl avatar-gradient flex items-center justify-center cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-[0_0_20px_rgba(240,255,61,0.4)]">
              <User size={18} className="text-[#0a0a0f]" />
            </div>
            <span className="absolute bottom-0 right-0 w-3 h-3 notification-dot rounded-full border-2 border-[#0f0f16]"></span>
          </div>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="glass px-6 py-3 flex items-center justify-between z-10">
          <div className="flex items-center gap-6">
            {/* Navigation pills */}
            <nav className="flex items-center gap-1 bg-[rgba(20,20,32,0.6)] rounded-full p-1">
              <Link
                to="/"
                className={`nav-pill ${location.pathname === '/' ? 'active' : ''}`}
              >
                AI Chat
              </Link>
              <Link
                to="/learn"
                className={`nav-pill ${location.pathname === '/learn' ? 'active' : ''}`}
              >
                English
              </Link>
              <Link
                to="/vault"
                className={`nav-pill ${location.pathname === '/vault' ? 'active' : ''}`}
              >
                Vault
              </Link>
              <Link
                to="/dashboard"
                className={`nav-pill ${location.pathname === '/dashboard' ? 'active' : ''}`}
              >
                Dashboard
              </Link>
            </nav>
          </div>

          {/* Right side icons */}
          <div className="flex items-center gap-3">
            <button className="p-2.5 rounded-xl hover:bg-[#F0FF3D]/5 transition-all duration-200 text-gray-400 hover:text-[#F0FF3D] relative">
              <Bell size={20} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 notification-dot rounded-full"></span>
            </button>
            <button className="p-2.5 rounded-xl hover:bg-[#F0FF3D]/5 transition-all duration-200 text-gray-400 hover:text-[#F0FF3D]">
              <Settings size={20} />
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
