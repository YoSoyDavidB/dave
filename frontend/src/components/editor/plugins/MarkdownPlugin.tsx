import { useEffect } from 'react'
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { $convertFromMarkdownString, $convertToMarkdownString, TRANSFORMERS } from '@lexical/markdown'

interface MarkdownPluginProps {
  initialMarkdown?: string
  onChange?: (markdown: string) => void
}

export default function MarkdownPlugin({ initialMarkdown, onChange }: MarkdownPluginProps) {
  const [editor] = useLexicalComposerContext()

  // Load initial markdown
  useEffect(() => {
    if (initialMarkdown) {
      editor.update(() => {
        $convertFromMarkdownString(initialMarkdown, TRANSFORMERS)
      })
    }
  }, []) // Only run once on mount

  // Listen to changes and convert to markdown
  useEffect(() => {
    if (!onChange) return

    return editor.registerUpdateListener(({ editorState }) => {
      editorState.read(() => {
        const markdown = $convertToMarkdownString(TRANSFORMERS)
        onChange(markdown)
      })
    })
  }, [editor, onChange])

  return null
}
