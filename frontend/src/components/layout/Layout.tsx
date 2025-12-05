import { Outlet, Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  HelpCircle,
  User,
  Settings,
  Home,
  BookOpen,
  LogOut,
  Database,
  Menu,
  X,
} from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import { useNavigate } from 'react-router-dom'
import NotificationBell from '../notifications/NotificationBell'
import { useState } from 'react'

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { logout } = useAuthStore()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const sidebarItems = [
    { path: '/', icon: Home, label: 'Chat' },
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/learn', icon: BookOpen, label: 'English' },
    { path: '/knowledge', icon: Database, label: 'Knowledge Base' },
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
      {/* Left Sidebar Navigation - Hidden on mobile, shown on desktop */}
      <aside className="sidebar-nav w-[72px] hidden md:flex flex-col items-center py-4 z-20">
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

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setIsMobileMenuOpen(false)}
          />

          {/* Menu */}
          <div className="absolute left-0 top-0 bottom-0 w-64 sidebar-nav flex flex-col p-4">
            {/* Header with close button */}
            <div className="flex items-center justify-between mb-6">
              <div className="w-11 h-11 rounded-xl avatar-gradient flex items-center justify-center glow-primary">
                <span className="text-white font-bold text-lg">D</span>
              </div>
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="p-2 text-zinc-400 hover:text-white"
              >
                <X size={24} />
              </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 flex flex-col gap-2">
              {sidebarItems.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                      isActive(item.path)
                        ? 'bg-[#F0FF3D]/10 text-[#F0FF3D] border border-[#F0FF3D]/30'
                        : 'text-zinc-400 hover:bg-[#F0FF3D]/5 hover:text-[#F0FF3D]'
                    }`}
                  >
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                )
              })}
            </nav>

            {/* Bottom section */}
            <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-white/[0.06]">
              {bottomItems.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl text-zinc-400 hover:bg-[#F0FF3D]/5 hover:text-[#F0FF3D] transition-all duration-200"
                  >
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                )
              })}

              <button
                onClick={handleLogout}
                className="flex items-center gap-3 px-4 py-3 rounded-xl text-zinc-400 hover:bg-red-500/10 hover:text-red-400 transition-all duration-200"
              >
                <LogOut size={20} />
                <span className="font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="glass px-3 md:px-6 py-3 flex items-center justify-between z-10">
          <div className="flex items-center gap-2 md:gap-6">
            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="md:hidden p-2 text-zinc-400 hover:text-white"
            >
              <Menu size={24} />
            </button>

            {/* Navigation pills - Responsive */}
            <nav className="flex items-center gap-1 bg-[rgba(20,20,32,0.6)] rounded-full p-1 overflow-x-auto hide-scrollbar">
              <Link
                to="/"
                className={`nav-pill whitespace-nowrap ${location.pathname === '/' ? 'active' : ''}`}
              >
                <span className="hidden sm:inline">AI Chat</span>
                <span className="sm:hidden">Chat</span>
              </Link>
              <Link
                to="/learn"
                className={`nav-pill whitespace-nowrap ${location.pathname === '/learn' ? 'active' : ''}`}
              >
                <span className="hidden sm:inline">English</span>
                <span className="sm:hidden">Learn</span>
              </Link>
              <Link
                to="/dashboard"
                className={`nav-pill whitespace-nowrap hidden lg:block ${location.pathname === '/dashboard' ? 'active' : ''}`}
              >
                Dashboard
              </Link>
              <Link
                to="/knowledge"
                className={`nav-pill whitespace-nowrap hidden xl:block ${location.pathname === '/knowledge' ? 'active' : ''}`}
              >
                Knowledge
              </Link>
            </nav>
          </div>

          {/* Right side icons */}
          <div className="flex items-center gap-2 md:gap-3">
            <NotificationBell />
            <button className="p-2 md:p-2.5 rounded-xl hover:bg-[#F0FF3D]/5 transition-all duration-200 text-gray-400 hover:text-[#F0FF3D]">
              <Settings size={18} className="md:w-5 md:h-5" />
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
