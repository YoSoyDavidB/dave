import { useState, useEffect, useRef } from 'react'
import {
  getRAGIndexStats,
  triggerFullIndex,
  triggerIncrementalIndex,
  searchRAG,
  getUserMemories,
  deleteMemory,
  listDocuments,
  uploadDocument,
  deleteDocument,
  getDocumentStats,
  RAGIndexStats,
  RAGSearchResult,
  Memory,
  UploadedDocument,
  DocumentCategory,
  DocumentStatsResponse,
} from '../services/api'
import { useAuthStore } from '../stores/authStore'
import {
  Trash2,
  Brain,
  Search,
  RefreshCw,
  Upload,
  File,
  X,
  Tag,
  FolderOpen,
  Plus,
  Loader2,
  Database,
} from 'lucide-react'

const CATEGORIES: { value: DocumentCategory; label: string }[] = [
  { value: 'manual', label: 'Manual' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'contract', label: 'Contract' },
  { value: 'receipt', label: 'Receipt' },
  { value: 'note', label: 'Note' },
  { value: 'report', label: 'Report' },
  { value: 'guide', label: 'Guide' },
  { value: 'reference', label: 'Reference' },
  { value: 'personal', label: 'Personal' },
  { value: 'work', label: 'Work' },
  { value: 'other', label: 'Other' },
]

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function KnowledgeBase() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState<'vault' | 'documents' | 'memories'>('documents')
  const [stats, setStats] = useState<RAGIndexStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [indexing, setIndexing] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<RAGSearchResult[]>([])
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Memory state
  const [memories, setMemories] = useState<Memory[]>([])
  const [loadingMemories, setLoadingMemories] = useState(false)
  const [memoryFilter, setMemoryFilter] = useState<string>('')

  // Document state
  const [documents, setDocuments] = useState<UploadedDocument[]>([])
  const [loadingDocuments, setLoadingDocuments] = useState(false)
  const [documentStats, setDocumentStats] = useState<DocumentStatsResponse | null>(null)
  const [categoryFilter, setCategoryFilter] = useState<DocumentCategory | ''>('')
  const [showUploadModal, setShowUploadModal] = useState(false)

  // Upload state
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadCategory, setUploadCategory] = useState<DocumentCategory>('other')
  const [uploadTags, setUploadTags] = useState<string>('')
  const [uploadDescription, setUploadDescription] = useState('')
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (activeTab === 'vault') {
      loadStats()
    }
  }, [activeTab])

  useEffect(() => {
    if (activeTab === 'memories' && user?.id) {
      loadMemories()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, user?.id])

  useEffect(() => {
    if (activeTab === 'documents' && user?.id) {
      loadDocuments()
      loadDocumentStats()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, user?.id, categoryFilter])

  const loadDocuments = async () => {
    if (!user?.id) return
    try {
      setLoadingDocuments(true)
      const response = await listDocuments(user.id, {
        category: categoryFilter || undefined,
        limit: 100,
      })
      setDocuments(response.documents)
    } catch (err) {
      console.error('Failed to load documents:', err)
      setError('Failed to load documents')
    } finally {
      setLoadingDocuments(false)
    }
  }

  const loadDocumentStats = async () => {
    if (!user?.id) return
    try {
      const stats = await getDocumentStats(user.id)
      setDocumentStats(stats)
    } catch (err) {
      console.error('Failed to load document stats:', err)
    }
  }

  const handleUpload = async () => {
    if (!user?.id || !uploadFile) return

    try {
      setUploading(true)
      setError(null)
      const tags = uploadTags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)

      await uploadDocument(uploadFile, user.id, uploadCategory, tags, uploadDescription)

      setSuccessMessage('Document uploaded successfully')
      setTimeout(() => setSuccessMessage(null), 3000)

      // Reset upload form
      setUploadFile(null)
      setUploadCategory('other')
      setUploadTags('')
      setUploadDescription('')
      setShowUploadModal(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      // Refresh document list
      loadDocuments()
      loadDocumentStats()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteDocument = async (documentId: string, filename: string) => {
    if (!user?.id || !confirm(`Are you sure you want to delete "${filename}"?`)) return
    try {
      await deleteDocument(user.id, documentId)
      setDocuments(documents.filter((d) => d.id !== documentId))
      loadDocumentStats()
      setSuccessMessage('Document deleted')
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError('Failed to delete document')
      console.error(err)
    }
  }

  const loadMemories = async () => {
    if (!user?.id) return
    try {
      setLoadingMemories(true)
      const response = await getUserMemories(user.id, {
        memoryType: memoryFilter || undefined,
        limit: 100,
      })
      setMemories(response.memories)
    } catch (err) {
      console.error('Failed to load memories:', err)
    } finally {
      setLoadingMemories(false)
    }
  }

  const handleDeleteMemory = async (memoryId: string) => {
    if (!user?.id || !confirm('Are you sure you want to delete this memory?')) return
    try {
      await deleteMemory(user.id, memoryId)
      setMemories(memories.filter((m) => m.id !== memoryId))
      setSuccessMessage('Memory deleted')
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError('Failed to delete memory')
      console.error(err)
    }
  }

  const loadStats = async () => {
    try {
      setLoading(true)
      const data = await getRAGIndexStats()
      setStats(data)
      setError(null)
    } catch (err) {
      setError('Failed to load index statistics')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleFullIndex = async () => {
    try {
      setIndexing(true)
      setError(null)
      await triggerFullIndex()
      setSuccessMessage('Full indexing started in background')
      setTimeout(() => setSuccessMessage(null), 5000)
      setTimeout(loadStats, 3000)
    } catch (err) {
      setError('Failed to start indexing')
      console.error(err)
    } finally {
      setIndexing(false)
    }
  }

  const handleIncrementalIndex = async () => {
    try {
      setIndexing(true)
      setError(null)
      await triggerIncrementalIndex()
      setSuccessMessage('Incremental indexing started in background')
      setTimeout(() => setSuccessMessage(null), 5000)
      setTimeout(loadStats, 3000)
    } catch (err) {
      setError('Failed to start incremental indexing')
      console.error(err)
    } finally {
      setIndexing(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    try {
      setSearching(true)
      setError(null)
      const response = await searchRAG(searchQuery, {
        includeDocuments: true,
        includeMemories: false,
        limit: 10,
        minScore: 0.4,
      })
      setSearchResults(response.results)
    } catch (err) {
      setError('Search failed')
      console.error(err)
    } finally {
      setSearching(false)
    }
  }

  const memoryTypeColors: Record<string, string> = {
    preference: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    fact: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    task: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    goal: 'bg-green-500/20 text-green-400 border-green-500/30',
    profile: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Knowledge Base</h1>
            <p className="text-zinc-500">Manage your documents, vault index, and memories</p>
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl">
            {error}
          </div>
        )}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 text-green-400 rounded-xl">
            {successMessage}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-8">
          <button
            onClick={() => setActiveTab('documents')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-all duration-200 ${activeTab === 'documents'
                ? 'bg-[#F0FF3D] text-[#0a0a0f]'
                : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
          >
            <Upload size={18} />
            My Documents
            <span className={`text-xs px-2 py-0.5 rounded-full ${activeTab === 'documents' ? 'bg-[#0a0a0f]/20' : 'bg-zinc-700'
              }`}>
              {documents.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('vault')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-all duration-200 ${activeTab === 'vault'
                ? 'bg-[#F0FF3D] text-[#0a0a0f]'
                : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
          >
            <Database size={18} />
            Vault Index
          </button>
          <button
            onClick={() => setActiveTab('memories')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-all duration-200 ${activeTab === 'memories'
                ? 'bg-[#F0FF3D] text-[#0a0a0f]'
                : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
          >
            <Brain size={18} />
            Memories
            <span className={`text-xs px-2 py-0.5 rounded-full ${activeTab === 'memories' ? 'bg-[#0a0a0f]/20' : 'bg-zinc-700'
              }`}>
              {memories.length}
            </span>
          </button>
        </div>

        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <div className="space-y-6">
            {/* Document Stats */}
            {documentStats && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="glass-card p-5">
                  <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Documents</div>
                  <div className="text-2xl font-bold text-white">{documentStats.total_documents}</div>
                </div>
                <div className="glass-card p-5">
                  <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Chunks</div>
                  <div className="text-2xl font-bold text-white">{documentStats.total_chunks}</div>
                </div>
                <div className="glass-card p-5">
                  <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Total Size</div>
                  <div className="text-2xl font-bold text-white">{formatFileSize(documentStats.total_size_bytes)}</div>
                </div>
                <div className="glass-card p-5">
                  <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Categories</div>
                  <div className="text-2xl font-bold text-white">{Object.keys(documentStats.by_category).length}</div>
                </div>
              </div>
            )}

            {/* Document Controls */}
            <div className="flex flex-wrap items-center gap-4">
              <button
                onClick={() => setShowUploadModal(true)}
                className="flex items-center gap-2 px-5 py-2.5 btn-gradient rounded-xl font-semibold"
              >
                <Plus size={18} />
                Upload Document
              </button>

              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value as DocumentCategory | '')}
                className="px-4 py-2.5 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white focus:outline-none focus:border-[#F0FF3D]/40 transition-all duration-200"
              >
                <option value="">All Categories</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>

              <button
                onClick={() => {
                  loadDocuments()
                  loadDocumentStats()
                }}
                disabled={loadingDocuments}
                className="p-2.5 rounded-xl hover:bg-[#F0FF3D]/5 transition-all duration-200 text-zinc-400 hover:text-[#F0FF3D]"
              >
                <RefreshCw size={20} className={loadingDocuments ? 'animate-spin' : ''} />
              </button>
            </div>

            {/* Document List */}
            <div className="glass-card overflow-hidden">
              {loadingDocuments ? (
                <div className="flex items-center justify-center py-16">
                  <Loader2 size={32} className="animate-spin text-[#F0FF3D]" />
                </div>
              ) : documents.length === 0 ? (
                <div className="text-center py-16">
                  <FolderOpen size={48} className="mx-auto text-zinc-600 mb-4" />
                  <p className="text-zinc-400">No documents found</p>
                  <p className="text-zinc-600 text-sm mt-1">
                    Upload documents to make them searchable
                  </p>
                  <button
                    onClick={() => setShowUploadModal(true)}
                    className="mt-6 px-5 py-2.5 btn-gradient rounded-xl font-semibold"
                  >
                    Upload Your First Document
                  </button>
                </div>
              ) : (
                <div className="divide-y divide-white/5">
                  {documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="p-5 hover:bg-white/[0.02] transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <File size={18} className="text-[#F0FF3D] flex-shrink-0" />
                            <span className="font-medium text-white truncate">
                              {doc.original_filename}
                            </span>
                            <span className="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-zinc-700">
                              {doc.category}
                            </span>
                          </div>
                          {doc.description && (
                            <p className="text-sm text-zinc-500 mb-2 ml-7">
                              {doc.description}
                            </p>
                          )}
                          <div className="flex flex-wrap items-center gap-3 text-xs text-zinc-500 ml-7">
                            <span>{formatFileSize(doc.file_size)}</span>
                            <span className="text-zinc-600">•</span>
                            <span>{doc.chunk_count} chunks</span>
                            <span className="text-zinc-600">•</span>
                            <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                            {doc.tags.length > 0 && (
                              <>
                                <span className="text-zinc-600">•</span>
                                <div className="flex items-center gap-1">
                                  <Tag size={12} className="text-zinc-500" />
                                  {doc.tags.map((tag) => (
                                    <span
                                      key={tag}
                                      className="px-1.5 py-0.5 bg-[#F0FF3D]/10 text-[#F0FF3D] rounded text-xs"
                                    >
                                      {tag}
                                    </span>
                                  ))}
                                </div>
                              </>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeleteDocument(doc.id, doc.original_filename)}
                          className="p-2 text-zinc-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all duration-200"
                          title="Delete document"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Upload Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="glass-card max-w-md w-full">
              <div className="flex items-center justify-between p-5 border-b border-white/5">
                <h2 className="text-lg font-semibold text-white">Upload Document</h2>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="p-1.5 text-zinc-400 hover:text-white hover:bg-white/5 rounded-lg transition-all duration-200"
                >
                  <X size={20} />
                </button>
              </div>
              <div className="p-5 space-y-5">
                {/* File Input */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    Select File
                  </label>
                  <div
                    className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${uploadFile
                        ? 'border-[#F0FF3D]/50 bg-[#F0FF3D]/5'
                        : 'border-zinc-700 hover:border-[#F0FF3D]/30 hover:bg-white/[0.02]'
                      }`}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".txt,.md,.csv,.json,.pdf"
                      className="hidden"
                      onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    />
                    {uploadFile ? (
                      <div className="flex items-center justify-center gap-2">
                        <File size={20} className="text-[#F0FF3D]" />
                        <span className="text-white">{uploadFile.name}</span>
                        <span className="text-zinc-500">({formatFileSize(uploadFile.size)})</span>
                      </div>
                    ) : (
                      <div>
                        <Upload size={28} className="mx-auto mb-3 text-zinc-500" />
                        <p className="text-zinc-400">Click to select a file</p>
                        <p className="text-xs text-zinc-600 mt-2">
                          .txt, .md, .csv, .json, .pdf (max 10MB)
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Category */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    Category
                  </label>
                  <select
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value as DocumentCategory)}
                    className="w-full px-4 py-3 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white focus:outline-none focus:border-[#F0FF3D]/40 transition-all duration-200"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Tags */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={uploadTags}
                    onChange={(e) => setUploadTags(e.target.value)}
                    placeholder="e.g., important, 2024, project-x"
                    className="w-full px-4 py-3 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-[#F0FF3D]/40 transition-all duration-200"
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">
                    Description (optional)
                  </label>
                  <textarea
                    value={uploadDescription}
                    onChange={(e) => setUploadDescription(e.target.value)}
                    placeholder="Brief description of the document..."
                    rows={2}
                    className="w-full px-4 py-3 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-[#F0FF3D]/40 transition-all duration-200 resize-none"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 p-5 border-t border-white/5">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="px-5 py-2.5 text-zinc-400 hover:text-white hover:bg-white/5 rounded-xl transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={!uploadFile || uploading}
                  className="px-5 py-2.5 btn-gradient rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? (
                    <span className="flex items-center gap-2">
                      <Loader2 size={16} className="animate-spin" />
                      Uploading...
                    </span>
                  ) : (
                    'Upload'
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Vault Tab */}
        {activeTab === 'vault' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="glass-card p-5">
                <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Documents Indexed</div>
                <div className="text-2xl font-bold text-white">
                  {loading ? '...' : stats?.stats?.documents_indexed ?? 0}
                </div>
              </div>
              <div className="glass-card p-5">
                <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Total Chunks</div>
                <div className="text-2xl font-bold text-white">
                  {loading ? '...' : stats?.stats?.total_chunks ?? 0}
                </div>
              </div>
              <div className="glass-card p-5">
                <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Avg Chunks/Doc</div>
                <div className="text-2xl font-bold text-white">
                  {loading
                    ? '...'
                    : stats?.stats?.documents_indexed
                      ? (stats.stats.total_chunks / stats.stats.documents_indexed).toFixed(1)
                      : '0'}
                </div>
              </div>
            </div>

            {/* Index Controls */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-semibold text-white mb-2">Index Management</h2>
              <p className="text-zinc-500 text-sm mb-5">
                Index your Obsidian vault for semantic search. Full index rebuilds everything,
                incremental only processes changed files.
              </p>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={handleIncrementalIndex}
                  disabled={indexing}
                  className="px-5 py-2.5 btn-gradient rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {indexing ? 'Starting...' : 'Incremental Index'}
                </button>
                <button
                  onClick={handleFullIndex}
                  disabled={indexing}
                  className="px-5 py-2.5 btn-glow-border rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {indexing ? 'Starting...' : 'Full Reindex'}
                </button>
                <button
                  onClick={loadStats}
                  disabled={loading}
                  className="p-2.5 rounded-xl hover:bg-[#F0FF3D]/5 transition-all duration-200 text-zinc-400 hover:text-[#F0FF3D]"
                >
                  <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
                </button>
              </div>
            </div>

            {/* Search Test */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Test Search</h2>
              <form onSubmit={handleSearch} className="mb-5">
                <div className="flex gap-3">
                  <div className="relative flex-1">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Search size={18} className="text-zinc-500" />
                    </div>
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search your knowledge base..."
                      className="w-full pl-11 pr-4 py-3 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-[#F0FF3D]/40 transition-all duration-200"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={searching || !searchQuery.trim()}
                    className="px-6 py-3 btn-gradient rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {searching ? (
                      <Loader2 size={18} className="animate-spin" />
                    ) : (
                      'Search'
                    )}
                  </button>
                </div>
              </form>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="space-y-3">
                  <div className="text-sm text-zinc-500">
                    Found {searchResults.length} results
                  </div>
                  {searchResults.map((result, index) => (
                    <div
                      key={index}
                      className="p-4 bg-white/[0.02] border border-white/5 rounded-xl"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-[#F0FF3D]">
                          {result.source}
                        </span>
                        <span className="text-xs px-2 py-1 bg-zinc-800 rounded text-zinc-400">
                          {(result.score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-zinc-400 text-sm line-clamp-3">
                        {result.content}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {searchResults.length === 0 && searchQuery && !searching && (
                <div className="text-center py-8">
                  <Search size={32} className="mx-auto text-zinc-600 mb-3" />
                  <p className="text-zinc-500">No results found</p>
                  <p className="text-zinc-600 text-sm mt-1">
                    Try a different query or lower the score threshold
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Memories Tab */}
        {activeTab === 'memories' && (
          <div className="space-y-6">
            {/* Memory Controls */}
            <div className="flex items-center justify-between">
              <select
                value={memoryFilter}
                onChange={(e) => {
                  setMemoryFilter(e.target.value)
                  setTimeout(loadMemories, 100)
                }}
                className="px-4 py-2.5 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-xl text-white focus:outline-none focus:border-[#F0FF3D]/40 transition-all duration-200"
              >
                <option value="">All Types</option>
                <option value="preference">Preferences</option>
                <option value="fact">Facts</option>
                <option value="task">Tasks</option>
                <option value="goal">Goals</option>
                <option value="profile">Profile</option>
              </select>
              <button
                onClick={loadMemories}
                disabled={loadingMemories}
                className="p-2.5 rounded-xl hover:bg-[#F0FF3D]/5 transition-all duration-200 text-zinc-400 hover:text-[#F0FF3D]"
              >
                <RefreshCw size={20} className={loadingMemories ? 'animate-spin' : ''} />
              </button>
            </div>

            {/* Memory List */}
            <div className="glass-card overflow-hidden">
              {loadingMemories ? (
                <div className="flex items-center justify-center py-16">
                  <Loader2 size={32} className="animate-spin text-[#F0FF3D]" />
                </div>
              ) : memories.length === 0 ? (
                <div className="text-center py-16">
                  <Brain size={48} className="mx-auto text-zinc-600 mb-4" />
                  <p className="text-zinc-400">No memories found</p>
                  <p className="text-zinc-600 text-sm mt-1">
                    Memories are extracted automatically from your conversations
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-white/5">
                  {memories.map((memory) => (
                    <div
                      key={memory.id}
                      className="p-5 hover:bg-white/[0.02] transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <span
                              className={`px-2 py-0.5 rounded-full text-xs font-medium border ${memoryTypeColors[memory.memory_type] || 'bg-zinc-800 text-zinc-400 border-zinc-700'
                                }`}
                            >
                              {memory.memory_type}
                            </span>
                            <span className="text-xs text-zinc-500">
                              {new Date(memory.timestamp).toLocaleDateString()}
                            </span>
                            <span className="text-xs text-zinc-600">
                              Referenced {memory.num_times_referenced}x
                            </span>
                          </div>
                          <p className="text-zinc-300">{memory.short_text}</p>
                          <div className="mt-2 flex items-center gap-4 text-xs text-zinc-500">
                            <span>Relevance: {(memory.relevance_score * 100).toFixed(0)}%</span>
                            <span>Source: {memory.source}</span>
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeleteMemory(memory.id)}
                          className="p-2 text-zinc-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all duration-200"
                          title="Delete memory"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
