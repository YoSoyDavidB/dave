import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect, useState } from 'react'
import { $getRoot } from 'lexical'
import { FileText, Clock } from 'lucide-react'

export default function WordCountPlugin() {
  const [editor] = useLexicalComposerContext()
  const [wordCount, setWordCount] = useState(0)
  const [charCount, setCharCount] = useState(0)
  const [readingTime, setReadingTime] = useState(0)

  useEffect(() => {
    const updateCounts = () => {
      editor.getEditorState().read(() => {
        const root = $getRoot()
        const text = root.getTextContent()

        // Character count
        const chars = text.length
        setCharCount(chars)

        // Word count
        const words = text.trim().split(/\s+/).filter((word) => word.length > 0).length
        setWordCount(words)

        // Reading time (average 200 words per minute)
        const minutes = Math.ceil(words / 200)
        setReadingTime(minutes)
      })
    }

    // Update on initial load
    updateCounts()

    // Update on editor changes
    return editor.registerUpdateListener(() => {
      updateCounts()
    })
  }, [editor])

  return (
    <div className="border-t border-[var(--border-color)] bg-[var(--bg-sidebar)] px-4 py-2 flex items-center justify-between text-xs text-zinc-400">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5" title="Word count">
          <FileText size={14} />
          <span>{wordCount} {wordCount === 1 ? 'word' : 'words'}</span>
        </div>
        <div className="text-zinc-600">•</div>
        <div title="Character count">
          {charCount} {charCount === 1 ? 'character' : 'characters'}
        </div>
      </div>
      <div className="flex items-center gap-1.5" title="Estimated reading time">
        <Clock size={14} />
        <span>{readingTime} min read</span>
      </div>
    </div>
  )
}
