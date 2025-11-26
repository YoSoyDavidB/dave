import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Copy, Check, Database, Code as CodeIcon } from 'lucide-react'
import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchVault } from '../../services/api'

interface MarkdownMessageProps {
  content: string
  isStreaming?: boolean
}

// Process wiki-links [[note]] into clickable links
function processWikiLinks(content: string): string {
  // Replace [[note]] with a special marker that we can detect later
  return content.replace(/\[\[([^\]]+)\]\]/g, (match, noteName) => {
    // Use a special format that markdown will render as a link
    return `[📝 ${noteName}](wikilink://${noteName})`
  })
}

// Custom code block with copy button
function CodeBlock({ language, children }: { language: string; children: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(children)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Check if this is a Dataview block
  if (language === 'dataview' || language === 'dataviewjs') {
    const isJS = language === 'dataviewjs'
    return (
      <div className="my-4 border border-[#F0FF3D]/30 rounded-lg overflow-hidden bg-[#F0FF3D]/5">
        {/* Header */}
        <div className="px-4 py-2 bg-[#F0FF3D]/10 border-b border-[#F0FF3D]/30 flex items-center gap-2">
          {isJS ? (
            <CodeIcon size={16} className="text-[#F0FF3D]" />
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
            {children.trim()}
          </pre>
        </div>

        {/* Footer hint */}
        <div className="px-4 py-2 bg-[#12121c]/50 border-t border-white/[0.06] text-xs text-zinc-500">
          💡 This query will be executed when Dataview integration is fully implemented
        </div>
      </div>
    )
  }

  return (
    <div className="relative group my-3">
      {/* Language badge and copy button */}
      <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-3 py-1.5 bg-[#1a1a24] rounded-t-lg border-b border-white/[0.06]">
        <span className="text-xs text-zinc-500 font-mono">{language || 'code'}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-xs text-zinc-500 hover:text-[#F0FF3D] transition-colors"
        >
          {copied ? (
            <>
              <Check size={12} />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <Copy size={12} />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code content */}
      <SyntaxHighlighter
        language={language || 'text'}
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: '2.5rem 1rem 1rem 1rem',
          borderRadius: '0.5rem',
          fontSize: '0.8rem',
          background: '#12121c',
          border: '1px solid rgba(255, 255, 255, 0.06)',
        }}
        codeTagProps={{
          style: {
            fontFamily: 'JetBrains Mono, Fira Code, monospace',
          }
        }}
      >
        {children.trim()}
      </SyntaxHighlighter>
    </div>
  )
}

export default function MarkdownMessage({ content, isStreaming }: MarkdownMessageProps) {
  const navigate = useNavigate()

  // Process wiki-links in the content
  const processedContent = useMemo(() => processWikiLinks(content), [content])

  const handleWikiLinkClick = async (noteName: string, e: React.MouseEvent) => {
    e.preventDefault()

    try {
      const results = await searchVault(noteName)
      if (results.length > 0) {
        navigate(`/vault/editor?path=${encodeURIComponent(results[0].path)}`)
      } else {
        alert(`Note "${noteName}" not found`)
      }
    } catch (err) {
      console.error('Failed to find note:', err)
      alert(`Failed to find note "${noteName}"`)
    }
  }

  return (
    <div className="text-sm leading-relaxed">
      <ReactMarkdown
        components={{
          // Code blocks with syntax highlighting
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            const isInline = !match && !className

            if (isInline) {
              return (
                <code className="bg-[#F0FF3D]/10 text-[#F0FF3D] px-1.5 py-0.5 rounded text-xs font-mono" {...props}>
                  {children}
                </code>
              )
            }

            return (
              <CodeBlock language={match ? match[1] : ''}>
                {String(children).replace(/\n$/, '')}
              </CodeBlock>
            )
          },

          // Pre tag - let code handle it
          pre({ children }) {
            return <>{children}</>
          },

          // Bold text with accent color
          strong({ children }) {
            return <strong className="text-[#F0FF3D] font-semibold">{children}</strong>
          },

          // Italic
          em({ children }) {
            return <em className="text-zinc-300 italic">{children}</em>
          },

          // Paragraphs
          p({ children }) {
            return <p className="mb-3 last:mb-0">{children}</p>
          },

          // Unordered lists
          ul({ children }) {
            return <ul className="list-disc list-outside ml-4 mb-3 space-y-1">{children}</ul>
          },

          // Ordered lists
          ol({ children }) {
            return <ol className="list-decimal list-outside ml-4 mb-3 space-y-1">{children}</ol>
          },

          // List items
          li({ children }) {
            return <li className="text-zinc-200">{children}</li>
          },

          // Links
          a({ href, children }) {
            // Check if this is a wiki-link
            const isWikiLink = href?.startsWith('wikilink://')

            if (isWikiLink) {
              const noteName = href.replace('wikilink://', '')
              return (
                <span
                  onClick={(e) => handleWikiLinkClick(noteName, e)}
                  className="text-[#F0FF3D] hover:text-[#F0FF3D]/80 cursor-pointer hover:underline"
                  title={`Open ${noteName}`}
                >
                  {children}
                </span>
              )
            }

            return (
              <a
                href={href}
                className="text-[#F0FF3D] hover:text-[#F0FF3D]/80 underline underline-offset-2"
                target="_blank"
                rel="noopener noreferrer"
              >
                {children}
              </a>
            )
          },

          // Blockquotes
          blockquote({ children }) {
            return (
              <blockquote className="border-l-2 border-[#F0FF3D]/50 pl-3 my-3 text-zinc-400 italic">
                {children}
              </blockquote>
            )
          },

          // Horizontal rule
          hr() {
            return <hr className="border-t border-white/[0.08] my-4" />
          },

          // Headers
          h1({ children }) {
            return <h1 className="text-lg font-semibold text-white mt-4 mb-2">{children}</h1>
          },
          h2({ children }) {
            return <h2 className="text-base font-semibold text-white mt-3 mb-2">{children}</h2>
          },
          h3({ children }) {
            return <h3 className="text-sm font-semibold text-white mt-3 mb-1">{children}</h3>
          },
        }}
      >
        {processedContent}
      </ReactMarkdown>

      {/* Streaming cursor */}
      {isStreaming && (
        <span className="inline-block w-2 h-4 ml-0.5 bg-[#F0FF3D] animate-pulse align-middle" />
      )}
    </div>
  )
}
