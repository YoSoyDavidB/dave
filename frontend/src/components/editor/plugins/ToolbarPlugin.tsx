import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useCallback, useEffect, useState } from 'react'
import {
  $getSelection,
  $isRangeSelection,
  FORMAT_TEXT_COMMAND,
  SELECTION_CHANGE_COMMAND,
  $createParagraphNode,
} from 'lexical'
import { $setBlocksType } from '@lexical/selection'
import { $createHeadingNode, $createQuoteNode, HeadingTagType } from '@lexical/rich-text'
import { $createCodeNode } from '@lexical/code'
import {
  INSERT_ORDERED_LIST_COMMAND,
  INSERT_UNORDERED_LIST_COMMAND,
  INSERT_CHECK_LIST_COMMAND,
  REMOVE_LIST_COMMAND,
  $isListNode,
} from '@lexical/list'
import {
  Bold,
  Italic,
  Underline,
  Strikethrough,
  Code,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  ListTodo,
  Quote,
  Type,
} from 'lucide-react'
import { Sparkles } from 'lucide-react'
import LinkPlugin from './LinkPlugin'
import ImagePlugin from './ImagePlugin'
import TablePlugin from './TablePlugin'
import HorizontalRulePlugin from './HorizontalRulePlugin'
import ExportPlugin from './ExportPlugin'

const LowPriority = 1

