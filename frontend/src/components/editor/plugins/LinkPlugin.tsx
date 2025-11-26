import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useCallback, useEffect, useState } from 'react'
import {
  $getSelection,
  $isRangeSelection,
  COMMAND_PRIORITY_LOW,
  SELECTION_CHANGE_COMMAND,
} from 'lexical'
import { $isLinkNode, TOGGLE_LINK_COMMAND } from '@lexical/link'
import { getSelectedNode } from '../utils/getSelectedNode'
import { Link2, ExternalLink } from 'lucide-react'

export default function LinkPlugin() {
  const [editor] = useLexicalComposerContext()
  const [isLink, setIsLink] = useState(false)
  const [linkUrl, setLinkUrl] = useState('')
  const [showLinkEditor, setShowLinkEditor] = useState(false)
  const [linkInputValue, setLinkInputValue] = useState('')

  const updateToolbar = useCallback(() => {
    const selection = $getSelection()
    if ($isRangeSelection(selection)) {
      const node = getSelectedNode(selection)
      const parent = node.getParent()

      if ($isLinkNode(parent) || $isLinkNode(node)) {
        const linkNode = $isLinkNode(parent) ? parent : node
        setIsLink(true)
        setLinkUrl(linkNode.getURL())
      } else {
        setIsLink(false)
        setLinkUrl('')
      }
    }
  }, [])

  useEffect(() => {
    return editor.registerCommand(
      SELECTION_CHANGE_COMMAND,
      () => {
        updateToolbar()
        return false
      },
      COMMAND_PRIORITY_LOW
    )
  }, [editor, updateToolbar])

  const insertLink = useCallback(() => {
    if (!linkInputValue) {
      editor.dispatchCommand(TOGGLE_LINK_COMMAND, null)
    } else {
      editor.dispatchCommand(TOGGLE_LINK_COMMAND, linkInputValue)
    }
    setShowLinkEditor(false)
    setLinkInputValue('')
  }, [editor, linkInputValue])

  const handleOpenLinkEditor = () => {
    setLinkInputValue(linkUrl)
    setShowLinkEditor(true)
  }

  return (
    <>
      {/* Link button in toolbar */}
      <div className="flex items-center gap-1">
        <button
          onClick={handleOpenLinkEditor}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${
            isLink ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
          }`}
          aria-label="Insert Link"
          title="Insert/Edit Link (Cmd+K)"
        >
          <Link2 size={18} />
        </button>
        {isLink && linkUrl && (
          <a
            href={linkUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 rounded hover:bg-[var(--bg-input)] text-zinc-400 hover:text-[#F0FF3D] transition-colors"
            title={`Open link: ${linkUrl}`}
          >
            <ExternalLink size={16} />
          </a>
        )}
      </div>

      {/* Link editor modal */}
      {showLinkEditor && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">
              {isLink ? 'Edit Link' : 'Insert Link'}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  URL or Wiki Link
                </label>
                <input
                  type="text"
                  value={linkInputValue}
                  onChange={(e) => setLinkInputValue(e.target.value)}
                  placeholder="https://example.com or [[Note Name]]"
                  className="w-full px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#F0FF3D]"
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      insertLink()
                    } else if (e.key === 'Escape') {
                      setShowLinkEditor(false)
                      setLinkInputValue('')
                    }
                  }}
                />
                <p className="text-xs text-zinc-500 mt-2">
                  Use [[Note Name]] for internal wiki links or https:// for external links
                </p>
              </div>

              <div className="flex justify-end gap-3">
                <button
                  onClick={() => {
                    setShowLinkEditor(false)
                    setLinkInputValue('')
                  }}
                  className="px-4 py-2 bg-[var(--bg-input)] hover:bg-[var(--bg-input)]/80 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                {isLink && (
                  <button
                    onClick={() => {
                      editor.dispatchCommand(TOGGLE_LINK_COMMAND, null)
                      setShowLinkEditor(false)
                      setLinkInputValue('')
                    }}
                    className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
                  >
                    Remove Link
                  </button>
                )}
                <button
                  onClick={insertLink}
                  className="px-4 py-2 bg-[#F0FF3D] hover:bg-[#F0FF3D]/90 text-black rounded-lg font-medium transition-colors"
                >
                  {isLink ? 'Update' : 'Insert'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
