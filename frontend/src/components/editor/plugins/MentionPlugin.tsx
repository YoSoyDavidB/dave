import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect, useState, useCallback } from 'react'
import {
  $getSelection,
  $isRangeSelection,
  TextNode,
  COMMAND_PRIORITY_LOW,
  KEY_ARROW_DOWN_COMMAND,
  KEY_ARROW_UP_COMMAND,
  KEY_ENTER_COMMAND,
  KEY_ESCAPE_COMMAND,
} from 'lexical'
import { FileText } from 'lucide-react'
import { searchVault } from '../../../services/api'

interface MentionSuggestion {
  name: string
  path: string
  type: 'file' | 'dir'
}

export default function MentionPlugin() {
  const [editor] = useLexicalComposerContext()
  const [showMenu, setShowMenu] = useState(false)
  const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0 })
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [suggestions, setSuggestions] = useState<MentionSuggestion[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // Fetch vault files when search query changes
  useEffect(() => {
    if (!showMenu) {
      setSuggestions([])
      return
    }

    // Show all files when empty query (or at least some popular ones)
    if (searchQuery.length === 0) {
      return
    }

    const fetchSuggestions = async () => {
      setIsLoading(true)
      try {
        const results = await searchVault(searchQuery)
        console.log('Search results:', results)

        // searchVault returns items with name and path (no type field)
        // All results from searchVault are files
        const files = results
          .slice(0, 10)
          .map((item) => ({
            name: item.name.replace('.md', ''),
            path: item.path,
            type: 'file' as const,
          }))

        console.log('Processed files:', files)
        setSuggestions(files)
      } catch (error) {
        console.error('Failed to search vault:', error)
        setSuggestions([])
      } finally {
        setIsLoading(false)
      }
    }

    const debounceTimer = setTimeout(fetchSuggestions, 200)
    return () => clearTimeout(debounceTimer)
  }, [searchQuery, showMenu])

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

        // Check if we just typed "@"
        if (textContent[anchorOffset - 1] === '@' && anchorOffset > 0) {
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
        } else if (showMenu) {
          // Update search query
          const atIndex = textContent.lastIndexOf('@', anchorOffset)
          if (atIndex !== -1 && anchorOffset > atIndex) {
            const query = textContent.slice(atIndex + 1, anchorOffset)
            // Close menu if there's a space after @
            if (query.includes(' ')) {
              setShowMenu(false)
            } else {
              setSearchQuery(query)
              setSelectedIndex(0)
            }
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

  const insertMention = useCallback(
    (suggestion: MentionSuggestion) => {
      editor.update(() => {
        const selection = $getSelection()
        if ($isRangeSelection(selection)) {
          const anchorNode = selection.anchor.getNode()
          const textContent = anchorNode.getTextContent()
          const anchorOffset = selection.anchor.offset

          const atIndex = textContent.lastIndexOf('@', anchorOffset)
          if (atIndex !== -1 && anchorNode instanceof TextNode) {
            // Create a markdown link: [[note name]]
            const beforeAt = textContent.slice(0, atIndex)
            const afterQuery = textContent.slice(anchorOffset)
            const mentionText = `[[${suggestion.name}]]`

            anchorNode.setTextContent(beforeAt + mentionText + afterQuery)

            // Move cursor after the mention
            const newOffset = atIndex + mentionText.length
            selection.anchor.offset = newOffset
            selection.focus.offset = newOffset
          }
        }
      })
      setShowMenu(false)
    },
    [editor]
  )

  useEffect(() => {
    if (!showMenu) return

    const onKeyDown = editor.registerCommand(
      KEY_ARROW_DOWN_COMMAND,
      (event: KeyboardEvent) => {
        if (suggestions.length > 0) {
          event.preventDefault()
          setSelectedIndex((prev) => (prev + 1) % suggestions.length)
          return true
        }
        return false
      },
      COMMAND_PRIORITY_LOW
    )

    const onKeyUp = editor.registerCommand(
      KEY_ARROW_UP_COMMAND,
      (event: KeyboardEvent) => {
        if (suggestions.length > 0) {
          event.preventDefault()
          setSelectedIndex((prev) => (prev - 1 + suggestions.length) % suggestions.length)
          return true
        }
        return false
      },
      COMMAND_PRIORITY_LOW
    )

    const onEnter = editor.registerCommand(
      KEY_ENTER_COMMAND,
      (event: KeyboardEvent) => {
        if (suggestions.length > 0 && suggestions[selectedIndex]) {
          event.preventDefault()
          insertMention(suggestions[selectedIndex])
          return true
        }
        return false
      },
      COMMAND_PRIORITY_LOW
    )

    const onEscape = editor.registerCommand(
      KEY_ESCAPE_COMMAND,
      () => {
        if (showMenu) {
          setShowMenu(false)
          return true
        }
        return false
      },
      COMMAND_PRIORITY_LOW
    )

    return () => {
      onKeyDown()
      onKeyUp()
      onEnter()
      onEscape()
    }
  }, [editor, showMenu, selectedIndex, suggestions, insertMention])

  if (!showMenu) return null

  return (
    <div
      className="fixed bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg shadow-xl py-2 z-50 min-w-[300px] max-h-[300px] overflow-y-auto"
      style={{
        top: `${menuPosition.top}px`,
        left: `${menuPosition.left}px`,
      }}
    >
      <div className="px-3 py-2 text-xs text-zinc-500 uppercase font-semibold border-b border-[var(--border-color)]">
        Link to Note
      </div>

      {isLoading && (
        <div className="px-4 py-3 text-sm text-zinc-400">Searching...</div>
      )}

      {!isLoading && suggestions.length === 0 && searchQuery.length > 0 && (
        <div className="px-4 py-3 text-sm text-zinc-400">
          No notes found for "{searchQuery}"
        </div>
      )}

      {!isLoading && suggestions.length === 0 && searchQuery.length === 0 && (
        <div className="px-4 py-3 text-sm text-zinc-400">
          Type to search notes...
        </div>
      )}

      {!isLoading && suggestions.length > 0 && (
        <>
          {suggestions.map((suggestion, index) => (
            <button
              key={suggestion.path}
              onClick={() => insertMention(suggestion)}
              className={`w-full px-4 py-2 text-left flex items-center gap-3 transition-colors ${
                index === selectedIndex
                  ? 'bg-[var(--bg-input)] text-[#F0FF3D]'
                  : 'text-white hover:bg-[var(--bg-input)]'
              }`}
            >
              <FileText size={16} className="flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{suggestion.name}</div>
                <div className="text-xs text-zinc-500 truncate">{suggestion.path}</div>
              </div>
            </button>
          ))}
        </>
      )}
    </div>
  )
}