export default function ToolbarPlugin() {
  const [editor] = useLexicalComposerContext()
  const [isBold, setIsBold] = useState(false)
  const [isItalic, setIsItalic] = useState(false)
  const [isUnderline, setIsUnderline] = useState(false)
  const [isStrikethrough, setIsStrikethrough] = useState(false)
  const [isCode, setIsCode] = useState(false)
  const [blockType, setBlockType] = useState('paragraph')

  const updateToolbar = useCallback(() => {
    const selection = $getSelection()
    if ($isRangeSelection(selection)) {
      setIsBold(selection.hasFormat('bold'))
      setIsItalic(selection.hasFormat('italic'))
      setIsUnderline(selection.hasFormat('underline'))
      setIsStrikethrough(selection.hasFormat('strikethrough'))
      setIsCode(selection.hasFormat('code'))

      const anchorNode = selection.anchor.getNode()
      const element =
        anchorNode.getKey() === 'root'
          ? anchorNode
          : anchorNode.getTopLevelElementOrThrow()

      const elementKey = element.getKey()
      const elementDOM = editor.getElementByKey(elementKey)

      if (elementDOM !== null) {
        if ($isListNode(element)) {
          const parentList = element
          const type = parentList.getListType()
          setBlockType(type)
        } else {
          const type = element.getType()
          setBlockType(type)
        }
      }
    }
  }, [editor])

  useEffect(() => {
    return editor.registerCommand(
      SELECTION_CHANGE_COMMAND,
      () => {
        updateToolbar()
        return false
      },
      LowPriority
    )
  }, [editor, updateToolbar])

  const formatParagraph = () => {
    editor.update(() => {
      const selection = $getSelection()
      if ($isRangeSelection(selection)) {
        $setBlocksType(selection, () => $createParagraphNode())
      }
    })
  }

  const formatHeading = (headingSize: HeadingTagType) => {
    if (blockType !== headingSize) {
      editor.update(() => {
        const selection = $getSelection()
        if ($isRangeSelection(selection)) {
          $setBlocksType(selection, () => $createHeadingNode(headingSize))
        }
      })
    } else {
      formatParagraph()
    }
  }

  const formatQuote = () => {
    if (blockType !== 'quote') {
      editor.update(() => {
        const selection = $getSelection()
        if ($isRangeSelection(selection)) {
          $setBlocksType(selection, () => $createQuoteNode())
        }
      })
    } else {
      formatParagraph()
    }
  }

  const formatCode = () => {
    if (blockType !== 'code') {
      editor.update(() => {
        const selection = $getSelection()
        if ($isRangeSelection(selection)) {
          $setBlocksType(selection, () => $createCodeNode())
        }
      })
    } else {
      formatParagraph()
    }
  }

  const formatBulletList = () => {
    if (blockType !== 'bullet') {
      editor.dispatchCommand(INSERT_UNORDERED_LIST_COMMAND, undefined)
    } else {
      editor.dispatchCommand(REMOVE_LIST_COMMAND, undefined)
    }
  }

  const formatNumberedList = () => {
    if (blockType !== 'number') {
      editor.dispatchCommand(INSERT_ORDERED_LIST_COMMAND, undefined)
    } else {
      editor.dispatchCommand(REMOVE_LIST_COMMAND, undefined)
    }
  }

  const formatCheckList = () => {
    if (blockType !== 'check') {
      editor.dispatchCommand(INSERT_CHECK_LIST_COMMAND, undefined)
    } else {
      editor.dispatchCommand(REMOVE_LIST_COMMAND, undefined)
    }
  }

  return (
    <div className="flex items-center gap-1 px-4 py-2 border-b border-[var(--border-color)] bg-[var(--bg-sidebar)] flex-wrap">
      {/* Text formatting */}
      <div className="flex items-center gap-1 pr-2 border-r border-[var(--border-color)]">
        <button
          onClick={() => {
            editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'bold')
          }}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${isBold ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Format Bold"
          title="Bold (Cmd+B)"
        >
          <Bold size={18} />
        </button>
        <button
          onClick={() => {
            editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'italic')
          }}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${isItalic ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Format Italic"
          title="Italic (Cmd+I)"
        >
          <Italic size={18} />
        </button>
        <button
          onClick={() => {
            editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'underline')
          }}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${isUnderline ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Format Underline"
          title="Underline (Cmd+U)"
        >
          <Underline size={18} />
        </button>
        <button
          onClick={() => {
            editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'strikethrough')
          }}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${isStrikethrough ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Format Strikethrough"
          title="Strikethrough"
        >
          <Strikethrough size={18} />
        </button>
        <button
          onClick={() => {
            editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'code')
          }}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${isCode ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Format Code"
          title="Inline Code"
        >
          <Code size={18} />
        </button>
      </div>

      {/* Block formatting */}
      <div className="flex items-center gap-1 pr-2 border-r border-[var(--border-color)]">
        <button
          onClick={() => formatParagraph()}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${blockType === 'paragraph' ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Normal Text"
          title="Normal Text"
        >
          <Type size={18} />
        </button>
        <button
          onClick={() => formatHeading('h1')}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${blockType === 'h1' ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Heading 1"
          title="Heading 1"
        >
          <Heading1 size={18} />
        </button>
        <button
          onClick={() => formatHeading('h2')}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${blockType === 'h2' ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Heading 2"
          title="Heading 2"
        >
          <Heading2 size={18} />
        </button>
        <button
          onClick={() => formatHeading('h3')}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${blockType === 'h3' ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Heading 3"
          title="Heading 3"
        >
          <Heading3 size={18} />
        </button>
      </div>

      {/* Lists */}
      <div className="flex items-center gap-1 pr-2 border-r border-[var(--border-color)]">
        <button
          onClick={formatBulletList}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${blockType === 'bullet' ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Bullet List"
          title="Bullet List"
        >
          <List size={18} />
        </button>
        <button
          onClick={formatNumberedList}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${blockType === 'number' ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Numbered List"
          title="Numbered List"
        >
          <ListOrdered size={18} />
        </button>
        <button
          onClick={formatCheckList}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${blockType === 'check' ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Task List"
          title="Task List (Checkboxes)"
        >
          <ListTodo size={18} />
        </button>
      </div>

      {/* Quote & Code Block */}
      <div className="flex items-center gap-1 pr-2 border-r border-[var(--border-color)]">
        <button
          onClick={formatQuote}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${blockType === 'quote' ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Quote"
          title="Quote Block"
        >
          <Quote size={18} />
        </button>
        <button
          onClick={formatCode}
          className={`p-2 rounded hover:bg-[var(--bg-input)] transition-colors ${blockType === 'code' ? 'bg-[var(--bg-input)] text-[#F0FF3D]' : 'text-zinc-400'
            }`}
          aria-label="Code Block"
          title="Code Block"
        >
          <Code size={18} />
        </button>
      </div>

      {/* Link, Image, Table & HR */}
      <LinkPlugin />
      <ImagePlugin />
      <TablePlugin />
      <HorizontalRulePlugin />

      {/* AI Assistant & Export */}
      <div className="flex items-center gap-1 pl-2 border-l border-[var(--border-color)]">
        <button
          onClick={() => {
            // Trigger AI modal by dispatching a custom event
            window.dispatchEvent(new CustomEvent('open-ai-assistant'))
          }}
          className="p-2 rounded hover:bg-[var(--bg-input)] text-[#F0FF3D] hover:text-[#F0FF3D]/80 transition-colors"
          aria-label="AI Assistant"
          title="AI Writing Assistant (Cmd+K)"
        >
          <Sparkles size={18} />
        </button>
        <ExportPlugin />
      </div>
    </div>
  )
}
