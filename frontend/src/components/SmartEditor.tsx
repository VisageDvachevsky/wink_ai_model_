import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import {
  AlertCircle,
  Check,
  ChevronDown,
  ChevronUp,
  Edit3,
  Eye,
  EyeOff,
  Loader2,
  Save,
  X,
  Zap,
  SkipForward,
  ArrowLeft,
  ArrowRight,
} from 'lucide-react'

interface LineIssue {
  line_number: number
  line_text: string
  category: string
  matched_words: string[]
  match_count: number
  context_before: { line: number; text: string }[]
  context_after: { line: number; text: string }[]
  severity: number
  correction?: {
    type: 'false_positive' | 'false_negative'
    notes?: string
  }
}

interface SmartEditorProps {
  scriptId: number
  initialContent: string
  onSave: (content: string, description?: string) => Promise<void>
  onClose: () => void
}

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  profanity: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-800 dark:text-yellow-300', border: 'border-yellow-400 dark:border-yellow-600' },
  violence: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-800 dark:text-red-300', border: 'border-red-400 dark:border-red-600' },
  gore: { bg: 'bg-red-200 dark:bg-red-900/40', text: 'text-red-900 dark:text-red-200', border: 'border-red-500 dark:border-red-700' },
  drugs: { bg: 'bg-purple-100 dark:bg-purple-900/30', text: 'text-purple-800 dark:text-purple-300', border: 'border-purple-400 dark:border-purple-600' },
  sex_act: { bg: 'bg-pink-100 dark:bg-pink-900/30', text: 'text-pink-800 dark:text-pink-300', border: 'border-pink-400 dark:border-pink-600' },
  nudity: { bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-800 dark:text-orange-300', border: 'border-orange-400 dark:border-orange-600' },
  child_risk: { bg: 'bg-rose-200 dark:bg-rose-900/40', text: 'text-rose-900 dark:text-rose-200', border: 'border-rose-500 dark:border-rose-700' },
}

