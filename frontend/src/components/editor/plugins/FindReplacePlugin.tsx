import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect, useState } from 'react'
import {
  $getRoot,
  $getSelection,
  $isRangeSelection,
  $isTextNode,
  TextNode,
  COMMAND_PRIORITY_LOW,
  KEY_ESCAPE_COMMAND,
} from 'lexical'
import { X, Search, Replace, ChevronUp, ChevronDown } from 'lucide-react'

interface Match {
  node: TextNode
  offset: number
  length: number
}

export default function FindReplacePlugin() {
  const [editor] = useLexicalComposerContext()
  const [showDialog, setShowDialog] = useState(false)
  const [findText, setFindText] = useState('')
  const [replaceText, setReplaceText] = useState('')
  const [matches, setMatches] = useState<Match[]>([])
  const [currentMatchIndex, setCurrentMatchIndex] = useState(-1)
  const [caseSensitive, setCaseSensitive] = useState(false)

  // Register Cmd+F keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'f') {
        event.preventDefault()
        setShowDialog(true)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Register Escape to close
  useEffect(() => {
    if (!showDialog) return

    return editor.registerCommand(
      KEY_ESCAPE_COMMAND,
      () => {
        setShowDialog(false)
        return true
      },
      COMMAND_PRIORITY_LOW
    )
  }, [editor, showDialog])

  // Find all matches
  useEffect(() => {
    if (!findText) {
      setMatches([])
      setCurrentMatchIndex(-1)
      return
    }

    editor.getEditorState().read(() => {
      const root = $getRoot()
      const allMatches: Match[] = []

      const searchText = caseSensitive ? findText : findText.toLowerCase()

      function traverse(node: LexicalNode) {
        if ($isTextNode(node)) {
          const text = node.getTextContent()
          const searchIn = caseSensitive ? text : text.toLowerCase()

          let offset = 0
          while (offset < searchIn.length) {
            const index = searchIn.indexOf(searchText, offset)
            if (index === -1) break

            allMatches.push({
              node: node as TextNode,
              offset: index,
              length: findText.length,
            })

            offset = index + 1
          }
        }

        const children = node.getChildren()
        for (const child of children) {
          traverse(child)
        }
      }

      traverse(root)
      setMatches(allMatches)
      setCurrentMatchIndex(allMatches.length > 0 ? 0 : -1)
    })
  }, [findText, caseSensitive, editor])

  const goToMatch = (index: number) => {
    if (index < 0 || index >= matches.length) return

    const match = matches[index]
    editor.update(() => {
      const selection = $getSelection()
      if ($isRangeSelection(selection)) {
        selection.focus.set(match.node.getKey(), match.offset + match.length, 'text')
        selection.anchor.set(match.node.getKey(), match.offset, 'text')
      }
    })
    setCurrentMatchIndex(index)
  }

  const handleNext = () => {
    if (matches.length === 0) return
    const nextIndex = (currentMatchIndex + 1) % matches.length
    goToMatch(nextIndex)
  }

  const handlePrevious = () => {
    if (matches.length === 0) return
    const prevIndex = (currentMatchIndex - 1 + matches.length) % matches.length
    goToMatch(prevIndex)
  }

  const handleReplaceCurrent = () => {
    if (currentMatchIndex < 0 || currentMatchIndex >= matches.length) return

    const match = matches[currentMatchIndex]
    editor.update(() => {
      const textContent = match.node.getTextContent()
      const before = textContent.slice(0, match.offset)
      const after = textContent.slice(match.offset + match.length)
      match.node.setTextContent(before + replaceText + after)
    })

    // Update matches after replacement
    setTimeout(() => {
      setFindText(findText) // Trigger re-search
    }, 100)
  }

  const handleReplaceAll = () => {
    editor.update(() => {
      // Process matches in reverse order to maintain offsets
      const sortedMatches = [...matches].reverse()

      for (const match of sortedMatches) {
        const textContent = match.node.getTextContent()
        const before = textContent.slice(0, match.offset)
        const after = textContent.slice(match.offset + match.length)
        match.node.setTextContent(before + replaceText + after)
      }
    })

    // Update matches after replacement
    setTimeout(() => {
      setFindText(findText) // Trigger re-search
    }, 100)
  }

  if (!showDialog) return null

  return (
    <div className="fixed top-20 right-6 bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg shadow-xl p-4 z-50 w-full max-w-md">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Search size={16} />
          Find & Replace
        </h3>
        <button
          onClick={() => setShowDialog(false)}
          className="p-1 rounded hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
        >
          <X size={16} />
        </button>
      </div>

      <div className="space-y-3">
        {/* Find input */}
        <div>
          <div className="relative">
            <input
              type="text"
              value={findText}
              onChange={(e) => setFindText(e.target.value)}
              placeholder="Find..."
              className="w-full px-3 py-2 pr-24 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#F0FF3D] text-sm"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  if (e.shiftKey) {
                    handlePrevious()
                  } else {
                    handleNext()
                  }
                }
              }}
            />
            {matches.length > 0 && (
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                <span className="text-xs text-zinc-400 mr-1">
                  {currentMatchIndex + 1}/{matches.length}
                </span>
                <button
                  onClick={handlePrevious}
                  className="p-1 rounded hover:bg-[var(--bg-sidebar)] text-zinc-400 hover:text-white transition-colors"
                  title="Previous (Shift+Enter)"
                >
                  <ChevronUp size={14} />
                </button>
                <button
                  onClick={handleNext}
                  className="p-1 rounded hover:bg-[var(--bg-sidebar)] text-zinc-400 hover:text-white transition-colors"
                  title="Next (Enter)"
                >
                  <ChevronDown size={14} />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Replace input */}
        <div>
          <input
            type="text"
            value={replaceText}
            onChange={(e) => setReplaceText(e.target.value)}
            placeholder="Replace with..."
            className="w-full px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#F0FF3D] text-sm"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                handleReplaceCurrent()
              }
            }}
          />
        </div>

        {/* Options */}
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-zinc-400 cursor-pointer">
            <input
              type="checkbox"
              checked={caseSensitive}
              onChange={(e) => setCaseSensitive(e.target.checked)}
              className="rounded border-zinc-600 bg-[var(--bg-input)] text-[#F0FF3D] focus:ring-2 focus:ring-[#F0FF3D]"
            />
            Case sensitive
          </label>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={handleReplaceCurrent}
            disabled={currentMatchIndex < 0}
            className="flex-1 px-3 py-2 bg-[var(--bg-input)] hover:bg-[var(--bg-input)]/80 text-white rounded-lg transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Replace size={14} />
            Replace
          </button>
          <button
            onClick={handleReplaceAll}
            disabled={matches.length === 0}
            className="flex-1 px-3 py-2 bg-[#F0FF3D] hover:bg-[#F0FF3D]/90 text-black rounded-lg transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Replace size={14} />
            Replace All
          </button>
        </div>
      </div>
    </div>
  )
}
