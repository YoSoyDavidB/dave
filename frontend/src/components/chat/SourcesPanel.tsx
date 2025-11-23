import { useState } from 'react'
import { ChevronDown, ChevronUp, Brain, FileText, Upload, ExternalLink } from 'lucide-react'
import { Source } from '../../services/api'

interface SourcesPanelProps {
  sources: Source[]
}

function getSourceIcon(type: Source['type']) {
  switch (type) {
    case 'memory':
      return <Brain size={14} className="text-purple-400" />
    case 'document':
      return <FileText size={14} className="text-blue-400" />
    case 'uploaded_doc':
      return <Upload size={14} className="text-green-400" />
  }
}

function getSourceLabel(type: Source['type']) {
  switch (type) {
    case 'memory':
      return 'Memory'
    case 'document':
      return 'Vault'
    case 'uploaded_doc':
      return 'Document'
  }
}

function getSourceBgColor(type: Source['type']) {
  switch (type) {
    case 'memory':
      return 'bg-purple-500/10 border-purple-500/20'
    case 'document':
      return 'bg-blue-500/10 border-blue-500/20'
    case 'uploaded_doc':
      return 'bg-green-500/10 border-green-500/20'
  }
}

export default function SourcesPanel({ sources }: SourcesPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!sources || sources.length === 0) {
    return null
  }

  // Group sources by type
  const groupedSources = sources.reduce((acc, source) => {
    if (!acc[source.type]) {
      acc[source.type] = []
    }
    acc[source.type].push(source)
    return acc
  }, {} as Record<Source['type'], Source[]>)

  const sourceTypes = Object.keys(groupedSources) as Source['type'][]

  return (
    <div className="mt-3 border-t border-white/[0.06] pt-3">
      {/* Toggle button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
      >
        <span className="flex items-center gap-1.5">
          {sourceTypes.map((type) => (
            <span key={type} className="flex items-center gap-1">
              {getSourceIcon(type)}
              <span>{groupedSources[type].length}</span>
            </span>
          ))}
        </span>
        <span className="text-zinc-600">|</span>
        <span>{sources.length} source{sources.length !== 1 ? 's' : ''} used</span>
        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {/* Expanded sources list */}
      {isExpanded && (
        <div className="mt-3 space-y-2">
          {sources.map((source, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border ${getSourceBgColor(source.type)} backdrop-blur-sm`}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getSourceIcon(source.type)}
                  <span className="text-xs font-medium text-zinc-300">
                    {getSourceLabel(source.type)}
                  </span>
                  {source.metadata?.category && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/[0.06] text-zinc-500">
                      {source.metadata.category}
                    </span>
                  )}
                  {source.metadata?.memory_type && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300">
                      {source.metadata.memory_type}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-zinc-600">
                    {Math.round(source.score * 100)}% match
                  </span>
                  {source.metadata?.path && (
                    <button
                      onClick={() => {
                        // Could navigate to vault or open file
                        console.log('Open:', source.metadata?.path)
                      }}
                      className="text-zinc-500 hover:text-[#F0FF3D] transition-colors"
                      title="View in vault"
                    >
                      <ExternalLink size={12} />
                    </button>
                  )}
                </div>
              </div>

              {/* Title */}
              <div className="text-sm font-medium text-zinc-200 mb-1">
                {source.title}
              </div>

              {/* Snippet */}
              <div className="text-xs text-zinc-500 line-clamp-2">
                {source.snippet}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
