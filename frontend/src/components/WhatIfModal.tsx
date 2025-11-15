import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { scriptsApi, WhatIfResponse, AdvancedWhatIfResponse, ModificationConfig } from '../api/client'
import { X, Sparkles, TrendingUp, TrendingDown, Minus, Lightbulb, Loader2 } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

interface WhatIfModalProps {
  scriptId: number
  scriptText: string
  currentRating: string | null
  onClose: () => void
}

const RATING_COLORS: Record<string, string> = {
  '0+': 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 border-green-300 dark:border-green-700',
  '6+': 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 border-blue-300 dark:border-blue-700',
  '12+': 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700',
  '16+': 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-400 border-orange-300 dark:border-orange-700',
  '18+': 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 border-red-300 dark:border-red-700',
}

const EXAMPLE_QUERIES = [
  'убрать сцену 1-3',
  'заменить драку на словесный конфликт',
  'убрать мат у всех персонажей',
  'без крови и увечий',
  'смягчить насилие',
  'remove scene 5',
  'replace fight with verbal argument',
  'remove all profanity',
]

const parseQueryToModifications = (query: string): ModificationConfig[] => {
  const mods: ModificationConfig[] = []
  const lower = query.toLowerCase()

  const sceneMatch = lower.match(/(?:убрать|удалить|remove|delete)\s+сцен[уыи]?\s+(\d+)(?:\s*[-–—]\s*(\d+))?/i)
  if (sceneMatch) {
    const start = parseInt(sceneMatch[1])
    const end = sceneMatch[2] ? parseInt(sceneMatch[2]) : start
    const sceneIds = Array.from({ length: end - start + 1 }, (_, i) => start + i)
    mods.push({ type: 'remove_scenes', params: { scene_ids: sceneIds } })
  }

  if (/(смягчить|убрать|reduce|remove).*(насилие|драк|бой|violence|fight)/i.test(lower)) {
    mods.push({ type: 'reduce_violence', params: { content_types: ['violence', 'gore'] } })
  }

  if (/(убрать|удалить|remove).*(мат|ненормативн|profanity|swear)/i.test(lower)) {
    mods.push({ type: 'reduce_profanity', params: { content_types: ['profanity'] } })
  }

  if (/(без|убрать|remove).*(кров|gore|blood)/i.test(lower)) {
    mods.push({ type: 'reduce_gore', params: { content_types: ['gore'] } })
  }

  if (/(без|убрать|remove).*(наркотик|drug)/i.test(lower)) {
    mods.push({ type: 'reduce_drugs', params: { content_types: ['drugs'] } })
  }

  if (/(без|убрать|remove).*(секс|sexual|nude)/i.test(lower)) {
    mods.push({ type: 'reduce_sexual', params: { content_types: ['sexual'] } })
  }

  return mods
}

