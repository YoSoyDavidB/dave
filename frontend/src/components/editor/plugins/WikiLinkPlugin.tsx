import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect } from 'react'
import { TextNode } from 'lexical'
import { $createWikiLinkNode } from '../nodes/WikiLinkNode'

export default function WikiLinkPlugin() {
  const [editor] = useLexicalComposerContext()

  useEffect(() => {
    // Transform [[note]] text into WikiLinkNode
    const removeTransform = editor.registerNodeTransform(TextNode, (textNode: TextNode) => {
      const text = textNode.getTextContent()
      const wikiLinkRegex = /\[\[([^\]]+)\]\]/g

      let match
      const matches: Array<{ start: number; end: number; noteName: string }> = []

      while ((match = wikiLinkRegex.exec(text)) !== null) {
        matches.push({
          start: match.index,
          end: match.index + match[0].length,
          noteName: match[1],
        })
      }

      if (matches.length === 0) return

      // Process matches in reverse order to maintain offsets
      for (let i = matches.length - 1; i >= 0; i--) {
        const { start, end, noteName } = matches[i]

        // Split the text node
        let targetNode = textNode

        if (start > 0) {
          // Split before the wiki link
          targetNode = textNode.splitText(start)[1]
        }

        if (end < text.length) {
          // Split after the wiki link
          targetNode.splitText(end - start)
        }

        // Replace with WikiLinkNode
        const wikiLinkNode = $createWikiLinkNode(noteName)
        targetNode.replace(wikiLinkNode)
      }
    })

    return () => {
      removeTransform()
    }
  }, [editor])

  return null
}
