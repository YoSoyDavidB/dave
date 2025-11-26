import {
  DecoratorNode,
  NodeKey,
  LexicalNode,
  SerializedLexicalNode,
} from 'lexical'

export type SerializedHorizontalRuleNode = SerializedLexicalNode

export class HorizontalRuleNode extends DecoratorNode<JSX.Element> {
  static getType(): string {
    return 'horizontal-rule'
  }

  static clone(node: HorizontalRuleNode): HorizontalRuleNode {
    return new HorizontalRuleNode(node.__key)
  }

  constructor(key?: NodeKey) {
    super(key)
  }

  createDOM(): HTMLElement {
    const elem = document.createElement('div')
    elem.className = 'editor-hr'
    return elem
  }

  updateDOM(): false {
    return false
  }

  decorate(): JSX.Element {
    return <hr className="my-4 border-zinc-600" />
  }

  static importJSON(): HorizontalRuleNode {
    return $createHorizontalRuleNode()
  }

  exportJSON(): SerializedHorizontalRuleNode {
    return {
      type: 'horizontal-rule',
      version: 1,
    }
  }
}

export function $createHorizontalRuleNode(): HorizontalRuleNode {
  return new HorizontalRuleNode()
}

export function $isHorizontalRuleNode(
  node: LexicalNode | null | undefined
): node is HorizontalRuleNode {
  return node instanceof HorizontalRuleNode
}
