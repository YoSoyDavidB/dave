import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { $insertNodes } from 'lexical'
import { useState } from 'react'
import { Table as TableIcon } from 'lucide-react'
import {
  $createTableNodeWithDimensions,
} from '@lexical/table'

export default function TablePlugin() {
  const [editor] = useLexicalComposerContext()
  const [showTableModal, setShowTableModal] = useState(false)
  const [rows, setRows] = useState(3)
  const [columns, setColumns] = useState(3)

  const insertTable = () => {
    editor.update(() => {
      const tableNode = $createTableNodeWithDimensions(rows, columns, true)
      $insertNodes([tableNode])
    })

    setShowTableModal(false)
    setRows(3)
    setColumns(3)
  }

  return (
    <>
      {/* Table button */}
      <button
        onClick={() => setShowTableModal(true)}
        className="p-2 rounded hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
        aria-label="Insert Table"
        title="Insert Table"
      >
        <TableIcon size={18} />
      </button>

      {/* Table insertion modal */}
      {showTableModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Insert Table</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  Number of Rows
                </label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={rows}
                  onChange={(e) => setRows(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
                  className="w-full px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#F0FF3D]"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  Number of Columns
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={columns}
                  onChange={(e) => setColumns(Math.max(1, Math.min(10, parseInt(e.target.value) || 1)))}
                  className="w-full px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#F0FF3D]"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      insertTable()
                    } else if (e.key === 'Escape') {
                      setShowTableModal(false)
                      setRows(3)
                      setColumns(3)
                    }
                  }}
                />
              </div>

              <div className="text-sm text-zinc-500">
                Will create a {rows}x{columns} table with headers
              </div>

              <div className="flex justify-end gap-3">
                <button
                  onClick={() => {
                    setShowTableModal(false)
                    setRows(3)
                    setColumns(3)
                  }}
                  className="px-4 py-2 bg-[var(--bg-input)] hover:bg-[var(--bg-input)]/80 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={insertTable}
                  className="px-4 py-2 bg-[#F0FF3D] hover:bg-[#F0FF3D]/90 text-black rounded-lg font-medium transition-colors"
                >
                  Insert Table
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
