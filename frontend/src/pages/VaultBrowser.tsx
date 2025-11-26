import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Folder,
  FileText,
  ChevronRight,
  Search,
  Home,
  Loader2,
  RefreshCw,
  Calendar,
  X,
  Edit3,
  Plus,
} from 'lucide-react'
import {
  listVaultDirectory,
  getVaultFile,
  searchVault,
  getDailyNote,
  VaultItem,
  VaultFile,
} from '../services/api'
import MarkdownMessage from '../components/chat/MarkdownMessage'
import CreateNoteModal from '../components/vault/CreateNoteModal'

function BreadcrumbNav({
  path,
  onNavigate,
}: {
  path: string
  onNavigate: (path: string) => void
}) {
  const parts = path ? path.split('/') : []

  return (
    <div className="flex items-center gap-1 text-sm overflow-x-auto">
      <button
        onClick={() => onNavigate('')}
        className="p-1.5 rounded-lg hover:bg-[#F0FF3D]/10 text-zinc-400 hover:text-[#F0FF3D] transition-colors"
      >
        <Home size={16} />
      </button>
      {parts.map((part, index) => {
        const fullPath = parts.slice(0, index + 1).join('/')
        return (
          <div key={fullPath} className="flex items-center">
            <ChevronRight size={14} className="text-zinc-600 mx-1" />
            <button
              onClick={() => onNavigate(fullPath)}
              className="px-2 py-1 rounded-lg hover:bg-[#F0FF3D]/10 text-zinc-400 hover:text-white transition-colors truncate max-w-[150px]"
            >
              {part}
            </button>
          </div>
        )
      })}
    </div>
  )
}

