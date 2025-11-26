import {
  DecoratorNode,
  LexicalNode,
  NodeKey,
  SerializedLexicalNode,
  Spread,
} from 'lexical'
import { Database, Code } from 'lucide-react'

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

function DataviewComponent({
  query,
  dataviewType,
}: {
  query: string
  dataviewType: DataviewType
  nodeKey: NodeKey
}) {
  const isJS = dataviewType === 'dataviewjs'

  return (
    <div className="my-4 border border-[#F0FF3D]/30 rounded-lg overflow-hidden bg-[#F0FF3D]/5">
      {/* Header */}
      <div className="px-4 py-2 bg-[#F0FF3D]/10 border-b border-[#F0FF3D]/30 flex items-center gap-2">
        {isJS ? (
          <Code size={16} className="text-[#F0FF3D]" />
        ) : (
          <Database size={16} className="text-[#F0FF3D]" />
        )}
        <span className="text-[#F0FF3D] text-sm font-medium">
          {isJS ? 'DataviewJS Query' : 'Dataview Query'}
        </span>
        <span className="ml-auto text-xs text-zinc-500 italic">
          Dataview queries are not yet fully executed
        </span>
      </div>

      {/* Query content */}
      <div className="p-4">
        <pre className="text-sm text-zinc-300 font-mono whitespace-pre-wrap">
          {query}
        </pre>
      </div>

      {/* Footer hint */}
      <div className="px-4 py-2 bg-[var(--bg-input)]/50 border-t border-[var(--border-color)] text-xs text-zinc-500">
        💡 This query will be executed when Dataview integration is fully implemented
      </div>
    </div>
  )
}

export function $createDataviewNode(query: string, type: DataviewType = 'dataview'): DataviewNode {
  return new DataviewNode(query, type)
}

export function $isDataviewNode(
  node: LexicalNode | null | undefined
): node is DataviewNode {
  return node instanceof DataviewNode
}
