import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect, useState, useCallback } from 'react'
import {
  $getSelection,
  $isRangeSelection,
  $createParagraphNode,
  TextNode,
  COMMAND_PRIORITY_LOW,
  KEY_ARROW_DOWN_COMMAND,
  KEY_ARROW_UP_COMMAND,
  KEY_ENTER_COMMAND,
  KEY_ESCAPE_COMMAND,
} from 'lexical'
import { $setBlocksType } from '@lexical/selection'
import { $createHeadingNode, $createQuoteNode } from '@lexical/rich-text'
import { $createCodeNode } from '@lexical/code'
import {
  INSERT_ORDERED_LIST_COMMAND,
  INSERT_UNORDERED_LIST_COMMAND,
  INSERT_CHECK_LIST_COMMAND,
} from '@lexical/list'
import { $createTableNodeWithDimensions } from '@lexical/table'
import { $insertNodes } from 'lexical'
import { $createHorizontalRuleNode } from '../nodes/HorizontalRuleNode'
import {
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  ListTodo,
  Quote,
  Code,
  Table,
  Minus,
  Image,
  Type,
} from 'lucide-react'

interface SlashCommand {
  id: string
  label: string
  icon: React.ReactNode
  keywords: string[]
  onSelect: () => void
}

export default function SlashCommandPlugin() {
  const [editor] = useLexicalComposerContext()
  const [showMenu, setShowMenu] = useState(false)
  const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0 })
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')

  const insertImage = useCallback(() => {
    const url = prompt('Enter image URL:')
    if (url) {
      editor.update(() => {
        const selection = $getSelection()
        if ($isRangeSelection(selection)) {
          // Import and use ImageNode
          import('../nodes/ImageNode').then(({ $createImageNode }) => {
            editor.update(() => {
              const imageNode = $createImageNode({ src: url, altText: 'Image' })
              $insertNodes([imageNode])
            })
          })
        }
      })
    }
  }, [editor])

  const commands: SlashCommand[] = [
    {
      id: 'paragraph',
      label: 'Text',
      icon: <Type size={18} />,
      keywords: ['text', 'paragraph', 'normal'],
      onSelect: () => {
        editor.update(() => {
          const selection = $getSelection()
          if ($isRangeSelection(selection)) {
            $setBlocksType(selection, () => $createParagraphNode())
          }
        })
      },
    },
    {
      id: 'h1',
      label: 'Heading 1',
      icon: <Heading1 size={18} />,
      keywords: ['h1', 'heading1', 'title'],
      onSelect: () => {
        editor.update(() => {
          const selection = $getSelection()
          if ($isRangeSelection(selection)) {
            $setBlocksType(selection, () => $createHeadingNode('h1'))
          }
        })
      },
    },
    {
      id: 'h2',
      label: 'Heading 2',
      icon: <Heading2 size={18} />,
      keywords: ['h2', 'heading2', 'subtitle'],
      onSelect: () => {
        editor.update(() => {
          const selection = $getSelection()
          if ($isRangeSelection(selection)) {
            $setBlocksType(selection, () => $createHeadingNode('h2'))
          }
        })
      },
    },
    {
      id: 'h3',
      label: 'Heading 3',
      icon: <Heading3 size={18} />,
      keywords: ['h3', 'heading3', 'section'],
      onSelect: () => {
        editor.update(() => {
          const selection = $getSelection()
          if ($isRangeSelection(selection)) {
            $setBlocksType(selection, () => $createHeadingNode('h3'))
          }
        })
      },
    },
    {
      id: 'bullet-list',
      label: 'Bullet List',
      icon: <List size={18} />,
      keywords: ['ul', 'bullet', 'list', 'unordered'],
      onSelect: () => {
        editor.dispatchCommand(INSERT_UNORDERED_LIST_COMMAND, undefined)
      },
    },
    {
      id: 'numbered-list',
      label: 'Numbered List',
      icon: <ListOrdered size={18} />,
      keywords: ['ol', 'numbered', 'list', 'ordered', '123'],
      onSelect: () => {
        editor.dispatchCommand(INSERT_ORDERED_LIST_COMMAND, undefined)
      },
    },
    {
      id: 'task-list',
      label: 'Task List',
      icon: <ListTodo size={18} />,
      keywords: ['todo', 'task', 'checkbox', 'checklist'],
      onSelect: () => {
        editor.dispatchCommand(INSERT_CHECK_LIST_COMMAND, undefined)
      },
    },
    {
      id: 'quote',
      label: 'Quote',
      icon: <Quote size={18} />,
      keywords: ['quote', 'blockquote', 'citation'],
      onSelect: () => {
        editor.update(() => {
          const selection = $getSelection()
          if ($isRangeSelection(selection)) {
            $setBlocksType(selection, () => $createQuoteNode())
          }
        })
      },
    },
    {
      id: 'code',
      label: 'Code Block',
      icon: <Code size={18} />,
      keywords: ['code', 'codeblock', 'pre'],
      onSelect: () => {
        editor.update(() => {
          const selection = $getSelection()
          if ($isRangeSelection(selection)) {
            $setBlocksType(selection, () => $createCodeNode())
          }
        })
      },
    },
    {
      id: 'table',
      label: 'Table',
      icon: <Table size={18} />,
      keywords: ['table', 'grid'],
      onSelect: () => {
        editor.update(() => {
          const tableNode = $createTableNodeWithDimensions(3, 3, true)
          $insertNodes([tableNode])
        })
      },
    },
    {
      id: 'hr',
      label: 'Divider',
      icon: <Minus size={18} />,
      keywords: ['hr', 'divider', 'separator', 'line', 'horizontal'],
      onSelect: () => {
        editor.update(() => {
          const hrNode = $createHorizontalRuleNode()
          $insertNodes([hrNode])
        })
      },
    },
    {
      id: 'image',
      label: 'Image',
      icon: <Image size={18} />,
      keywords: ['image', 'img', 'picture', 'photo'],
      onSelect: insertImage,
    },
  ]

  const filteredCommands = commands.filter((cmd) => {
    const query = searchQuery.toLowerCase()
    return (
      cmd.label.toLowerCase().includes(query) ||
      cmd.keywords.some((keyword) => keyword.toLowerCase().includes(query))
    )
  })

  useEffect(() => {
    const updateListener = editor.registerUpdateListener(({ editorState }) => {
      editorState.read(() => {
        const selection = $getSelection()
        if (!$isRangeSelection(selection)) {
          setShowMenu(false)
          return
        }

        const anchorNode = selection.anchor.getNode()
        const textContent = anchorNode.getTextContent()
        const anchorOffset = selection.anchor.offset

        // Check if we just typed "/"
        if (textContent[anchorOffset - 1] === '/' && anchorOffset > 0) {
          // Check if "/" is at the start of the line or preceded by whitespace
          const prevChar = textContent[anchorOffset - 2]
          if (anchorOffset === 1 || !prevChar || prevChar === ' ') {
            // Get the DOM element position for the menu
            const domSelection = window.getSelection()
            if (domSelection && domSelection.rangeCount > 0) {
              const range = domSelection.getRangeAt(0)
              const rect = range.getBoundingClientRect()

              setMenuPosition({
                top: rect.bottom + window.scrollY + 5,
                left: rect.left + window.scrollX,
              })
              setShowMenu(true)
              setSearchQuery('')
              setSelectedIndex(0)
            }
          }
        } else if (showMenu) {
          // Update search query
          const slashIndex = textContent.lastIndexOf('/', anchorOffset)
          if (slashIndex !== -1 && anchorOffset > slashIndex) {
            const query = textContent.slice(slashIndex + 1, anchorOffset)
            setSearchQuery(query)
            setSelectedIndex(0)
          } else {
            setShowMenu(false)
          }
        }
      })
    })

    return () => {
      updateListener()
    }
  }, [editor, showMenu])

  useEffect(() => {
    if (!showMenu) return

    const removeSlashAndQuery = () => {
      editor.update(() => {
        const selection = $getSelection()
        if ($isRangeSelection(selection)) {
          const anchorNode = selection.anchor.getNode()
          const textContent = anchorNode.getTextContent()
          const anchorOffset = selection.anchor.offset

          const slashIndex = textContent.lastIndexOf('/', anchorOffset)
          if (slashIndex !== -1) {
            // Remove the slash and query text
            if (anchorNode instanceof TextNode) {
              const beforeSlash = textContent.slice(0, slashIndex)
              const afterQuery = textContent.slice(anchorOffset)
              anchorNode.setTextContent(beforeSlash + afterQuery)

              // Move cursor to where the slash was
              selection.anchor.offset = slashIndex
              selection.focus.offset = slashIndex
            }
          }
        }
      })
    }

    const onKeyDown = editor.registerCommand(
      KEY_ARROW_DOWN_COMMAND,
      (event: KeyboardEvent) => {
        event.preventDefault()
        setSelectedIndex((prev) => (prev + 1) % filteredCommands.length)
        return true
      },
      COMMAND_PRIORITY_LOW
    )

    const onKeyUp = editor.registerCommand(
      KEY_ARROW_UP_COMMAND,
      (event: KeyboardEvent) => {
        event.preventDefault()
        setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % filteredCommands.length)
        return true
      },
      COMMAND_PRIORITY_LOW
    )

    const onEnter = editor.registerCommand(
      KEY_ENTER_COMMAND,
      (event: KeyboardEvent) => {
        if (filteredCommands[selectedIndex]) {
          event.preventDefault()
          removeSlashAndQuery()
          filteredCommands[selectedIndex].onSelect()
          setShowMenu(false)
          return true
        }
        return false
      },
      COMMAND_PRIORITY_LOW
    )

    const onEscape = editor.registerCommand(
      KEY_ESCAPE_COMMAND,
      () => {
        setShowMenu(false)
        return true
      },
      COMMAND_PRIORITY_LOW
    )

    return () => {
      onKeyDown()
      onKeyUp()
      onEnter()
      onEscape()
    }
  }, [editor, showMenu, selectedIndex, filteredCommands])

  if (!showMenu || filteredCommands.length === 0) return null

  return (
    <div
      className="fixed bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg shadow-xl py-2 z-50 min-w-[250px] max-h-[400px] overflow-y-auto"
      style={{
        top: `${menuPosition.top}px`,
        left: `${menuPosition.left}px`,
      }}
    >
      <div className="px-3 py-2 text-xs text-zinc-500 uppercase font-semibold border-b border-[var(--border-color)]">
        Blocks
      </div>
      {filteredCommands.map((command, index) => (
        <button
          key={command.id}
          onClick={() => {
            editor.update(() => {
              const selection = $getSelection()
              if ($isRangeSelection(selection)) {
                const anchorNode = selection.anchor.getNode()
                const textContent = anchorNode.getTextContent()
                const anchorOffset = selection.anchor.offset

                const slashIndex = textContent.lastIndexOf('/', anchorOffset)
                if (slashIndex !== -1 && anchorNode instanceof TextNode) {
                  const beforeSlash = textContent.slice(0, slashIndex)
                  const afterQuery = textContent.slice(anchorOffset)
                  anchorNode.setTextContent(beforeSlash + afterQuery)
                  selection.anchor.offset = slashIndex
                  selection.focus.offset = slashIndex
                }
              }
            })
            command.onSelect()
            setShowMenu(false)
          }}
          className={`w-full px-4 py-2 text-left flex items-center gap-3 transition-colors ${
            index === selectedIndex
              ? 'bg-[var(--bg-input)] text-[#F0FF3D]'
              : 'text-white hover:bg-[var(--bg-input)]'
          }`}
        >
          <span className="flex-shrink-0">{command.icon}</span>
          <span className="text-sm">{command.label}</span>
        </button>
      ))}
    </div>
  )
}
