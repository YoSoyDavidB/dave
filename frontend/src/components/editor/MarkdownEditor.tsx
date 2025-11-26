import { LexicalComposer } from '@lexical/react/LexicalComposer'
import { RichTextPlugin } from '@lexical/react/LexicalRichTextPlugin'
import { ContentEditable } from '@lexical/react/LexicalContentEditable'
import { HistoryPlugin } from '@lexical/react/LexicalHistoryPlugin'
import { LexicalErrorBoundary } from '@lexical/react/LexicalErrorBoundary'
import { HeadingNode, QuoteNode } from '@lexical/rich-text'
import { ListItemNode, ListNode } from '@lexical/list'
import { CodeNode, CodeHighlightNode } from '@lexical/code'
import { LinkNode } from '@lexical/link'
import { MarkdownShortcutPlugin } from '@lexical/react/LexicalMarkdownShortcutPlugin'
import { TRANSFORMERS } from '@lexical/markdown'
import { LinkPlugin as LexicalLinkPlugin } from '@lexical/react/LexicalLinkPlugin'
import { TablePlugin as LexicalTablePlugin } from '@lexical/react/LexicalTablePlugin'
import { CheckListPlugin } from '@lexical/react/LexicalCheckListPlugin'
import { TableCellNode, TableNode, TableRowNode } from '@lexical/table'
import MarkdownPlugin from './plugins/MarkdownPlugin'
import ToolbarPlugin from './plugins/ToolbarPlugin'
import KeyboardShortcutsPlugin from './plugins/KeyboardShortcutsPlugin'
import AutoSavePlugin from './plugins/AutoSavePlugin'
import DragDropImagePlugin from './plugins/DragDropImagePlugin'
import AIAssistantPlugin from './plugins/AIAssistantPlugin'
import TableContextMenuPlugin from './plugins/TableContextMenuPlugin'
import SlashCommandPlugin from './plugins/SlashCommandPlugin'
import MentionPlugin from './plugins/MentionPlugin'
import FindReplacePlugin from './plugins/FindReplacePlugin'
import WordCountPlugin from './plugins/WordCountPlugin'
import WikiLinkPlugin from './plugins/WikiLinkPlugin'
import DataviewPlugin from './plugins/DataviewPlugin'
import { ImageNode } from './nodes/ImageNode'
import { HorizontalRuleNode } from './nodes/HorizontalRuleNode'
import { WikiLinkNode } from './nodes/WikiLinkNode'
import { DataviewNode } from './nodes/DataviewNode'

interface MarkdownEditorProps {
  initialContent?: string
  onChange?: (markdown: string) => void
  editable?: boolean
  onSave?: () => void
  autoSave?: boolean
  autoSaveDelayMs?: number
}

const theme = {
  paragraph: 'mb-2',
  heading: {
    h1: 'text-3xl font-bold mb-4 mt-6',
    h2: 'text-2xl font-bold mb-3 mt-5',
    h3: 'text-xl font-bold mb-2 mt-4',
    h4: 'text-lg font-bold mb-2 mt-3',
    h5: 'text-base font-bold mb-2 mt-2',
  },
  list: {
    ul: 'list-disc list-inside ml-4 mb-2',
    ol: 'list-decimal list-inside ml-4 mb-2',
    listitem: 'mb-1',
  },
  code: 'bg-[var(--bg-input)] px-1.5 py-0.5 rounded text-sm font-mono',
  codeHighlight: {
    atrule: 'text-purple-400',
    attr: 'text-blue-400',
    boolean: 'text-orange-400',
    builtin: 'text-cyan-400',
    cdata: 'text-gray-400',
    char: 'text-green-400',
    class: 'text-yellow-400',
    'class-name': 'text-yellow-400',
    comment: 'text-gray-500 italic',
    constant: 'text-orange-400',
    deleted: 'text-red-400',
    doctype: 'text-gray-400',
    entity: 'text-orange-400',
    function: 'text-blue-400',
    important: 'text-red-400',
    inserted: 'text-green-400',
    keyword: 'text-purple-400',
    namespace: 'text-cyan-400',
    number: 'text-orange-400',
    operator: 'text-gray-300',
    prolog: 'text-gray-400',
    property: 'text-blue-400',
    punctuation: 'text-gray-300',
    regex: 'text-orange-400',
    selector: 'text-green-400',
    string: 'text-green-400',
    symbol: 'text-orange-400',
    tag: 'text-red-400',
    url: 'text-blue-400',
    variable: 'text-orange-400',
  },
  link: 'text-[#F0FF3D] hover:underline cursor-pointer',
  quote: 'border-l-4 border-zinc-600 pl-4 italic text-zinc-400 my-4',
  text: {
    bold: 'font-bold',
    italic: 'italic',
    underline: 'underline',
    strikethrough: 'line-through',
    code: 'bg-[var(--bg-input)] px-1.5 py-0.5 rounded text-sm font-mono',
  },
  table: 'border-collapse table-auto w-full my-4',
  tableCell: 'border border-zinc-600 px-3 py-2 text-left',
  tableCellHeader: 'border border-zinc-600 px-3 py-2 text-left font-bold bg-zinc-800',
}

function onError(error: Error) {
  console.error('Lexical error:', error)
}

export default function MarkdownEditor({
  initialContent = '',
  onChange,
  editable = true,
  onSave,
  autoSave = false,
  autoSaveDelayMs = 3000,
}: MarkdownEditorProps) {
  const initialConfig = {
    namespace: 'MarkdownEditor',
    theme,
    onError,
    editable,
    nodes: [
      HeadingNode,
      ListNode,
      ListItemNode,
      QuoteNode,
      CodeNode,
      CodeHighlightNode,
      LinkNode,
      ImageNode,
      TableNode,
      TableCellNode,
      TableRowNode,
      HorizontalRuleNode,
      WikiLinkNode,
      DataviewNode,
    ],
  }

  return (
    <LexicalComposer initialConfig={initialConfig}>
      <div className="relative h-full flex flex-col">
        {editable && <ToolbarPlugin />}
        <div className="flex-1 overflow-auto">
          <RichTextPlugin
            contentEditable={
              <ContentEditable className="min-h-full px-6 py-4 focus:outline-none text-white prose prose-invert max-w-none" />
            }
            placeholder={
              <div className="absolute top-4 left-6 text-zinc-500 pointer-events-none">
                Start writing...
              </div>
            }
            ErrorBoundary={LexicalErrorBoundary}
          />
        </div>
        <HistoryPlugin />
        <MarkdownShortcutPlugin transformers={TRANSFORMERS} />
        <LexicalLinkPlugin />
        <LexicalTablePlugin />
        <CheckListPlugin />
        <DragDropImagePlugin />
        <AIAssistantPlugin showButton={false} />
        <TableContextMenuPlugin />
        <SlashCommandPlugin />
        <MentionPlugin />
        <FindReplacePlugin />
        <WikiLinkPlugin />
        <DataviewPlugin />
        <MarkdownPlugin initialMarkdown={initialContent} onChange={onChange} />
        <KeyboardShortcutsPlugin onSave={onSave} />
        {autoSave && onSave && <AutoSavePlugin onSave={onSave} delayMs={autoSaveDelayMs} />}
        {editable && <WordCountPlugin />}
      </div>
    </LexicalComposer>
  )
}
