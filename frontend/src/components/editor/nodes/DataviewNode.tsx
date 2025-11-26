import {
  DecoratorNode,
  LexicalNode,
  NodeKey,
  SerializedLexicalNode,
  Spread,
} from 'lexical'
import DataviewComponent from './DataviewComponent'

export type DataviewType = 'dataview' | 'dataviewjs'

export type SerializedDataviewNode = Spread<
  {
    query: string
    type: DataviewType
  },
  SerializedLexicalNode
>

export class DataviewNode extends DecoratorNode<JSX.Element> {
  __query: string
  __dataviewType: DataviewType

  static getType(): string {
    return 'dataview'
  }

  static clone(node: DataviewNode): DataviewNode {
    return new DataviewNode(node.__query, node.__dataviewType, node.__key)
  }

  constructor(query: string, dataviewType: DataviewType = 'dataview', key?: NodeKey) {
    super(key)
    this.__query = query
    this.__dataviewType = dataviewType
  }

  createDOM(): HTMLElement {
    return document.createElement('div')
  }

  updateDOM(): false {
    return false
  }

  static importJSON(serializedNode: SerializedDataviewNode): DataviewNode {
    return $createDataviewNode(serializedNode.query, serializedNode.type)
  }

  exportJSON(): SerializedDataviewNode {
    return {
      query: this.__query,
      type: this.__dataviewType,
      version: 1,
    }
  }

  getQuery(): string {
    return this.__query
  }

  setQuery(query: string): void {
    const writable = this.getWritable()
    writable.__query = query
  }

  getDataviewType(): DataviewType {
    return this.__dataviewType
  }

  decorate(): JSX.Element {
    return (
      <DataviewComponent
        query={this.__query}
        dataviewType={this.__dataviewType}
        nodeKey={this.__key}
      />
    )
  }

  getTextContent(): string {
    return `\`\`\`${this.__dataviewType}\n${this.__query}\n\`\`\``
  }
}


export function $createDataviewNode(query: string, type: DataviewType = 'dataview'): DataviewNode {
  return new DataviewNode(query, type)
}

export function $isDataviewNode(
  node: LexicalNode | null | undefined
): node is DataviewNode {
  return node instanceof DataviewNode
}
