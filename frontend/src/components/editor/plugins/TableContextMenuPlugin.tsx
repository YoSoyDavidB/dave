import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect, useState } from 'react'
import { $getSelection, $isRangeSelection } from 'lexical'
import {
  $getTableColumnIndexFromTableCellNode,
  $getTableRowIndexFromTableCellNode,
  $isTableCellNode,
  $isTableNode,
  $insertTableRow__EXPERIMENTAL,
  $insertTableColumn__EXPERIMENTAL,
  $deleteTableRow__EXPERIMENTAL,
  $deleteTableColumn__EXPERIMENTAL,
  $removeTableRowAtIndex,
  $removeTableColumnAtIndex,
  TableCellNode,
} from '@lexical/table'
import {
  RowsIcon,
  Columns3,
  Trash2,
  Plus,
} from 'lucide-react'

interface ContextMenuPosition {
  x: number
  y: number
}

export default function TableContextMenuPlugin() {
  const [editor] = useLexicalComposerContext()
  const [showMenu, setShowMenu] = useState(false)
  const [menuPosition, setMenuPosition] = useState<ContextMenuPosition>({ x: 0, y: 0 })
  const [selectedCell, setSelectedCell] = useState<TableCellNode | null>(null)

  useEffect(() => {
    const handleContextMenu = (event: MouseEvent) => {
      const target = event.target as HTMLElement

      // Check if the click is inside a table cell
      const tableCellElement = target.closest('td, th')
      if (!tableCellElement) {
        setShowMenu(false)
        return
      }

      event.preventDefault()

      // Get the cell node from the editor
      editor.update(() => {
        const selection = $getSelection()
        if ($isRangeSelection(selection)) {
          const anchorNode = selection.anchor.getNode()
          const cellNode = anchorNode.getParent()

          if ($isTableCellNode(cellNode)) {
            setSelectedCell(cellNode)
            setMenuPosition({ x: event.clientX, y: event.clientY })
            setShowMenu(true)
          }
        }
      })
    }

    const handleClick = (event: MouseEvent) => {
      // Close menu when clicking outside
      if (showMenu) {
        const menu = document.getElementById('table-context-menu')
        if (menu && !menu.contains(event.target as Node)) {
          setShowMenu(false)
        }
      }
    }

    document.addEventListener('contextmenu', handleContextMenu)
    document.addEventListener('click', handleClick)

    return () => {
      document.removeEventListener('contextmenu', handleContextMenu)
      document.removeEventListener('click', handleClick)
    }
  }, [editor, showMenu])

  const insertRowAbove = () => {
    editor.update(() => {
      if (selectedCell) {
        const tableNode = selectedCell.getParentOrThrow().getParentOrThrow()
        if ($isTableNode(tableNode)) {
          const rowIndex = $getTableRowIndexFromTableCellNode(selectedCell)
          $insertTableRow__EXPERIMENTAL(tableNode, rowIndex)
        }
      }
    })
    setShowMenu(false)
  }

  const insertRowBelow = () => {
    editor.update(() => {
      if (selectedCell) {
        const tableNode = selectedCell.getParentOrThrow().getParentOrThrow()
        if ($isTableNode(tableNode)) {
          const rowIndex = $getTableRowIndexFromTableCellNode(selectedCell)
          $insertTableRow__EXPERIMENTAL(tableNode, rowIndex + 1)
        }
      }
    })
    setShowMenu(false)
  }

  const insertColumnLeft = () => {
    editor.update(() => {
      if (selectedCell) {
        const tableNode = selectedCell.getParentOrThrow().getParentOrThrow()
        if ($isTableNode(tableNode)) {
          const columnIndex = $getTableColumnIndexFromTableCellNode(selectedCell)
          $insertTableColumn__EXPERIMENTAL(tableNode, columnIndex)
        }
      }
    })
    setShowMenu(false)
  }

  const insertColumnRight = () => {
    editor.update(() => {
      if (selectedCell) {
        const tableNode = selectedCell.getParentOrThrow().getParentOrThrow()
        if ($isTableNode(tableNode)) {
          const columnIndex = $getTableColumnIndexFromTableCellNode(selectedCell)
          $insertTableColumn__EXPERIMENTAL(tableNode, columnIndex + 1)
        }
      }
    })
    setShowMenu(false)
  }

  const deleteRow = () => {
    editor.update(() => {
      if (selectedCell) {
        const tableNode = selectedCell.getParentOrThrow().getParentOrThrow()
        if ($isTableNode(tableNode)) {
          const rowIndex = $getTableRowIndexFromTableCellNode(selectedCell)
          $deleteTableRow__EXPERIMENTAL(tableNode, rowIndex)
        }
      }
    })
    setShowMenu(false)
  }

  const deleteColumn = () => {
    editor.update(() => {
      if (selectedCell) {
        const tableNode = selectedCell.getParentOrThrow().getParentOrThrow()
        if ($isTableNode(tableNode)) {
          const columnIndex = $getTableColumnIndexFromTableCellNode(selectedCell)
          $deleteTableColumn__EXPERIMENTAL(tableNode, columnIndex)
        }
      }
    })
    setShowMenu(false)
  }

  if (!showMenu) return null

  return (
    <div
      id="table-context-menu"
      className="fixed bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg shadow-xl py-2 z-50 min-w-[200px]"
      style={{
        left: `${menuPosition.x}px`,
        top: `${menuPosition.y}px`,
      }}
    >
      {/* Row operations */}
      <div className="px-2 py-1 text-xs text-zinc-500 uppercase font-semibold">
        Row
      </div>
      <button
        onClick={insertRowAbove}
        className="w-full px-4 py-2 text-left text-white hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
      >
        <Plus size={16} />
        Insert Row Above
      </button>
      <button
        onClick={insertRowBelow}
        className="w-full px-4 py-2 text-left text-white hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
      >
        <Plus size={16} />
        Insert Row Below
      </button>
      <button
        onClick={deleteRow}
        className="w-full px-4 py-2 text-left text-red-400 hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
      >
        <Trash2 size={16} />
        Delete Row
      </button>

      <div className="border-t border-[var(--border-color)] my-2" />

      {/* Column operations */}
      <div className="px-2 py-1 text-xs text-zinc-500 uppercase font-semibold">
        Column
      </div>
      <button
        onClick={insertColumnLeft}
        className="w-full px-4 py-2 text-left text-white hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
      >
        <Plus size={16} />
        Insert Column Left
      </button>
      <button
        onClick={insertColumnRight}
        className="w-full px-4 py-2 text-left text-white hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
      >
        <Plus size={16} />
        Insert Column Right
      </button>
      <button
        onClick={deleteColumn}
        className="w-full px-4 py-2 text-left text-red-400 hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
      >
        <Trash2 size={16} />
        Delete Column
      </button>
    </div>
  )
}