function FileItem({
  item,
  onSelect,
  isSelected,
}: {
  item: VaultItem
  onSelect: (item: VaultItem) => void
  isSelected: boolean
}) {
  const isFolder = item.type === 'dir'

  return (
    <button
      onClick={() => onSelect(item)}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-left ${
        isSelected
          ? 'bg-[#F0FF3D]/10 border border-[#F0FF3D]/30'
          : 'hover:bg-[var(--bg-input)] border border-transparent'
      }`}
    >
      {isFolder ? (
        <Folder size={18} className="text-[#F0FF3D] flex-shrink-0" />
      ) : (
        <FileText size={18} className="text-zinc-400 flex-shrink-0" />
      )}
      <span className={`truncate ${isSelected ? 'text-white' : 'text-zinc-300'}`}>
        {item.name}
      </span>
      {isFolder && <ChevronRight size={16} className="text-zinc-600 ml-auto" />}
    </button>
  )
}

function FileViewer({
  file,
  onClose,
}: {
  file: VaultFile
  onClose: () => void
}) {
  const navigate = useNavigate()
  const fileName = file.path.split('/').pop() || 'Untitled'

  const handleEdit = () => {
    navigate(`/vault/editor?path=${encodeURIComponent(file.path)}`)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-2">
          <FileText size={18} className="text-[#F0FF3D]" />
          <span className="text-white font-medium truncate">{fileName}</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleEdit}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#F0FF3D]/10 hover:bg-[#F0FF3D]/20 text-[#F0FF3D] transition-colors text-sm font-medium"
          >
            <Edit3 size={16} />
            Edit
          </button>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="prose-invert prose-sm max-w-none">
          <MarkdownMessage content={file.content} />
        </div>
      </div>
    </div>
  )
}

function SearchResults({
  results,
  onSelect,
  query,
}: {
  results: VaultItem[]
  onSelect: (item: VaultItem) => void
  query: string
}) {
  if (results.length === 0) {
    return (
      <div className="text-center py-8">
        <Search size={32} className="mx-auto text-zinc-600 mb-3" />
        <p className="text-zinc-400">No results found for "{query}"</p>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      <p className="text-zinc-500 text-sm mb-3">
        {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
      </p>
      {results.map((item) => (
        <button
          key={item.path}
          onClick={() => onSelect(item)}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-[var(--bg-input)] transition-colors text-left"
        >
          <FileText size={18} className="text-zinc-400 flex-shrink-0" />
          <div className="min-w-0">
            <p className="text-white truncate">{item.name}</p>
            <p className="text-zinc-500 text-xs truncate">{item.path}</p>
          </div>
        </button>
      ))}
    </div>
  )
}

export default function VaultBrowser() {
  const navigate = useNavigate()
  const [currentPath, setCurrentPath] = useState('')
  const [items, setItems] = useState<VaultItem[]>([])
  const [selectedFile, setSelectedFile] = useState<VaultFile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingFile, setIsLoadingFile] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<VaultItem[] | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)

  const loadDirectory = useCallback(async (path: string) => {
    setIsLoading(true)
    setError(null)
    setSearchResults(null)
    setSearchQuery('')
    try {
      const data = await listVaultDirectory(path)
      // Sort: folders first, then files, alphabetically
      const sorted = [...data].sort((a, b) => {
        if (a.type !== b.type) return a.type === 'dir' ? -1 : 1
        return a.name.localeCompare(b.name)
      })
      setItems(sorted)
      setCurrentPath(path)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load directory')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const loadFile = async (path: string) => {
    setIsLoadingFile(true)
    try {
      const file = await getVaultFile(path)
      setSelectedFile(file)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load file')
    } finally {
      setIsLoadingFile(false)
    }
  }

  const loadDailyNote = async () => {
    setIsLoadingFile(true)
    try {
      const file = await getDailyNote()
      setSelectedFile(file)
    } catch (err) {
      if (err instanceof Error && err.message.includes('not found')) {
        setError("Today's daily note doesn't exist yet")
      } else {
        setError(err instanceof Error ? err.message : 'Failed to load daily note')
      }
    } finally {
      setIsLoadingFile(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults(null)
      return
    }
    setIsSearching(true)
    try {
      const results = await searchVault(searchQuery)
      setSearchResults(results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setIsSearching(false)
    }
  }

  const handleItemSelect = (item: VaultItem) => {
    if (item.type === 'dir') {
      loadDirectory(item.path)
      setSelectedFile(null)
    } else {
      loadFile(item.path)
    }
  }

  useEffect(() => {
    loadDirectory('')
  }, [loadDirectory])

  return (
    <div className="h-full flex">
      {/* Sidebar - File browser */}
      <div className="w-80 border-r border-[var(--border-color)] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-[var(--border-color)]">
          <h1 className="text-lg font-semibold text-white mb-3">Obsidian Vault</h1>

          {/* Search */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search notes..."
              className="w-full pl-10 pr-4 py-2.5 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-[#F0FF3D]/40 transition-all duration-200 text-sm"
            />
            <Search
              size={16}
              className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500"
            />
            {isSearching && (
              <Loader2
                size={16}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#F0FF3D] animate-spin"
              />
            )}
          </div>

          {/* Quick actions */}
          <div className="flex gap-2 mt-3">
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-[#F0FF3D]/10 text-[#F0FF3D] hover:bg-[#F0FF3D]/20 transition-colors text-sm font-medium"
            >
              <Plus size={14} />
              New Note
            </button>
            <button
              onClick={loadDailyNote}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-[var(--bg-input)] text-zinc-400 hover:text-[#F0FF3D] hover:bg-[#F0FF3D]/10 transition-colors text-sm"
            >
              <Calendar size={14} />
              Today
            </button>
            <button
              onClick={() => loadDirectory(currentPath)}
              className="p-2 rounded-xl bg-[var(--bg-input)] text-zinc-400 hover:text-[#F0FF3D] hover:bg-[#F0FF3D]/10 transition-colors"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        </div>

        {/* Breadcrumb */}
        {!searchResults && (
          <div className="px-4 py-2 border-b border-[var(--border-color)]">
            <BreadcrumbNav path={currentPath} onNavigate={loadDirectory} />
          </div>
        )}

        {/* File list */}
        <div className="flex-1 overflow-y-auto p-2">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 size={24} className="animate-spin text-[#F0FF3D]" />
            </div>
          ) : searchResults ? (
            <SearchResults
              results={searchResults}
              onSelect={handleItemSelect}
              query={searchQuery}
            />
          ) : items.length === 0 ? (
            <div className="text-center py-8">
              <Folder size={32} className="mx-auto text-zinc-600 mb-3" />
              <p className="text-zinc-400">Empty folder</p>
            </div>
          ) : (
            <div className="space-y-1">
              {items.map((item) => (
                <FileItem
                  key={item.path}
                  item={item}
                  onSelect={handleItemSelect}
                  isSelected={selectedFile?.path === item.path}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main content - File viewer */}
      <div className="flex-1 flex flex-col">
        {error && (
          <div className="m-4 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
              <X size={16} />
            </button>
          </div>
        )}

        {isLoadingFile ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 size={32} className="animate-spin text-[#F0FF3D]" />
          </div>
        ) : selectedFile ? (
          <FileViewer file={selectedFile} onClose={() => setSelectedFile(null)} />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
            <div className="w-20 h-20 rounded-2xl bg-[var(--bg-input)] flex items-center justify-center mb-4">
              <FileText size={32} className="text-zinc-600" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Select a note</h2>
            <p className="text-zinc-500 max-w-sm">
              Browse your Obsidian vault and click on a note to view its contents
            </p>
          </div>
        )}
      </div>

      {/* Create Note Modal */}
      <CreateNoteModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onNoteCreated={(path) => {
          setShowCreateModal(false)
          // Navigate to the newly created note in the editor
          navigate(`/vault/editor?path=${encodeURIComponent(path)}`)
        }}
        initialPath={currentPath}
      />
    </div>
  )
}
