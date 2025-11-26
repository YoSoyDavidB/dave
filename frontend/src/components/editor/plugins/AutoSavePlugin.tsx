import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect, useRef } from 'react'

interface AutoSavePluginProps {
  onSave?: () => void
  delayMs?: number
}

export default function AutoSavePlugin({ onSave, delayMs = 3000 }: AutoSavePluginProps) {
  const [editor] = useLexicalComposerContext()
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!onSave) return

    return editor.registerUpdateListener(() => {
      // Clear existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }

      // Set new timeout for auto-save
      timeoutRef.current = setTimeout(() => {
        onSave()
      }, delayMs)
    })
  }, [editor, onSave, delayMs])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return null
}
