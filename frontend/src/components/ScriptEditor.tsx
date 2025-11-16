import { useState, useRef, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, RotateCcw, Loader2, Wand2, AlertCircle, Check, GitBranch } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

interface ScriptEditorProps {
  scriptId: number
  initialContent: string
  currentVersion: number
  onClose: () => void
  onSave?: (content: string) => void
}

export default function ScriptEditor({ scriptId, initialContent, currentVersion, onClose, onSave }: ScriptEditorProps) {
  const { language } = useLanguage()
  const queryClient = useQueryClient()
  const [content, setContent] = useState(initialContent)
  const [hasChanges, setHasChanges] = useState(false)
  const [showAIAssistant, setShowAIAssistant] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    setHasChanges(content !== initialContent)
  }, [content, initialContent])

  const saveMutation = useMutation({
    mutationFn: async (newContent: string) => {
      const response = await fetch(`/api/v1/scripts/${scriptId}/content`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newContent }),
      })
      if (!response.ok) throw new Error('Failed to save')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['script', scriptId] })
      setHasChanges(false)
      if (onSave) onSave(content)
    },
  })

  const createVersionMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/v1/scripts/${scriptId}/versions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          change_description: language === 'ru' ? 'Ручное редактирование' : 'Manual editing',
          make_current: true,
        }),
      })
      if (!response.ok) throw new Error('Failed to create version')
      return response.json()
    },
    onSuccess: () => {
      saveMutation.mutate(content)
    },
  })

  const handleSave = async () => {
    await createVersionMutation.mutateAsync()
  }

  const handleReset = () => {
    setContent(initialContent)
    setHasChanges(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault()
      if (hasChanges) handleSave()
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-7xl max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {language === 'ru' ? 'Редактор сценария' : 'Script Editor'}
            </h2>
            <div className="flex items-center gap-2 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <GitBranch className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-blue-900 dark:text-blue-300">
                v{currentVersion}
              </span>
            </div>
            {hasChanges && (
              <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 rounded-lg text-sm font-medium">
                {language === 'ru' ? 'Несохраненные изменения' : 'Unsaved changes'}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAIAssistant(!showAIAssistant)}
              className="inline-flex items-center px-4 py-2 border border-purple-300 dark:border-purple-600 rounded-lg text-sm font-medium text-purple-700 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/30 hover:bg-purple-100 dark:hover:bg-purple-900/50 transition-all"
            >
              <Wand2 className="h-4 w-4 mr-2" />
              AI {language === 'ru' ? 'Ассистент' : 'Assistant'}
            </button>
            <button
              onClick={handleReset}
              disabled={!hasChanges}
              className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              {language === 'ru' ? 'Сбросить' : 'Reset'}
            </button>
            <button
              onClick={handleSave}
              disabled={!hasChanges || createVersionMutation.isPending || saveMutation.isPending}
              className="inline-flex items-center px-6 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createVersionMutation.isPending || saveMutation.isPending ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              {language === 'ru' ? 'Сохранить версию' : 'Save Version'}
            </button>
            <button
              onClick={onClose}
              className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all"
            >
              {language === 'ru' ? 'Закрыть' : 'Close'}
            </button>
          </div>
        </div>

        <div className="flex-1 flex overflow-hidden">
          <div className={`flex-1 flex flex-col ${showAIAssistant ? 'w-2/3' : 'w-full'} transition-all duration-300`}>
            <div className="flex-1 overflow-hidden">
              <textarea
                ref={textareaRef}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                onKeyDown={handleKeyDown}
                className="w-full h-full p-6 font-mono text-sm bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 border-none focus:ring-0 resize-none"
                placeholder={language === 'ru' ? 'Начните вводить текст сценария...' : 'Start typing your script...'}
                spellCheck={false}
              />
            </div>
            <div className="px-6 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <div className="flex items-center gap-4">
                  <span>{content.split('\n').length} {language === 'ru' ? 'строк' : 'lines'}</span>
                  <span>{content.split(/\s+/).filter(Boolean).length} {language === 'ru' ? 'слов' : 'words'}</span>
                  <span>{content.length} {language === 'ru' ? 'символов' : 'characters'}</span>
                </div>
                <div className="text-xs text-gray-400">
                  {language === 'ru' ? 'Ctrl+S для сохранения' : 'Ctrl+S to save'}
                </div>
              </div>
            </div>
          </div>

          {showAIAssistant && (
            <div className="w-1/3 border-l border-gray-200 dark:border-gray-700 bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 overflow-hidden">
              <AIAssistantPanel
                scriptId={scriptId}
                content={content}
                onApplyChange={(newContent) => setContent(newContent)}
                language={language}
              />
            </div>
          )}
        </div>

        {(createVersionMutation.isError || saveMutation.isError) && (
          <div className="px-6 py-3 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800">
            <div className="flex items-center text-red-800 dark:text-red-400">
              <AlertCircle className="h-4 w-4 mr-2" />
              <span className="text-sm">
                {language === 'ru' ? 'Ошибка сохранения' : 'Save error'}
              </span>
            </div>
          </div>
        )}

        {(createVersionMutation.isSuccess && saveMutation.isSuccess) && (
          <div className="px-6 py-3 bg-green-50 dark:bg-green-900/20 border-t border-green-200 dark:border-green-800">
            <div className="flex items-center text-green-800 dark:text-green-400">
              <Check className="h-4 w-4 mr-2" />
              <span className="text-sm">
                {language === 'ru' ? 'Новая версия сохранена успешно!' : 'New version saved successfully!'}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function AIAssistantPanel({ scriptId, content, onApplyChange, language }: {
  scriptId: number
  content: string
  onApplyChange: (newContent: string) => void
  language: string
}) {
  const [prompt, setPrompt] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [suggestion, setSuggestion] = useState('')
  const [streamingText, setStreamingText] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim()) return

    setIsProcessing(true)
    setSuggestion('')
    setStreamingText('')

    try {
      const response = await fetch(`/api/v1/scripts/${scriptId}/ai-suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          instruction: prompt,
        }),
      })

      if (!response.ok) throw new Error('AI request failed')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        let accumulatedText = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          accumulatedText += chunk

          setStreamingText(accumulatedText)

          await new Promise(resolve => setTimeout(resolve, 30))
        }

        setSuggestion(accumulatedText)
      }
    } catch (error) {
      console.error('AI Assistant error:', error)
    } finally {
      setIsProcessing(false)
      setStreamingText('')
    }
  }

  const handleApply = () => {
    if (suggestion) {
      onApplyChange(suggestion)
      setSuggestion('')
      setPrompt('')
    }
  }

  return (
    <div className="h-full flex flex-col p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-300 mb-2 flex items-center">
          <Wand2 className="h-5 w-5 mr-2" />
          {language === 'ru' ? 'AI Ассистент' : 'AI Assistant'}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {language === 'ru'
            ? 'Опишите желаемые изменения, и ИИ автоматически применит их к тексту'
            : 'Describe the changes you want, and AI will automatically apply them'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="mb-4">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={language === 'ru'
            ? 'Например: "Убери весь мат из диалогов" или "Смягчи сцены насилия"'
            : 'E.g., "Remove all profanity from dialogues" or "Tone down violence scenes"'}
          className="w-full px-4 py-3 rounded-lg border border-purple-200 dark:border-purple-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-600 resize-none"
          rows={4}
          disabled={isProcessing}
        />
        <button
          type="submit"
          disabled={!prompt.trim() || isProcessing}
          className="mt-3 w-full inline-flex items-center justify-center px-4 py-3 border border-transparent rounded-lg text-sm font-medium text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isProcessing ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              {language === 'ru' ? 'Обработка...' : 'Processing...'}
            </>
          ) : (
            <>
              <Wand2 className="h-4 w-4 mr-2" />
              {language === 'ru' ? 'Применить изменения' : 'Apply Changes'}
            </>
          )}
        </button>
      </form>

      {(isProcessing || streamingText || suggestion) && (
        <div className="flex-1 overflow-auto">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-purple-900 dark:text-purple-300">
                {language === 'ru' ? 'Предложение' : 'Suggestion'}
              </span>
              {isProcessing && (
                <div className="flex items-center text-purple-600 dark:text-purple-400">
                  <div className="animate-pulse flex space-x-1">
                    <div className="h-2 w-2 bg-purple-600 dark:bg-purple-400 rounded-full"></div>
                    <div className="h-2 w-2 bg-purple-600 dark:bg-purple-400 rounded-full animation-delay-200"></div>
                    <div className="h-2 w-2 bg-purple-600 dark:bg-purple-400 rounded-full animation-delay-400"></div>
                  </div>
                </div>
              )}
            </div>
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <pre className="whitespace-pre-wrap font-mono text-xs bg-gray-50 dark:bg-gray-900 p-3 rounded border border-gray-200 dark:border-gray-700">
                {streamingText || suggestion}
                {isProcessing && <span className="inline-block w-2 h-4 bg-purple-600 dark:bg-purple-400 animate-pulse ml-1"></span>}
              </pre>
            </div>
            {suggestion && !isProcessing && (
              <button
                onClick={handleApply}
                className="mt-4 w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 transition-all"
              >
                <Check className="h-4 w-4 mr-2" />
                {language === 'ru' ? 'Применить к сценарию' : 'Apply to Script'}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
