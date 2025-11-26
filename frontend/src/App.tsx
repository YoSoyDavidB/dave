import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Chat from './pages/Chat'
import Dashboard from './pages/Dashboard'
import EnglishProgress from './pages/EnglishProgress'
import VaultBrowser from './pages/VaultBrowser'
import KnowledgeBase from './pages/KnowledgeBase'
import MarkdownEditorPage from './pages/MarkdownEditorPage'
import LoginPage from './pages/LoginPage'
import ProtectedRoute from './components/auth/ProtectedRoute'
import { useEffect } from 'react'
import { useAuthStore } from './stores/authStore'

function App() {
  const { checkAuthStatus } = useAuthStore()

  useEffect(() => {
    checkAuthStatus()
  }, [checkAuthStatus])

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Layout />}>
          <Route index element={<Chat />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="learn" element={<EnglishProgress />} />
          <Route path="vault" element={<VaultBrowser />} />
          <Route path="vault/editor" element={<MarkdownEditorPage />} />
          <Route path="knowledge" element={<KnowledgeBase />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
