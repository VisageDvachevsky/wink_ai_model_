import React, { useState, useEffect, useRef } from 'react'
import { Save, RotateCcw, AlertCircle, Sparkles, Eye, EyeOff } from 'lucide-react'
import { LineDetection } from '../api/client'
import { useLanguage } from '../contexts/LanguageContext'

interface SmartEditorProps {
  scriptId: number
  initialContent: string
  detections: LineDetection[]
  onSave: (content: string) => Promise<void>
  onReanalyze?: () => Promise<void>
}

const CATEGORY_BG_COLORS: Record<string, string> = {
  violence: 'bg-red-200 dark:bg-red-900/60',
  gore: 'bg-red-300 dark:bg-red-900/70',
  profanity: 'bg-orange-200 dark:bg-orange-900/60',
  drugs: 'bg-purple-200 dark:bg-purple-900/60',
  sex_act: 'bg-pink-200 dark:bg-pink-900/60',
  nudity: 'bg-pink-100 dark:bg-pink-900/50',
  child_risk: 'bg-yellow-200 dark:bg-yellow-900/60',
}

const SmartEditor: React.FC<SmartEditorProps> = ({
  initialContent,
  detections,
  onSave,
  onReanalyze,
}) => {
  const { t } = useLanguage()
  const [content, setContent] = useState(initialContent)
  const [hasChanges, setHasChanges] = useState(false)
  const [saving, setSaving] = useState(false)
  const [showHighlights, setShowHighlights] = useState(true)
  const editorRef = useRef<HTMLTextAreaElement>(null)
  const highlightContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setContent(initialContent)
    setHasChanges(false)
  }, [initialContent])

  useEffect(() => {
    if (editorRef.current && highlightContainerRef.current) {
      highlightContainerRef.current.scrollTop = editorRef.current.scrollTop
    }
  }, [content])

  const handleContentChange = (newContent: string) => {
    setContent(newContent)
    setHasChanges(newContent !== initialContent)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await onSave(content)
      setHasChanges(false)
    } catch (error) {
      console.error('Failed to save:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setContent(initialContent)
    setHasChanges(false)
  }

  const renderHighlightedContent = () => {
    const lines = content.split('\n')
    const detectionMap = new Map<number, LineDetection[]>()

    detections.forEach(detection => {
      for (let i = detection.line_start; i <= detection.line_end; i++) {
        if (!detectionMap.has(i)) {
          detectionMap.set(i, [])
        }
        detectionMap.get(i)!.push(detection)
      }
    })

    return lines.map((line, index) => {
      const lineNum = index + 1
      const lineDetections = detectionMap.get(lineNum) || []

      let bgClass = ''
      let borderClass = ''

      if (lineDetections.length > 0 && showHighlights) {
        const highestSeverity = Math.max(...lineDetections.map(d => d.severity))
        const primaryCategory = lineDetections[0].category

        bgClass = CATEGORY_BG_COLORS[primaryCategory] || 'bg-gray-200 dark:bg-gray-800'

        if (highestSeverity >= 0.7) {
          borderClass = 'border-l-4 border-red-500'
        } else if (highestSeverity >= 0.4) {
          borderClass = 'border-l-4 border-orange-500'
        } else {
          borderClass = 'border-l-4 border-yellow-500'
        }
      }

      return (
        <div
          key={lineNum}
          className={`min-h-[24px] px-2 ${bgClass} ${borderClass} transition-all duration-200`}
          style={{ lineHeight: '24px', color: 'transparent' }}
        >
          {line || ' '}
        </div>
      )
    })
  }

  const handleScroll = () => {
    if (editorRef.current && highlightContainerRef.current) {
      highlightContainerRef.current.scrollTop = editorRef.current.scrollTop
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          {t('editor.title')}
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowHighlights(!showHighlights)}
            className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            title={showHighlights ? t('editor.hideHighlights') : t('editor.showHighlights')}
          >
            {showHighlights ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
          </button>
          <button
            onClick={handleReset}
            disabled={!hasChanges}
            className="px-3 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            {t('editor.reset')}
          </button>
          <button
            onClick={handleSave}
            disabled={!hasChanges || saving}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {saving ? t('editor.saving') : t('editor.save')}
          </button>
          {onReanalyze && (
            <button
              onClick={onReanalyze}
              className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              <AlertCircle className="w-4 h-4" />
              {t('editor.reanalyze')}
            </button>
          )}
        </div>
      </div>

      {hasChanges && (
        <div className="p-3 bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {t('editor.unsavedChanges')}
        </div>
      )}

      <div className="relative border border-gray-300 dark:border-gray-700 rounded-lg overflow-hidden bg-white dark:bg-gray-900">
        <div className="absolute inset-0 pointer-events-none overflow-hidden" ref={highlightContainerRef}>
          <div className="font-mono text-sm p-4 whitespace-pre-wrap break-words">
            {renderHighlightedContent()}
          </div>
        </div>

        <textarea
          ref={editorRef}
          value={content}
          onChange={(e) => handleContentChange(e.target.value)}
          onScroll={handleScroll}
          className="w-full h-[600px] p-4 font-mono text-sm bg-transparent relative z-10 resize-none focus:outline-none text-gray-900 dark:text-gray-100 caret-blue-600"
          style={{
            caretColor: '#2563eb',
            background: 'transparent',
          }}
          spellCheck={false}
        />
      </div>

      <div className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-4">
        <span>{content.split('\n').length} {t('editor.lines')}</span>
        <span>{content.length} {t('editor.characters')}</span>
        {detections.length > 0 && (
          <span className="text-orange-600 dark:text-orange-400">
            {detections.length} {t('editor.issues')}
          </span>
        )}
      </div>
    </div>
  )
}

export default SmartEditor
