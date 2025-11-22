import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Chat from './pages/Chat'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Chat />} />
        <Route path="dashboard" element={<Dashboard />} />
      </Route>
    </Routes>
  )
}

export default App
