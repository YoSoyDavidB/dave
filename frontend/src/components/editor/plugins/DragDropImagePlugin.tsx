import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect } from 'react'
import { DRAG_DROP_PASTE } from '@lexical/rich-text'
import { $insertNodes } from 'lexical'
import { $createImageNode } from '../nodes/ImageNode'

export default function DragDropImagePlugin() {
  const [editor] = useLexicalComposerContext()

  useEffect(() => {
    return editor.registerCommand(
      DRAG_DROP_PASTE,
      (files: File[]) => {
        const images = files.filter((file) => /image\/(png|jpg|jpeg|gif|webp)/.test(file.type))

        if (images.length > 0) {
          images.forEach((image) => {
            const reader = new FileReader()
            reader.onload = (e) => {
              if (e.target?.result && typeof e.target.result === 'string') {
                editor.update(() => {
                  const imageNode = $createImageNode({
                    src: e.target.result as string,
                    altText: image.name,
                  })
                  $insertNodes([imageNode])
                })
              }
            }
            reader.readAsDataURL(image)
          })

          return true
        }

        return false
      },
      1
    )
  }, [editor])

  return null
}
