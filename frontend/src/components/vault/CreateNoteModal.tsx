import { useState, useEffect } from 'react'
import { X, FileText, FilePlus } from 'lucide-react'
import { listVaultDirectory, getVaultFile, createVaultFile, VaultItem } from '../../services/api'

interface CreateNoteModalProps {
  isOpen: boolean
  onClose: () => void
  onNoteCreated: (path: string) => void
  initialPath?: string
}

const TEMPLATES_PATH = 'Extras/Templates'

export default function CreateNoteModal({
  isOpen,
  onClose,
  onNoteCreated,
  initialPath = '',
}: CreateNoteModalProps) {
  const [noteName, setNoteName] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [templates, setTemplates] = useState<VaultItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      loadTemplates()
      setNoteName('')
      setSelectedTemplate(null)
      setError(null)
    }
  }, [isOpen])

  const loadTemplates = async () => {
    setIsLoading(true)
    try {
      const items = await listVaultDirectory(TEMPLATES_PATH)
      setTemplates(items.filter(item => item.type === 'file'))
    } catch (err) {
      console.error('Failed to load templates:', err)
      setTemplates([])
    } finally {
      setIsLoading(false)
    }
  }

  const getTemplateDisplayName = (name: string): string => {
    // Remove "Template, " prefix and ".md" suffix
    return name.replace(/^Template,\s*/, '').replace(/\.md$/, '')
  }

  const handleCreate = async () => {
    if (!noteName.trim()) {
      setError('Please enter a note name')
      return
    }

    setIsCreating(true)
    setError(null)

    try {
      let content = ''

      // Load template content if selected
      if (selectedTemplate) {
        const templateFile = await getVaultFile(selectedTemplate)
        content = templateFile.content

        // Replace {{title}} or {{name}} placeholders with note name
        content = content
          .replace(/\{\{title\}\}/g, noteName)
          .replace(/\{\{name\}\}/g, noteName)
          .replace(/\{\{date\}\}/g, new Date().toISOString().split('T')[0])
      }

      // Determine the path based on template type
      let notePath = ''
      const templateName = selectedTemplate ? templates.find(t => t.path === selectedTemplate)?.name || '' : ''

      if (templateName.includes('People')) {
        notePath = `Extras/People/${noteName}.md`
      } else if (templateName.includes('Daily log')) {
        const today = new Date().toISOString().split('T')[0]
        notePath = `Daily/${today}.md`
      } else if (templateName.includes('Meeting')) {
        notePath = `Timestamps/Meetings/${noteName}.md`
      } else if (templateName.includes('English')) {
        notePath = `Resource/English/${noteName}.md`
      } else {
        // Default to current path or root
        notePath = initialPath ? `${initialPath}/${noteName}.md` : `${noteName}.md`
      }

      await createVaultFile(notePath, content)
      onNoteCreated(notePath)
      onClose()
    } catch (err: unknown) {
      console.error('Failed to create note:', err)
      setError(err.message || 'Failed to create note')
    } finally {
      setIsCreating(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <FilePlus size={20} className="text-[#F0FF3D]" />
            Create New Note
          </h3>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          {/* Note name */}
          <div>
            <label className="block text-sm text-zinc-400 mb-2">Note Name</label>
            <input
              type="text"
              value={noteName}
              onChange={(e) => setNoteName(e.target.value)}
              placeholder="My new note"
              className="w-full px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#F0FF3D]"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleCreate()
                }
              }}
            />
          </div>

          {/* Template selection */}
          <div>
            <label className="block text-sm text-zinc-400 mb-2">
              Template (optional)
            </label>
            {isLoading ? (
              <div className="text-sm text-zinc-500">Loading templates...</div>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setSelectedTemplate(null)}
                  className={`px-3 py-2 rounded-lg text-sm text-left transition-colors ${selectedTemplate === null
                      ? 'bg-[#F0FF3D] text-black font-medium'
                      : 'bg-[var(--bg-input)] text-white hover:bg-[var(--bg-input)]/80'
                    }`}
                >
                  <div className="flex items-center gap-2">
                    <FileText size={14} />
                    Blank Note
                  </div>
                </button>
                {templates.map((template) => (
                  <button
                    key={template.path}
                    onClick={() => setSelectedTemplate(template.path)}
                    className={`px-3 py-2 rounded-lg text-sm text-left transition-colors ${selectedTemplate === template.path
                        ? 'bg-[#F0FF3D] text-black font-medium'
                        : 'bg-[var(--bg-input)] text-white hover:bg-[var(--bg-input)]/80'
                      }`}
                  >
                    <div className="flex items-center gap-2">
                      <FileText size={14} />
                      <span className="truncate">
                        {getTemplateDisplayName(template.name)}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {error && (
            <div className="px-3 py-2 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-[var(--bg-input)] hover:bg-[var(--bg-input)]/80 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={isCreating || !noteName.trim()}
              className="px-4 py-2 bg-[#F0FF3D] hover:bg-[#F0FF3D]/90 text-black rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isCreating ? (
                <>Creating...</>
              ) : (
                <>
                  <FilePlus size={18} />
                  Create Note
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