export default function SmartEditor({ scriptId, initialContent, onSave, onClose }: SmartEditorProps) {
  const { t } = useLanguage()
  const [content, setContent] = useState(initialContent)
  const [issues, setIssues] = useState<LineIssue[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [currentIssueIndex, setCurrentIssueIndex] = useState(0)
  const [showOnlyIssues, setShowOnlyIssues] = useState(false)
  const [corrections, setCorrections] = useState<Map<string, { type: string; notes?: string }>>(new Map())
  const editorRef = useRef<HTMLTextAreaElement>(null)
  const lineRefs = useRef<Map<number, HTMLDivElement>>(new Map())

  const detectIssues = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/v1/scripts/${scriptId}/detect-lines?context_lines=3`)
      if (!response.ok) throw new Error('Failed to detect issues')
      const data = await response.json()
      setIssues(data.issues || [])
    } catch (error) {
      console.error('Error detecting issues:', error)
    } finally {
      setLoading(false)
    }
  }, [scriptId])

  useEffect(() => {
    detectIssues()
  }, [detectIssues])

  const scrollToIssue = (index: number) => {
    if (issues[index]) {
      const lineNumber = issues[index].line_number
      const lineElement = lineRefs.current.get(lineNumber)
      if (lineElement) {
        lineElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
        lineElement.classList.add('ring-4', 'ring-blue-500', 'dark:ring-blue-400')
        setTimeout(() => {
          lineElement.classList.remove('ring-4', 'ring-blue-500', 'dark:ring-blue-400')
        }, 2000)
      }
    }
  }

  const markAsFalsePositive = async (issue: LineIssue) => {
    const key = `${issue.category}_${issue.line_number}`
    const newCorrections = new Map(corrections)
    newCorrections.set(key, { type: 'false_positive' })
    setCorrections(newCorrections)

    try {
      await fetch(`/api/v1/scripts/${scriptId}/corrections`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify([
          {
            issue_id: key,
            correction_type: 'false_positive',
            category: issue.category,
            line_number: issue.line_number,
          },
        ]),
      })
    } catch (error) {
      console.error('Error saving correction:', error)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await onSave(content, 'Manual edit via Smart Editor')
      await detectIssues()
    } finally {
      setSaving(false)
    }
  }

  const lines = content.split('\n')
  const issuesByLine = useMemo(() => {
    const map = new Map<number, LineIssue[]>()
    issues.forEach((issue) => {
      if (!map.has(issue.line_number)) {
        map.set(issue.line_number, [])
      }
      map.get(issue.line_number)!.push(issue)
    })
    return map
  }, [issues])

  const filteredLines = showOnlyIssues
    ? lines.map((line, idx) => ({
        line,
        lineNumber: idx + 1,
        hasIssue: issuesByLine.has(idx + 1),
      })).filter((l) => l.hasIssue)
    : lines.map((line, idx) => ({
        line,
        lineNumber: idx + 1,
        hasIssue: issuesByLine.has(idx + 1),
      }))

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-7xl h-[90vh] flex flex-col animate-fadeIn">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
          <div className="flex items-center gap-3">
            <Edit3 className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {t('editor.title') || 'Smart Editor'}
            </h2>
            {loading && <Loader2 className="h-5 w-5 animate-spin text-blue-600 dark:text-blue-400" />}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col border-r border-gray-200 dark:border-gray-700">
            <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {t('editor.issues_found') || 'Issues found'}: {issues.length}
                </span>
                {issues.length > 0 && (
                  <button
                    onClick={() => setShowOnlyIssues(!showOnlyIssues)}
                    className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                  >
                    {showOnlyIssues ? <Eye className="h-3 w-3 mr-1" /> : <EyeOff className="h-3 w-3 mr-1" />}
                    {showOnlyIssues ? t('editor.show_all') || 'Show All' : t('editor.show_issues_only') || 'Issues Only'}
                  </button>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                  {t('editor.save') || 'Save'}
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-auto font-mono text-sm">
              <div className="min-h-full bg-gray-50 dark:bg-gray-900">
                {filteredLines.map(({ line, lineNumber, hasIssue }) => {
                  const lineIssues = issuesByLine.get(lineNumber) || []
                  const highestSeverity = lineIssues.reduce((max, issue) => Math.max(max, issue.severity), 0)
                  const primaryCategory = lineIssues[0]?.category || 'profanity'
                  const colors = CATEGORY_COLORS[primaryCategory] || CATEGORY_COLORS.profanity

                  return (
                    <div
                      key={lineNumber}
                      ref={(el) => el && lineRefs.current.set(lineNumber, el)}
                      className={`flex transition-all ${
                        hasIssue
                          ? `${colors.bg} border-l-4 ${colors.border}`
                          : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                    >
                      <div className="w-16 flex-shrink-0 text-right pr-4 py-1 text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 border-r border-gray-300 dark:border-gray-700 select-none">
                        {lineNumber}
                      </div>
                      <div className="flex-1 px-4 py-1 whitespace-pre-wrap break-words">
                        {hasIssue ? (
                          <span className={`${colors.text} font-medium`}>{line}</span>
                        ) : (
                          <span className="text-gray-700 dark:text-gray-300">{line}</span>
                        )}
                        {hasIssue && lineIssues.length > 0 && (
                          <div className="mt-1 flex flex-wrap gap-1">
                            {lineIssues.map((issue, idx) => (
                              <span
                                key={idx}
                                className={`inline-flex items-center px-2 py-0.5 rounded text-xs ${
                                  CATEGORY_COLORS[issue.category].bg
                                } ${CATEGORY_COLORS[issue.category].text}`}
                              >
                                <Zap className="h-3 w-3 mr-1" />
                                {t(`category.${issue.category}`) || issue.category} ({issue.match_count})
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          <div className="w-96 flex flex-col bg-gray-50 dark:bg-gray-900">
            <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white flex items-center">
                <AlertCircle className="h-5 w-5 mr-2 text-purple-600 dark:text-purple-400" />
                {t('editor.assistant') || 'AI Assistant'}
              </h3>
            </div>

            {issues.length > 0 && (
              <div className="px-4 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {t('editor.issue') || 'Issue'} {currentIssueIndex + 1} / {issues.length}
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => {
                        const newIndex = (currentIssueIndex - 1 + issues.length) % issues.length
                        setCurrentIssueIndex(newIndex)
                        scrollToIssue(newIndex)
                      }}
                      className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                    >
                      <ArrowLeft className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    </button>
                    <button
                      onClick={() => {
                        const newIndex = (currentIssueIndex + 1) % issues.length
                        setCurrentIssueIndex(newIndex)
                        scrollToIssue(newIndex)
                      }}
                      className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                    >
                      <ArrowRight className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    </button>
                    <button
                      onClick={() => scrollToIssue(currentIssueIndex)}
                      className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                    >
                      <SkipForward className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="flex-1 overflow-auto">
              {issues.length === 0 ? (
                <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                  <Check className="h-12 w-12 mx-auto mb-3 text-green-500 dark:text-green-400" />
                  <p className="font-medium">{t('editor.no_issues') || 'No issues found!'}</p>
                  <p className="text-sm mt-1">{t('editor.script_clean') || 'Your script looks clean.'}</p>
                </div>
              ) : (
                <div className="p-4 space-y-4">
                  {issues[currentIssueIndex] && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg border-2 border-purple-200 dark:border-purple-700 p-4 shadow-lg animate-slideIn">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span
                            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${
                              CATEGORY_COLORS[issues[currentIssueIndex].category].bg
                            } ${CATEGORY_COLORS[issues[currentIssueIndex].category].text}`}
                          >
                            {t(`category.${issues[currentIssueIndex].category}`) || issues[currentIssueIndex].category}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {t('editor.line') || 'Line'} {issues[currentIssueIndex].line_number}
                          </span>
                        </div>
                        <span className="text-xs font-semibold text-red-600 dark:text-red-400">
                          {t('editor.severity') || 'Severity'}: {(issues[currentIssueIndex].severity * 100).toFixed(0)}%
                        </span>
                      </div>

                      <div className="mb-3">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">{t('editor.matched_words') || 'Matched'}:</p>
                        <div className="flex flex-wrap gap-1">
                          {issues[currentIssueIndex].matched_words.map((word, idx) => (
                            <span
                              key={idx}
                              className="inline-block px-2 py-1 rounded text-xs font-mono bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300"
                            >
                              {word}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="bg-gray-50 dark:bg-gray-900 rounded p-3 mb-3">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">{t('editor.context') || 'Context'}:</p>
                        <div className="space-y-1 font-mono text-xs">
                          {issues[currentIssueIndex].context_before.map((ctx) => (
                            <div key={ctx.line} className="text-gray-600 dark:text-gray-400">
                              <span className="text-gray-400 dark:text-gray-600 mr-2">{ctx.line}:</span>
                              {ctx.text}
                            </div>
                          ))}
                          <div className="text-gray-900 dark:text-white font-bold">
                            <span className="text-red-600 dark:text-red-400 mr-2">{issues[currentIssueIndex].line_number}:</span>
                            {issues[currentIssueIndex].line_text}
                          </div>
                          {issues[currentIssueIndex].context_after.map((ctx) => (
                            <div key={ctx.line} className="text-gray-600 dark:text-gray-400">
                              <span className="text-gray-400 dark:text-gray-600 mr-2">{ctx.line}:</span>
                              {ctx.text}
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <button
                          onClick={() => markAsFalsePositive(issues[currentIssueIndex])}
                          className="flex-1 inline-flex items-center justify-center px-3 py-2 rounded-lg text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                        >
                          <X className="h-3 w-3 mr-1" />
                          {t('editor.mark_false_positive') || 'False Positive'}
                        </button>
                        <button
                          onClick={() => scrollToIssue(currentIssueIndex)}
                          className="flex-1 inline-flex items-center justify-center px-3 py-2 rounded-lg text-xs font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
                        >
                          <Eye className="h-3 w-3 mr-1" />
                          {t('editor.jump_to_line') || 'Jump'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.2s ease-out;
        }
        .animate-slideIn {
          animation: slideIn 0.3s ease-out;
        }
      `}</style>
    </div>
  )
}
