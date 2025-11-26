import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { ArrowLeft, Save, X, Loader2, Check, AlertCircle, Zap } from 'lucide-react'
import MarkdownEditor from '../components/editor/MarkdownEditor'
import { getVaultFile, updateVaultFile, searchVault, VaultFile } from '../services/api'

type SaveState = 'idle' | 'saving' | 'saved' | 'error'

export default function MarkdownEditorPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const filePath = searchParams.get('path')

  const [file, setFile] = useState<VaultFile | null>(null)
  const [currentContent, setCurrentContent] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [saveError, setSaveError] = useState<string | null>(null)
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true)

  const fileName = filePath?.split('/').pop() || 'Untitled'

  useEffect(() => {
    if (!filePath) {
      setError('No file path provided')
      setIsLoading(false)
      return
    }

    loadFile()
  }, [filePath, loadFile]);

  // Handle wiki-link navigation
  useEffect(() => {
    const handleWikiLinkNavigation = async (event: CustomEvent) => {
      const { noteName } = event.detail

      // Search for the note in the vault
      try {
        const results = await searchVault(noteName)
        if (results.length > 0) {
          // Navigate to the first result
          const targetPath = results[0].path
          navigate(`/vault/editor?path=${encodeURIComponent(targetPath)}`)
        } else {
          alert(`Note "${noteName}" not found`)
        }
      } catch (err) {
        console.error('Failed to find note:', err)
        alert(`Failed to find note "${noteName}"`)
      }
    }

    window.addEventListener('navigate-to-note', handleWikiLinkNavigation as EventListener)
    return () => {
      window.removeEventListener('navigate-to-note', handleWikiLinkNavigation as EventListener)
    }
  }, [navigate])

  const loadFile = async () => {
    if (!filePath) return

    setIsLoading(true)
    setError(null)

    try {
      const fileData = await getVaultFile(filePath)
      setFile(fileData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load file')
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    if (hasUnsavedChanges) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to leave?'
      )
      if (!confirmed) return
    }
    navigate('/vault')
  }

  const handleContentChange = (markdown: string) => {
    setCurrentContent(markdown)
    if (!hasUnsavedChanges) {
      setHasUnsavedChanges(true)
    }
    if (saveState === 'saved') {
      setSaveState('idle')
    }
  }

  const handleSave = async () => {
    if (!filePath || !file) return

    setSaveState('saving')
    setSaveError(null)

    try {
      const result = await updateVaultFile(filePath, currentContent, file.sha)

      // Update file with new SHA
      setFile({
        ...file,
        content: currentContent,
        sha: result.sha
      })

      setHasUnsavedChanges(false)
      setSaveState('saved')

      // Reset saved state after 2 seconds
      setTimeout(() => {
        setSaveState('idle')
      }, 2000)
    } catch (err) {
      setSaveState('error')
      setSaveError(err instanceof Error ? err.message : 'Failed to save file')
    }
  }

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 size={32} className="animate-spin text-[#F0FF3D]" />
      </div>
    )
  }

  if (error || !file) {
    return (
      <div className="h-full flex flex-col items-center justify-center">
        <div className="text-center">
          <X size={48} className="mx-auto text-red-400 mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Failed to load file</h2>
          <p className="text-zinc-400 mb-4">{error || 'File not found'}</p>
          <button
            onClick={() => navigate('/vault')}
            className="px-4 py-2 bg-[var(--bg-input)] hover:bg-[var(--bg-input)]/80 text-white rounded-lg transition-colors"
          >
            Back to Vault
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-3">
          <button
            onClick={handleClose}
            className="p-1.5 rounded-lg hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-white font-medium">{fileName}</h1>
            <p className="text-xs text-zinc-500">{filePath}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Auto-save toggle */}
          <button
            onClick={() => setAutoSaveEnabled(!autoSaveEnabled)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${autoSaveEnabled
              ? 'bg-[#F0FF3D]/20 text-[#F0FF3D]'
              : 'bg-[var(--bg-input)] text-zinc-400 hover:text-white'
              }`}
            title={autoSaveEnabled ? 'Auto-save enabled' : 'Auto-save disabled'}
          >
            <Zap size={16} />
            {autoSaveEnabled ? 'Auto-save' : 'Manual'}
          </button>

          {/* Save state indicator */}
          {saveState === 'saving' && (
            <span className="flex items-center gap-2 text-sm text-zinc-400">
              <Loader2 size={16} className="animate-spin" />
              Saving...
            </span>
          )}
          {saveState === 'saved' && (
            <span className="flex items-center gap-2 text-sm text-green-400">
              <Check size={16} />
              Saved
            </span>
          )}
          {saveState === 'error' && (
            <span className="flex items-center gap-2 text-sm text-red-400">
              <AlertCircle size={16} />
              {saveError || 'Save failed'}
            </span>
          )}
          {saveState === 'idle' && hasUnsavedChanges && !autoSaveEnabled && (
            <span className="text-sm text-zinc-400">Unsaved changes</span>
          )}

          {/* Manual save button - only show when auto-save is disabled */}
          {!autoSaveEnabled && (
            <button
              onClick={handleSave}
              disabled={!hasUnsavedChanges || saveState === 'saving'}
              className="flex items-center gap-2 px-4 py-2 bg-[#F0FF3D] hover:bg-[#F0FF3D]/90 text-black rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saveState === 'saving' ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Saving
                </>
              ) : (
                <>
                  <Save size={18} />
                  Save
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <MarkdownEditor
          initialContent={file.content}
          onChange={handleContentChange}
          onSave={handleSave}
          autoSave={autoSaveEnabled}
          autoSaveDelayMs={2000}
        />
      </div>
    </div>
  )
}