export default function WhatIfModal({ scriptId, scriptText, currentRating, onClose }: WhatIfModalProps) {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<AdvancedWhatIfResponse | null>(null)
  const { t } = useLanguage()

  const whatIfMutation = useMutation({
    mutationFn: async (modificationRequest: string) => {
      const modifications = parseQueryToModifications(modificationRequest)
      if (modifications.length === 0) {
        throw new Error('Не удалось распознать модификации. Попробуйте другой запрос.')
      }
      return scriptsApi.whatIfAdvanced(scriptText, modifications)
    },
    onSuccess: (data) => {
      setResult(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      whatIfMutation.mutate(query)
    }
  }

  const handleExampleClick = (example: string) => {
    setQuery(example)
  }

  const getRatingChangeIcon = () => {
    if (!result) return null

    if (!result.rating_changed) {
      return <Minus className="h-6 w-6 text-gray-500" />
    }

    const ratings = ['0+', '6+', '12+', '16+', '18+']
    const originalIndex = ratings.indexOf(result.original_rating)
    const modifiedIndex = ratings.indexOf(result.modified_rating)

    if (modifiedIndex < originalIndex) {
      return <TrendingDown className="h-6 w-6 text-green-500" />
    } else if (modifiedIndex > originalIndex) {
      return <TrendingUp className="h-6 w-6 text-red-500" />
    }
    return <Minus className="h-6 w-6 text-gray-500" />
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
        <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-700 dark:to-indigo-700 text-white px-6 py-5 flex justify-between items-center rounded-t-2xl">
          <div className="flex items-center gap-3">
            <Sparkles className="h-6 w-6" />
            <h2 className="text-2xl font-bold">{t('whatif.title')}</h2>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {currentRating && (
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                <span className="font-semibold text-blue-900 dark:text-blue-300">{t('whatif.current_rating')}</span>
              </div>
              <span className={`inline-flex items-center px-4 py-2 rounded-lg text-lg font-bold border-2 ${RATING_COLORS[currentRating]}`}>
                {currentRating}
              </span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="whatif-query" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                {t('whatif.describe_modification')}
              </label>
              <textarea
                id="whatif-query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t('whatif.placeholder')}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white rounded-xl focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-600 focus:border-transparent resize-none transition-colors"
                rows={3}
                disabled={whatIfMutation.isPending}
              />
            </div>

            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400 w-full mb-1">{t('whatif.quick_examples')}</span>
              {EXAMPLE_QUERIES.map((example, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleExampleClick(example)}
                  className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-full transition-colors"
                  disabled={whatIfMutation.isPending}
                >
                  {example}
                </button>
              ))}
            </div>

            <button
              type="submit"
              disabled={!query.trim() || whatIfMutation.isPending}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
            >
              {whatIfMutation.isPending ? <Loader2 className="h-5 w-5 animate-spin" /> : <Sparkles className="h-5 w-5" />}
              {whatIfMutation.isPending ? t('whatif.simulating') : t('whatif.run_simulation')}
            </button>

            {whatIfMutation.error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 text-red-700 dark:text-red-400">
                <p className="font-semibold">{t('common.error')}</p>
                <p className="text-sm">{(whatIfMutation.error as Error).message}</p>
              </div>
            )}
          </form>

          {result && (
            <div className="border-t-2 border-gray-200 dark:border-gray-700 pt-6 space-y-4 animate-in fade-in duration-500">
              <div className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  {getRatingChangeIcon()}
                  {t('whatif.rating_comparison')}
                </h3>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">{t('whatif.original')}</div>
                    <span className={`inline-flex items-center px-6 py-3 rounded-xl text-2xl font-bold border-2 ${RATING_COLORS[result.original_rating]}`}>
                      {result.original_rating}
                    </span>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">{t('whatif.modified')}</div>
                    <span className={`inline-flex items-center px-6 py-3 rounded-xl text-2xl font-bold border-2 ${RATING_COLORS[result.modified_rating]}`}>
                      {result.modified_rating}
                    </span>
                  </div>
                </div>

                {result.rating_changed && (
                  <div className={`text-center px-4 py-2 rounded-lg ${
                    result.modified_rating < result.original_rating
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                      : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400'
                  }`}>
                    <span className="font-semibold">
                      {result.modified_rating < result.original_rating
                        ? t('whatif.rating_improved')
                        : t('whatif.rating_increased')}
                    </span>
                  </div>
                )}
              </div>

              {result.modifications_applied.length > 0 && (
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-5 border border-blue-200 dark:border-blue-800">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-300 mb-3">{t('whatif.applied_changes')}</h4>
                  <ul className="space-y-2">
                    {result.modifications_applied.map((mod, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-blue-800 dark:text-blue-300">
                        <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                        <div>
                          <div className="font-medium">{mod.type}</div>
                          {mod.metadata && (
                            <div className="text-xs text-blue-700 dark:text-blue-400 mt-1">
                              {Object.entries(mod.metadata).map(([key, val]) => (
                                <span key={key} className="mr-2">
                                  {key}: {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                                </span>
                              ))}
                            </div>
                          )}
                          {mod.error && (
                            <div className="text-xs text-red-600 dark:text-red-400 mt-1">Error: {mod.error}</div>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-5 border border-amber-200 dark:border-amber-800">
                <h4 className="font-semibold text-amber-900 dark:text-amber-300 mb-3 flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  {t('whatif.explanation')}
                </h4>
                <p className="text-sm text-amber-800 dark:text-amber-300 leading-relaxed">{result.explanation}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
                  <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3 text-sm">{t('whatif.original_scores')}</h4>
                  <div className="space-y-2">
                    {Object.entries(result.original_scores).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-xs">
                        <span className="text-gray-600 dark:text-gray-400 capitalize">{key.replace('_', ' ')}</span>
                        <span className="font-mono font-semibold text-gray-900 dark:text-white">{(value * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
                  <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3 text-sm">{t('whatif.modified_scores')}</h4>
                  <div className="space-y-2">
                    {Object.entries(result.modified_scores).map(([key, value]) => {
                      const originalValue = result.original_scores[key] || 0
                      const diff = value - originalValue
                      const diffColor = diff < 0 ? 'text-green-600 dark:text-green-400' : diff > 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-600 dark:text-gray-400'

                      return (
                        <div key={key} className="flex justify-between text-xs">
                          <span className="text-gray-600 dark:text-gray-400 capitalize">{key.replace('_', ' ')}</span>
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-semibold text-gray-900 dark:text-white">{(value * 100).toFixed(0)}%</span>
                            {Math.abs(diff) > 0.01 && (
                              <span className={`font-mono text-xs ${diffColor}`}>
                                {diff > 0 ? '+' : ''}{(diff * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
