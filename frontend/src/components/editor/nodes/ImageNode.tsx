import {
  DecoratorNode,
  NodeKey,
  LexicalNode,
  SerializedLexicalNode,
  Spread,
} from 'lexical'

export interface ImagePayload {
  altText: string
  src: string
  key?: NodeKey
}

export type SerializedImageNode = Spread<
  {
    altText: string
    src: string
  },
  SerializedLexicalNode
>

export class ImageNode extends DecoratorNode<JSX.Element> {
  __src: string
  __altText: string

  static getType(): string {
    return 'image'
  }

  static clone(node: ImageNode): ImageNode {
    return new ImageNode(node.__src, node.__altText, node.__key)
  }

  constructor(src: string, altText: string, key?: NodeKey) {
    super(key)
    this.__src = src
    this.__altText = altText
  }

  createDOM(): HTMLElement {
    const elem = document.createElement('div')
    elem.className = 'editor-image'
    return elem
  }

  updateDOM(): false {
    return false
  }

  getSrc(): string {
    return this.__src
  }

  getAltText(): string {
    return this.__altText
  }

  decorate(): JSX.Element {
    return (
      <img
        src={this.__src}
        alt={this.__altText}
        className="max-w-full h-auto rounded-lg my-4"
      />
    )
  }

  static importJSON(serializedNode: SerializedImageNode): ImageNode {
    const { altText, src } = serializedNode
    return $createImageNode({
      altText,
      src,
    })
  }

  exportJSON(): SerializedImageNode {
    return {
      altText: this.getAltText(),
      src: this.getSrc(),
      type: 'image',
      version: 1,
    }
  }
}

export function $createImageNode({ altText, src, key }: ImagePayload): ImageNode {
  return new ImageNode(src, altText, key)
}

export function $isImageNode(node: LexicalNode | null | undefined): node is ImageNode {
  return node instanceof ImageNode
}
