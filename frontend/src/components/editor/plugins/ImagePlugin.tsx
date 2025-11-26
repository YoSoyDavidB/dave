import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { $insertNodes } from 'lexical'
import { useState } from 'react'
import { Image as ImageIcon } from 'lucide-react'
import { $createImageNode } from '../nodes/ImageNode'

export default function ImagePlugin() {
  const [editor] = useLexicalComposerContext()
  const [showImageModal, setShowImageModal] = useState(false)
  const [imageUrl, setImageUrl] = useState('')
  const [imageAlt, setImageAlt] = useState('')

  const insertImage = () => {
    if (!imageUrl) return

    editor.update(() => {
      const imageNode = $createImageNode({
        src: imageUrl,
        altText: imageAlt || 'Image',
      })
      $insertNodes([imageNode])
    })

    setShowImageModal(false)
    setImageUrl('')
    setImageAlt('')
  }

  return (
    <>
      {/* Image button */}
      <button
        onClick={() => setShowImageModal(true)}
        className="p-2 rounded hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
        aria-label="Insert Image"
        title="Insert Image"
      >
        <ImageIcon size={18} />
      </button>

      {/* Image insertion modal */}
      {showImageModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Insert Image</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Image URL</label>
                <input
                  type="text"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  placeholder="https://example.com/image.jpg"
                  className="w-full px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#F0FF3D]"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  Alt Text (optional)
                </label>
                <input
                  type="text"
                  value={imageAlt}
                  onChange={(e) => setImageAlt(e.target.value)}
                  placeholder="Description of the image"
                  className="w-full px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#F0FF3D]"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      insertImage()
                    } else if (e.key === 'Escape') {
                      setShowImageModal(false)
                      setImageUrl('')
                      setImageAlt('')
                    }
                  }}
                />
              </div>

              <div className="flex justify-end gap-3">
                <button
                  onClick={() => {
                    setShowImageModal(false)
                    setImageUrl('')
                    setImageAlt('')
                  }}
                  className="px-4 py-2 bg-[var(--bg-input)] hover:bg-[var(--bg-input)]/80 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={insertImage}
                  disabled={!imageUrl}
                  className="px-4 py-2 bg-[#F0FF3D] hover:bg-[#F0FF3D]/90 text-black rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Insert
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
