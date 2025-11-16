import { useQuery } from '@tanstack/react-query'
import { AlertCircle, FileSearch, Loader2, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'

interface LineFinding {
  id: number
  line_start: number
  line_end: number
  category: string
  severity: number
  matched_text: string
  context_before: string | null
  context_after: string | null
  match_count: number
  rating_impact: string | null
}

interface LineFindingsResponse {
  total_findings: number
  by_category: Record<string, { count: number; total_matches: number; avg_severity: number }>
  findings: LineFinding[]
}

const CATEGORY_LABELS: Record<string, { ru: string; en: string }> = {
  profanity: { ru: 'Ненормативная лексика', en: 'Profanity' },
  violence: { ru: 'Насилие', en: 'Violence' },
  gore: { ru: 'Жестокость', en: 'Gore' },
  sex_act: { ru: 'Сексуальный контент', en: 'Sexual Content' },
  nudity: { ru: 'Нагота', en: 'Nudity' },
  drugs: { ru: 'Наркотики', en: 'Drugs' },
  child_risk: { ru: 'Риск для детей', en: 'Child Risk' },
}

const CATEGORY_COLORS: Record<string, string> = {
  profanity: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700',
  violence: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 border-red-300 dark:border-red-700',
  gore: 'bg-red-200 dark:bg-red-900/50 text-red-900 dark:text-red-300 border-red-400 dark:border-red-600',
  sex_act: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-400 border-orange-300 dark:border-orange-700',
  nudity: 'bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400 border-orange-200 dark:border-orange-700',
  drugs: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400 border-purple-300 dark:border-purple-700',
  child_risk: 'bg-red-200 dark:bg-red-900/50 text-red-900 dark:text-red-300 border-red-500 dark:border-red-600',
}

export default function LineFindingsPanel({ scriptId }: { scriptId: number }) {
  const { language } = useLanguage()
  const [expandedFinding, setExpandedFinding] = useState<number | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const { data, isLoading, error } = useQuery<LineFindingsResponse>({
    queryKey: ['line-findings', scriptId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/scripts/${scriptId}/line-findings`)
      if (!response.ok) throw new Error('Failed to fetch line findings')
      return response.json()
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600 dark:text-blue-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="h-8 w-8 text-red-500 dark:text-red-400 mx-auto mb-2" />
        <div className="text-red-600 dark:text-red-400 text-sm">{language === 'ru' ? 'Ошибка загрузки' : 'Failed to load'}</div>
      </div>
    )
  }

  if (!data || data.total_findings === 0) {
    return (
      <div className="text-center py-8">
        <FileSearch className="h-12 w-12 text-green-500 dark:text-green-400 mx-auto mb-2" />
        <div className="text-gray-600 dark:text-gray-400">{language === 'ru' ? 'Проблемные строки не найдены' : 'No problematic lines found'}</div>
      </div>
    )
  }

  const filteredFindings = selectedCategory
    ? data.findings.filter(f => f.category === selectedCategory)
    : data.findings

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
          <FileSearch className="h-5 w-5 mr-2" />
          {language === 'ru' ? 'Построчный анализ' : 'Line-by-Line Analysis'}
        </h3>
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {language === 'ru' ? 'Найдено' : 'Found'}: {data.total_findings}
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedCategory(null)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            selectedCategory === null
              ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 border border-blue-300 dark:border-blue-700'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-400 border border-gray-300 dark:border-gray-700 hover:bg-gray-200 dark:hover:bg-gray-700'
          }`}
        >
          {language === 'ru' ? 'Все' : 'All'} ({data.total_findings})
        </button>
        {Object.entries(data.by_category).map(([category, stats]) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              selectedCategory === category
                ? CATEGORY_COLORS[category]
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-400 border-gray-300 dark:border-gray-700 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            {CATEGORY_LABELS[category]?.[language] || category} ({stats.count})
          </button>
        ))}
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredFindings.map(finding => (
          <div
            key={finding.id}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded text-xs font-medium border ${CATEGORY_COLORS[finding.category]}`}>
                  {CATEGORY_LABELS[finding.category]?.[language] || finding.category}
                </span>
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  {language === 'ru' ? 'Строки' : 'Lines'} {finding.line_start}{finding.line_end !== finding.line_start && `-${finding.line_end}`}
                </span>
                {finding.match_count > 1 && (
                  <span className="text-xs font-medium text-red-600 dark:text-red-400">
                    {finding.match_count} {language === 'ru' ? 'совп.' : 'matches'}
                  </span>
                )}
                {finding.rating_impact && (
                  <span className="text-xs font-bold text-orange-600 dark:text-orange-400">
                    → {finding.rating_impact}
                  </span>
                )}
              </div>
              <button
                onClick={() => setExpandedFinding(expandedFinding === finding.id ? null : finding.id)}
                className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
              >
                {expandedFinding === finding.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>
            </div>

            <div className="text-sm text-gray-900 dark:text-gray-100 font-mono bg-gray-50 dark:bg-gray-900 p-2 rounded border border-gray-200 dark:border-gray-700">
              "{finding.matched_text}"
            </div>

            {expandedFinding === finding.id && (finding.context_before || finding.context_after) && (
              <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
                {finding.context_before && (
                  <div className="text-xs text-gray-500 dark:text-gray-500 font-mono">
                    <div className="font-semibold mb-1">{language === 'ru' ? 'Контекст до:' : 'Before:'}</div>
                    <div className="pl-2 border-l-2 border-gray-300 dark:border-gray-600">{finding.context_before}</div>
                  </div>
                )}
                {finding.context_after && (
                  <div className="text-xs text-gray-500 dark:text-gray-500 font-mono">
                    <div className="font-semibold mb-1">{language === 'ru' ? 'Контекст после:' : 'After:'}</div>
                    <div className="pl-2 border-l-2 border-gray-300 dark:border-gray-600">{finding.context_after}</div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
