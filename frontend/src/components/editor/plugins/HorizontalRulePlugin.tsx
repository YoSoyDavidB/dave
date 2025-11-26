import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { $insertNodes } from 'lexical'
import { Minus } from 'lucide-react'
import { $createHorizontalRuleNode } from '../nodes/HorizontalRuleNode'

export default function HorizontalRulePlugin() {
  const [editor] = useLexicalComposerContext()

  const insertHorizontalRule = () => {
    editor.update(() => {
      const hrNode = $createHorizontalRuleNode()
      $insertNodes([hrNode])
    })
  }

  return (
    <button
      onClick={insertHorizontalRule}
      className="p-2 rounded hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
      aria-label="Insert Horizontal Rule"
      title="Insert Horizontal Rule (---)"
    >
      <Minus size={18} />
    </button>
  )
}
