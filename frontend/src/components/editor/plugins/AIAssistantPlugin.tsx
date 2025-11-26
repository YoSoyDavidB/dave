import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import { useEffect, useState } from 'react'
import { $getSelection, $isRangeSelection, KEY_MODIFIER_COMMAND } from 'lexical'
import { Sparkles, Loader2, X } from 'lucide-react'
import { sendMessageStream } from '../../../services/api'

interface AIAssistantPluginProps {
  conversationId?: string
  showButton?: boolean
}

type AssistantMode = 'improve' | 'fix-grammar' | 'make-shorter' | 'make-longer' | 'simplify' | 'custom'

export default function AIAssistantPlugin({ conversationId, showButton = false }: AIAssistantPluginProps) {
  const [editor] = useLexicalComposerContext()
  const [showModal, setShowModal] = useState(false)
  const [selectedText, setSelectedText] = useState('')
  const [mode, setMode] = useState<AssistantMode>('improve')
  const [customPrompt, setCustomPrompt] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [aiResponse, setAiResponse] = useState('')

  useEffect(() => {
    // Register with CRITICAL priority to ensure it runs before others
    return editor.registerCommand(
      KEY_MODIFIER_COMMAND,
      (event: KeyboardEvent) => {
        const { key, ctrlKey, metaKey } = event

        console.log('AI Assistant: Key pressed:', key, 'Meta:', metaKey, 'Ctrl:', ctrlKey)

        // Check for Cmd+K (Mac) or Ctrl+K (Windows/Linux)
        if (key === 'k' && (metaKey || ctrlKey)) {
          console.log('AI Assistant: Cmd+K detected!')
          event.preventDefault()
          event.stopPropagation()

          editor.getEditorState().read(() => {
            const selection = $getSelection()
            console.log('AI Assistant: Selection:', selection)
            if ($isRangeSelection(selection)) {
              const text = selection.getTextContent()
              console.log('AI Assistant: Selected text:', text)
              if (text) {
                setSelectedText(text)
                setShowModal(true)
              } else {
                console.log('AI Assistant: No text selected')
                // Show modal even without selection
                setSelectedText('')
                setShowModal(true)
              }
            }
          })

          return true
        }

        return false
      },
      4 // Use priority 4 (higher than COMMAND_PRIORITY_HIGH which is 3)
    )
  }, [editor])

  const getPromptForMode = (text: string, mode: AssistantMode, custom?: string): string => {
    switch (mode) {
      case 'improve':
        return `Improve the following text while maintaining its meaning and tone:\n\n${text}`
      case 'fix-grammar':
        return `Fix any grammar, spelling, and punctuation errors in the following text. Keep the same style and tone:\n\n${text}`
      case 'make-shorter':
        return `Make the following text more concise while keeping the key information:\n\n${text}`
      case 'make-longer':
        return `Expand the following text with more details and examples:\n\n${text}`
      case 'simplify':
        return `Simplify the following text to make it easier to understand:\n\n${text}`
      case 'custom':
        return `${custom}\n\nText:\n${text}`
      default:
        return text
    }
  }

  const handleProcess = async () => {
    setIsProcessing(true)
    setAiResponse('')

    const prompt = getPromptForMode(selectedText, mode, customPrompt)

    try {
      // Create a temporary conversation if none exists
      const tempConvId = conversationId || 'temp-editor-' + Date.now()

      await sendMessageStream(
        {
          messages: [
            {
              role: 'user',
              content: prompt,
            },
          ],
          conversation_id: tempConvId,
        },
        (event) => {
          if (event.type === 'content') {
            setAiResponse((prev) => prev + event.content)
          } else if (event.type === 'error') {
            setAiResponse('Error: ' + event.content)
            setIsProcessing(false)
          } else if (event.type === 'done') {
            setIsProcessing(false)
          }
        }
      )
    } catch (error) {
      console.error('AI Assistant error:', error)
      setIsProcessing(false)
      setAiResponse('Error processing request. Please try again.')
    }
  }

  const handleReplace = () => {
    editor.update(() => {
      const selection = $getSelection()
      if ($isRangeSelection(selection) && aiResponse) {
        selection.insertText(aiResponse)
      }
    })
    handleClose()
  }

  const handleClose = () => {
    setShowModal(false)
    setAiResponse('')
    setCustomPrompt('')
    setMode('improve')
  }

  const openAssistant = () => {
    editor.getEditorState().read(() => {
      const selection = $getSelection()
      if ($isRangeSelection(selection)) {
        const text = selection.getTextContent()
        setSelectedText(text || '')
        setShowModal(true)
      }
    })
  }

  // Listen for custom event from toolbar
  useEffect(() => {
    const handleEvent = () => {
      openAssistant()
    }
    window.addEventListener('open-ai-assistant', handleEvent)
    return () => {
      window.removeEventListener('open-ai-assistant', handleEvent)
    }
  }, [editor])

  return (
    <>
      {showButton && (
        <button
          onClick={openAssistant}
          className="p-2 rounded hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
          aria-label="AI Assistant"
          title="AI Assistant (Cmd+K)"
        >
          <Sparkles size={18} />
        </button>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <Sparkles size={20} className="text-[#F0FF3D]" />
                AI Writing Assistant
              </h3>
              <button
                onClick={handleClose}
                className="p-1 rounded hover:bg-[var(--bg-input)] text-zinc-400 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              {/* Selected text */}
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Selected Text</label>
                <div className="px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white text-sm max-h-32 overflow-y-auto">
                  {selectedText}
                </div>
              </div>

              {/* Mode selection */}
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Action</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'improve', label: 'Improve writing' },
                    { value: 'fix-grammar', label: 'Fix grammar' },
                    { value: 'make-shorter', label: 'Make shorter' },
                    { value: 'make-longer', label: 'Make longer' },
                    { value: 'simplify', label: 'Simplify' },
                    { value: 'custom', label: 'Custom prompt' },
                  ].map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setMode(option.value as AssistantMode)}
                      className={`px-3 py-2 rounded-lg text-sm transition-colors ${mode === option.value
                          ? 'bg-[#F0FF3D] text-black font-medium'
                          : 'bg-[var(--bg-input)] text-white hover:bg-[var(--bg-input)]/80'
                        }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Custom prompt */}
              {mode === 'custom' && (
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Custom Instructions</label>
                  <textarea
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder="E.g., Translate to Spanish, Make it more formal, Add examples..."
                    className="w-full px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#F0FF3D] h-20 resize-none"
                  />
                </div>
              )}

              {/* AI Response */}
              {(aiResponse || isProcessing) && (
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">
                    {isProcessing ? 'Processing...' : 'Suggestion'}
                  </label>
                  <div className="px-3 py-2 bg-[var(--bg-input)] border border-[var(--border-color)] rounded-lg text-white text-sm min-h-32 max-h-48 overflow-y-auto">
                    {aiResponse || (
                      <div className="flex items-center gap-2 text-zinc-400">
                        <Loader2 size={16} className="animate-spin" />
                        Thinking...
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3">
                <button
                  onClick={handleClose}
                  className="px-4 py-2 bg-[var(--bg-input)] hover:bg-[var(--bg-input)]/80 text-white rounded-lg transition-colors"
                >
                  Cancel
                </button>
                {!aiResponse && (
                  <button
                    onClick={handleProcess}
                    disabled={isProcessing || (mode === 'custom' && !customPrompt)}
                    className="px-4 py-2 bg-[#F0FF3D] hover:bg-[#F0FF3D]/90 text-black rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 size={18} className="animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Sparkles size={18} />
                        Generate
                      </>
                    )}
                  </button>
                )}
                {aiResponse && !isProcessing && (
                  <button
                    onClick={handleReplace}
                    className="px-4 py-2 bg-[#F0FF3D] hover:bg-[#F0FF3D]/90 text-black rounded-lg font-medium transition-colors"
                  >
                    Replace Text
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
