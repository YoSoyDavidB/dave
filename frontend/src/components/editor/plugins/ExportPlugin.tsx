import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useState } from 'react'
import { $getRoot } from 'lexical'
import { $convertToMarkdownString, TRANSFORMERS } from '@lexical/markdown'
import { Download, FileText, Copy, CheckCircle2 } from 'lucide-react'

export default function ExportPlugin() {
  const [editor] = useLexicalComposerContext()
  const [showMenu, setShowMenu] = useState(false)
  const [copied, setCopied] = useState(false)

  const getMarkdown = (): string => {
    let markdown = ''
    editor.getEditorState().read(() => {
      markdown = $convertToMarkdownString(TRANSFORMERS)
    })
    return markdown
  }

  const getPlainText = (): string => {
    let text = ''
    editor.getEditorState().read(() => {
      text = $getRoot().getTextContent()
    })
    return text
  }

  const getHTML = (): string => {
    let html = ''
    editor.getEditorState().read(() => {
      const root = $getRoot()
      // Simple HTML conversion - can be enhanced with proper HTML serialization
      html = root.getTextContent()
    })
    return html
  }

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }

  const handleExportMarkdown = () => {
    const markdown = getMarkdown()
    downloadFile(markdown, 'document.md', 'text/markdown')
    setShowMenu(false)
  }

  const handleExportText = () => {
    const text = getPlainText()
    downloadFile(text, 'document.txt', 'text/plain')
    setShowMenu(false)
  }

  const handleExportHTML = () => {
    const markdown = getMarkdown()
    // For proper HTML export, we'd use a markdown-to-html library
    // For now, just wrap in basic HTML structure
    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Document</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 800px;
      margin: 40px auto;
      padding: 20px;
      line-height: 1.6;
    }
    pre {
      background: #f4f4f4;
      padding: 15px;
      border-radius: 5px;
      overflow-x: auto;
    }
    code {
      background: #f4f4f4;
      padding: 2px 6px;
      border-radius: 3px;
    }
    blockquote {
      border-left: 4px solid #ddd;
      padding-left: 15px;
      color: #666;
    }
  </style>
</head>
<body>
  <pre>${markdown}</pre>
</body>
</html>`
    downloadFile(html, 'document.html', 'text/html')
    setShowMenu(false)
  }

  const handleCopyMarkdown = async () => {
    const markdown = getMarkdown()
    await copyToClipboard(markdown)
    setShowMenu(false)
  }

  const handleCopyPlainText = async () => {
    const text = getPlainText()
    await copyToClipboard(text)
    setShowMenu(false)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        className="p-2 rounded hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
        aria-label="Export"
        title="Export document"
      >
        <Download size={18} />
      </button>

      {showMenu && (
        <>
          {/* Backdrop to close menu */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowMenu(false)}
          />

          {/* Menu */}
          <div className="absolute top-full right-0 mt-2 bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg shadow-xl py-2 z-50 min-w-[220px]">
            {/* Export section */}
            <div className="px-2 py-1 text-xs text-zinc-500 uppercase font-semibold">
              Download
            </div>
            <button
              onClick={handleExportMarkdown}
              className="w-full px-4 py-2 text-left text-white hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
            >
              <FileText size={16} />
              Export as Markdown (.md)
            </button>
            <button
              onClick={handleExportText}
              className="w-full px-4 py-2 text-left text-white hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
            >
              <FileText size={16} />
              Export as Text (.txt)
            </button>
            <button
              onClick={handleExportHTML}
              className="w-full px-4 py-2 text-left text-white hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
            >
              <FileText size={16} />
              Export as HTML (.html)
            </button>

            <div className="border-t border-[var(--border-color)] my-2" />

            {/* Copy section */}
            <div className="px-2 py-1 text-xs text-zinc-500 uppercase font-semibold">
              Copy to Clipboard
            </div>
            <button
              onClick={handleCopyMarkdown}
              className="w-full px-4 py-2 text-left text-white hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
            >
              {copied ? (
                <>
                  <CheckCircle2 size={16} className="text-green-400" />
                  <span className="text-green-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy size={16} />
                  Copy as Markdown
                </>
              )}
            </button>
            <button
              onClick={handleCopyPlainText}
              className="w-full px-4 py-2 text-left text-white hover:bg-[var(--bg-input)] transition-colors flex items-center gap-2 text-sm"
            >
              <Copy size={16} />
              Copy as Plain Text
            </button>
          </div>
        </>
      )}
    </div>
  )
}
