import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect } from 'react'
import { $isCodeNode, CodeNode } from '@lexical/code'
import { $createDataviewNode, DataviewType } from '../nodes/DataviewNode'

export default function DataviewPlugin() {
  const [editor] = useLexicalComposerContext()

  useEffect(() => {
    // Transform code blocks with language "dataview" or "dataviewjs" into DataviewNode
    const removeTransform = editor.registerNodeTransform(CodeNode, (codeNode: CodeNode) => {
      const language = codeNode.getLanguage()

      if (language === 'dataview' || language === 'dataviewjs') {
        const query = codeNode.getTextContent()
        const dataviewType: DataviewType = language as DataviewType

        // Replace with DataviewNode
        const dataviewNode = $createDataviewNode(query, dataviewType)
        codeNode.replace(dataviewNode)
      }
    })

    return () => {
      removeTransform()
    }
  }, [editor])

  return null
}
