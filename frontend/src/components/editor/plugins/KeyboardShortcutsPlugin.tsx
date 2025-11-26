import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect } from 'react'
import { COMMAND_PRIORITY_HIGH, KEY_MODIFIER_COMMAND } from 'lexical'

interface KeyboardShortcutsPluginProps {
  onSave?: () => void
}

export default function KeyboardShortcutsPlugin({ onSave }: KeyboardShortcutsPluginProps) {
  const [editor] = useLexicalComposerContext()

  useEffect(() => {
    // Register Cmd+S / Ctrl+S for save
    return editor.registerCommand(
      KEY_MODIFIER_COMMAND,
      (event: KeyboardEvent) => {
        const { key, ctrlKey, metaKey } = event

        // Check for Cmd+S (Mac) or Ctrl+S (Windows/Linux)
        if (key === 's' && (metaKey || ctrlKey)) {
          event.preventDefault()
          event.stopPropagation()

          if (onSave) {
            onSave()
          }

          return true
        }

        return false
      },
      COMMAND_PRIORITY_HIGH
    )
  }, [editor, onSave])

  return null
}
