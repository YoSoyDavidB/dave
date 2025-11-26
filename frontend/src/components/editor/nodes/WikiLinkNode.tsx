import {
  DecoratorNode,
  LexicalNode,
  NodeKey,
  SerializedLexicalNode,
  Spread,
} from 'lexical'
import WikiLinkComponent from './WikiLinkComponent'

export type SerializedWikiLinkNode = Spread<
  {
    noteName: string
  },
  SerializedLexicalNode
>

export class WikiLinkNode extends DecoratorNode<JSX.Element> {
  __noteName: string

  static getType(): string {
    return 'wiki-link'
  }

  static clone(node: WikiLinkNode): WikiLinkNode {
    return new WikiLinkNode(node.__noteName, node.__key)
  }

  constructor(noteName: string, key?: NodeKey) {
    super(key)
    this.__noteName = noteName
  }

  createDOM(): HTMLElement {
    return document.createElement('span')
  }

  updateDOM(): false {
    return false
  }

  static importJSON(serializedNode: SerializedWikiLinkNode): WikiLinkNode {
    return $createWikiLinkNode(serializedNode.noteName)
  }

  exportJSON(): SerializedWikiLinkNode {
    return {
      noteName: this.__noteName,
      type: 'wiki-link',
      version: 1,
    }
  }

  getNoteName(): string {
    return this.__noteName
  }

  setNoteName(noteName: string): void {
    const writable = this.getWritable()
    writable.__noteName = noteName
  }

  decorate(): JSX.Element {
    return (
      <WikiLinkComponent
        noteName={this.__noteName}
        nodeKey={this.__key}
      />
    )
  }

  getTextContent(): string {
    return `[[${this.__noteName}]]`
  }
}


export function $createWikiLinkNode(noteName: string): WikiLinkNode {
  return new WikiLinkNode(noteName)
}

export function $isWikiLinkNode(
  node: LexicalNode | null | undefined
): node is WikiLinkNode {
  return node instanceof WikiLinkNode
}
