import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { scriptsApi, WhatIfResponse } from '../api/client'
import { X, Sparkles, TrendingUp, TrendingDown, Minus, Lightbulb } from 'lucide-react'

interface WhatIfModalProps {
  scriptId: number
  currentRating: string | null
  onClose: () => void
}

const RATING_COLORS: Record<string, string> = {
  '0+': 'bg-green-100 text-green-800 border-green-300',
  '6+': 'bg-blue-100 text-blue-800 border-blue-300',
  '12+': 'bg-yellow-100 text-yellow-800 border-yellow-300',
  '16+': 'bg-orange-100 text-orange-800 border-orange-300',
  '18+': 'bg-red-100 text-red-800 border-red-300',
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

export default function WhatIfModal({ scriptId, currentRating, onClose }: WhatIfModalProps) {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<WhatIfResponse | null>(null)

  const whatIfMutation = useMutation({
    mutationFn: (modificationRequest: string) =>
      scriptsApi.whatIf(scriptId, modificationRequest),
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-5 flex justify-between items-center rounded-t-2xl">
          <div className="flex items-center gap-3">
            <Sparkles className="h-6 w-6" />
            <h2 className="text-2xl font-bold">What-If Rating Simulator</h2>
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
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="h-5 w-5 text-blue-600" />
                <span className="font-semibold text-blue-900">Current Rating</span>
              </div>
              <span className={`inline-flex items-center px-4 py-2 rounded-lg text-lg font-bold border-2 ${RATING_COLORS[currentRating]}`}>
                {currentRating}
              </span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="whatif-query" className="block text-sm font-semibold text-gray-700 mb-2">
                Describe your modification
              </label>
              <textarea
                id="whatif-query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Example: remove scene 12-13, replace fight with verbal conflict, remove all profanity..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows={3}
                disabled={whatIfMutation.isPending}
              />
            </div>

            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-medium text-gray-600 w-full mb-1">Quick examples:</span>
              {EXAMPLE_QUERIES.map((example, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleExampleClick(example)}
                  className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
                  disabled={whatIfMutation.isPending}
                >
                  {example}
                </button>
              ))}
            </div>

            <button
              type="submit"
              disabled={!query.trim() || whatIfMutation.isPending}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
            >
              <Sparkles className="h-5 w-5" />
              {whatIfMutation.isPending ? 'Simulating...' : 'Run Simulation'}
            </button>

            {whatIfMutation.error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">
                <p className="font-semibold">Error</p>
                <p className="text-sm">{(whatIfMutation.error as Error).message}</p>
              </div>
            )}
          </form>

          {result && (
            <div className="border-t-2 border-gray-200 pt-6 space-y-4 animate-in fade-in duration-500">
              <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-6 border border-purple-200">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  {getRatingChangeIcon()}
                  Rating Comparison
                </h3>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-2">Original</div>
                    <span className={`inline-flex items-center px-6 py-3 rounded-xl text-2xl font-bold border-2 ${RATING_COLORS[result.original_rating]}`}>
                      {result.original_rating}
                    </span>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-2">Modified</div>
                    <span className={`inline-flex items-center px-6 py-3 rounded-xl text-2xl font-bold border-2 ${RATING_COLORS[result.modified_rating]}`}>
                      {result.modified_rating}
                    </span>
                  </div>
                </div>

                {result.rating_changed && (
                  <div className={`text-center px-4 py-2 rounded-lg ${
                    result.modified_rating < result.original_rating
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    <span className="font-semibold">
                      {result.modified_rating < result.original_rating
                        ? '✓ Rating improved!'
                        : '✗ Rating increased'}
                    </span>
                  </div>
                )}
              </div>

              {result.changes_applied.length > 0 && (
                <div className="bg-blue-50 rounded-xl p-5 border border-blue-200">
                  <h4 className="font-semibold text-blue-900 mb-3">Applied Changes</h4>
                  <ul className="space-y-2">
                    {result.changes_applied.map((change, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-blue-800">
                        <span className="text-blue-600 mt-0.5">•</span>
                        <span>{change}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="bg-amber-50 rounded-xl p-5 border border-amber-200">
                <h4 className="font-semibold text-amber-900 mb-3 flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  Explanation
                </h4>
                <p className="text-sm text-amber-800 leading-relaxed">{result.explanation}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white rounded-xl p-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-700 mb-3 text-sm">Original Scores</h4>
                  <div className="space-y-2">
                    {Object.entries(result.original_scores).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-xs">
                        <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                        <span className="font-mono font-semibold">{(value * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white rounded-xl p-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-700 mb-3 text-sm">Modified Scores</h4>
                  <div className="space-y-2">
                    {Object.entries(result.modified_scores).map(([key, value]) => {
                      const originalValue = result.original_scores[key] || 0
                      const diff = value - originalValue
                      const diffColor = diff < 0 ? 'text-green-600' : diff > 0 ? 'text-red-600' : 'text-gray-600'

                      return (
                        <div key={key} className="flex justify-between text-xs">
                          <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-semibold">{(value * 100).toFixed(0)}%</span>
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
