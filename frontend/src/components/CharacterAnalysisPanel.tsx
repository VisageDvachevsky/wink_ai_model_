import { useQuery } from '@tanstack/react-query'
import { AlertCircle, Users, Loader2, TrendingUp, MessageSquare } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

interface CharacterAnalysis {
  id: number
  character_name: string
  profanity_count: number
  violence_scenes: number
  sex_scenes: number
  drug_scenes: number
  total_problematic_scenes: number
  severity_score: number
  recommendations: { items?: string[] } | null
  scene_appearances: Record<number, string[]> | null
}

interface CharacterAnalysisResponse {
  total_characters: number
  top_offenders: CharacterAnalysis[]
  all_characters: CharacterAnalysis[]
}

export default function CharacterAnalysisPanel({ scriptId }: { scriptId: number }) {
  const { language } = useLanguage()

  const { data, isLoading, error } = useQuery<CharacterAnalysisResponse>({
    queryKey: ['character-analysis', scriptId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/scripts/${scriptId}/character-analysis`)
      if (!response.ok) throw new Error('Failed to fetch character analysis')
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

  if (!data || data.total_characters === 0) {
    return (
      <div className="text-center py-8">
        <Users className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-2" />
        <div className="text-gray-600 dark:text-gray-400">{language === 'ru' ? 'Персонажи не найдены' : 'No characters found'}</div>
      </div>
    )
  }

  const getScoreColor = (score: number): string => {
    if (score >= 5) return 'text-red-600 dark:text-red-400'
    if (score >= 3) return 'text-orange-600 dark:text-orange-400'
    if (score >= 1) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-green-600 dark:text-green-400'
  }

  const getScoreBgColor = (score: number): string => {
    if (score >= 5) return 'bg-red-100 dark:bg-red-900/30'
    if (score >= 3) return 'bg-orange-100 dark:bg-orange-900/30'
    if (score >= 1) return 'bg-yellow-100 dark:bg-yellow-900/30'
    return 'bg-green-100 dark:bg-green-900/30'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
          <Users className="h-5 w-5 mr-2" />
          {language === 'ru' ? 'Анализ персонажей' : 'Character Analysis'}
        </h3>
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {language === 'ru' ? 'Всего' : 'Total'}: {data.total_characters}
        </span>
      </div>

      {data.top_offenders.length > 0 && (
        <div className="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
          <div className="flex items-center mb-2">
            <TrendingUp className="h-4 w-4 text-red-600 dark:text-red-400 mr-2" />
            <span className="text-sm font-semibold text-red-900 dark:text-red-300">
              {language === 'ru' ? 'Основные «виновники» рейтинга' : 'Top Rating Contributors'}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.top_offenders.slice(0, 5).map(char => (
              <div
                key={char.id}
                className={`${getScoreBgColor(char.severity_score)} rounded-lg p-3 border border-gray-200 dark:border-gray-700`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-gray-900 dark:text-white">{char.character_name}</span>
                  <span className={`text-sm font-bold ${getScoreColor(char.severity_score)}`}>
                    {char.severity_score.toFixed(1)}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-700 dark:text-gray-300">
                  {char.profanity_count > 0 && (
                    <div>
                      <span className="font-medium">{language === 'ru' ? 'Мат' : 'Profanity'}:</span> {char.profanity_count}
                    </div>
                  )}
                  {char.violence_scenes > 0 && (
                    <div>
                      <span className="font-medium">{language === 'ru' ? 'Насилие' : 'Violence'}:</span> {char.violence_scenes} {language === 'ru' ? 'сцен' : 'scenes'}
                    </div>
                  )}
                  {char.sex_scenes > 0 && (
                    <div>
                      <span className="font-medium">{language === 'ru' ? 'Секс' : 'Sex'}:</span> {char.sex_scenes} {language === 'ru' ? 'сцен' : 'scenes'}
                    </div>
                  )}
                  {char.drug_scenes > 0 && (
                    <div>
                      <span className="font-medium">{language === 'ru' ? 'Наркотики' : 'Drugs'}:</span> {char.drug_scenes} {language === 'ru' ? 'сцен' : 'scenes'}
                    </div>
                  )}
                </div>
                <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                  {language === 'ru' ? 'Проблемных сцен' : 'Problematic scenes'}: {char.total_problematic_scenes}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-3 max-h-96 overflow-y-auto">
        <div className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          {language === 'ru' ? 'Все персонажи' : 'All Characters'}
        </div>
        {data.all_characters.map(char => (
          <div
            key={char.id}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-800 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-900 dark:text-white text-lg">{char.character_name}</span>
                <span className={`px-2 py-1 rounded text-xs font-bold ${getScoreBgColor(char.severity_score)} ${getScoreColor(char.severity_score)}`}>
                  {char.severity_score.toFixed(1)}
                </span>
              </div>
              <span className="text-xs text-gray-600 dark:text-gray-400">
                {char.total_problematic_scenes} {language === 'ru' ? 'пробл. сцен' : 'prob. scenes'}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                <div className="text-sm">
                  <div className="text-gray-600 dark:text-gray-400 text-xs">{language === 'ru' ? 'Мат' : 'Profanity'}</div>
                  <div className="font-semibold text-gray-900 dark:text-white">{char.profanity_count}</div>
                </div>
              </div>
              <div className="text-sm">
                <div className="text-gray-600 dark:text-gray-400 text-xs">{language === 'ru' ? 'Насилие' : 'Violence'}</div>
                <div className="font-semibold text-gray-900 dark:text-white">{char.violence_scenes} {language === 'ru' ? 'сцен' : 'scenes'}</div>
              </div>
              <div className="text-sm">
                <div className="text-gray-600 dark:text-gray-400 text-xs">{language === 'ru' ? 'Секс' : 'Sex'}</div>
                <div className="font-semibold text-gray-900 dark:text-white">{char.sex_scenes} {language === 'ru' ? 'сцен' : 'scenes'}</div>
              </div>
              <div className="text-sm">
                <div className="text-gray-600 dark:text-gray-400 text-xs">{language === 'ru' ? 'Наркотики' : 'Drugs'}</div>
                <div className="font-semibold text-gray-900 dark:text-white">{char.drug_scenes} {language === 'ru' ? 'сцен' : 'scenes'}</div>
              </div>
            </div>

            {char.recommendations && char.recommendations.items && char.recommendations.items.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                  {language === 'ru' ? 'Рекомендации:' : 'Recommendations:'}
                </div>
                <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                  {char.recommendations.items.map((rec, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="mr-1">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {char.scene_appearances && Object.keys(char.scene_appearances).length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                <div className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                  {language === 'ru' ? 'Появления в сценах:' : 'Scene Appearances:'}
                </div>
                <div className="flex flex-wrap gap-1">
                  {Object.entries(char.scene_appearances).slice(0, 10).map(([sceneId, tags]) => (
                    <span
                      key={sceneId}
                      className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 rounded text-xs"
                      title={(tags as string[]).join(', ')}
                    >
                      #{sceneId}
                    </span>
                  ))}
                  {Object.keys(char.scene_appearances).length > 10 && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      +{Object.keys(char.scene_appearances).length - 10} {language === 'ru' ? 'ещё' : 'more'}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
