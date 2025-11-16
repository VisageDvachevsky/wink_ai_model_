import { Scene } from '../api/client'
import { useLanguage } from '../contexts/LanguageContext'

interface SceneHeatmapProps {
  scenes: Scene[]
}

const CATEGORIES = [
  { key: 'violence', labelKey: 'category.violence' },
  { key: 'gore', labelKey: 'category.gore' },
  { key: 'sex_act', labelKey: 'category.sexual' },
  { key: 'nudity', labelKey: 'category.nudity' },
  { key: 'profanity', labelKey: 'category.profanity' },
  { key: 'drugs', labelKey: 'category.drugs' },
  { key: 'child_risk', labelKey: 'category.child_risk' },
]

export default function SceneHeatmap({ scenes }: SceneHeatmapProps) {
  const { t } = useLanguage()

  const getColor = (value: number) => {
    if (value > 0.7) return 'bg-red-600 dark:bg-red-700'
    if (value > 0.5) return 'bg-orange-500 dark:bg-orange-600'
    if (value > 0.3) return 'bg-yellow-400 dark:bg-yellow-500'
    if (value > 0.1) return 'bg-blue-400 dark:bg-blue-500'
    return 'bg-gray-200 dark:bg-gray-700'
  }

  const maxScenesPerRow = 20

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-lg">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
        {t('heatmap.title')}
      </h3>

      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {CATEGORIES.map((category) => (
            <div key={category.key} className="mb-3 last:mb-0">
              <div className="flex items-center gap-3">
                <div className="w-28 text-sm font-medium text-gray-700 dark:text-gray-300">
                  {t(category.labelKey)}
                </div>
                <div className="flex gap-1">
                  {scenes.slice(0, maxScenesPerRow).map((scene) => {
                    const value = scene[category.key as keyof Scene] as number
                    const colorClass = getColor(value)

                    return (
                      <div
                        key={`${scene.id}-${category.key}`}
                        className={`w-7 h-7 ${colorClass} hover:ring-2 hover:ring-indigo-500 dark:hover:ring-indigo-400 rounded transition-all cursor-pointer hover:scale-110`}
                        title={`Scene ${scene.scene_id}: ${t(category.labelKey)} = ${(value * 100).toFixed(0)}%`}
                      />
                    )
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 flex items-center gap-4 text-xs bg-gray-50 dark:bg-gray-900/50 p-4 rounded-lg">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="font-semibold text-gray-700 dark:text-gray-300">{t('heatmap.legend')}</span>
          <div className="flex items-center gap-1.5">
            <div className="w-5 h-5 bg-gray-200 dark:bg-gray-700 rounded shadow-sm"></div>
            <span className="text-gray-600 dark:text-gray-400 font-medium">0-10%</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-5 h-5 bg-blue-400 dark:bg-blue-500 rounded shadow-sm"></div>
            <span className="text-gray-600 dark:text-gray-400 font-medium">10-30%</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-5 h-5 bg-yellow-400 dark:bg-yellow-500 rounded shadow-sm"></div>
            <span className="text-gray-600 dark:text-gray-400 font-medium">30-50%</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-5 h-5 bg-orange-500 dark:bg-orange-600 rounded shadow-sm"></div>
            <span className="text-gray-600 dark:text-gray-400 font-medium">50-70%</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-5 h-5 bg-red-600 dark:bg-red-700 rounded shadow-sm"></div>
            <span className="text-gray-600 dark:text-gray-400 font-medium">70-100%</span>
          </div>
        </div>
      </div>
    </div>
  )
}
