import React from 'react'
import { AlertTriangle, Shield, AlertCircle } from 'lucide-react'
import { ParentsGuideCategoryStats } from '../api/client'
import { useLanguage } from '../contexts/LanguageContext'

interface ParentsGuideProps {
  parentsGuide: Record<string, ParentsGuideCategoryStats>
}

const SEVERITY_COLORS = {
  NONE: 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20',
  MILD: 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900/20',
  MODERATE: 'text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-900/20',
  SEVERE: 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/20',
}

const CATEGORY_ICONS: Record<string, string> = {
  violence: '⚔️',
  gore: '🩸',
  profanity: '🤬',
  drugs: '💊',
  sex_act: '🔞',
  nudity: '👙',
  child_risk: '⚠️',
}

const ParentsGuide: React.FC<ParentsGuideProps> = ({ parentsGuide }) => {
  const { t } = useLanguage()

  if (!parentsGuide || Object.keys(parentsGuide).length === 0) {
    return null
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        <h2 className="text-2xl font-bold">Parents Guide</h2>
      </div>

      <div className="space-y-4">
        {Object.entries(parentsGuide).map(([category, stats]) => (
          <div
            key={category}
            className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{CATEGORY_ICONS[category]}</span>
                <h3 className="text-lg font-semibold">{t(`category.${category}`)}</h3>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${SEVERITY_COLORS[stats.severity as keyof typeof SEVERITY_COLORS]}`}>
                {stats.severity}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-500 dark:text-gray-400 mb-1">Episodes</div>
                <div className="font-semibold text-lg">{stats.episode_count}</div>
              </div>
              <div>
                <div className="text-gray-500 dark:text-gray-400 mb-1">Coverage</div>
                <div className="font-semibold text-lg">{stats.percentage.toFixed(2)}%</div>
              </div>
              <div>
                <div className="text-gray-500 dark:text-gray-400 mb-1">Peak Matches</div>
                <div className="font-semibold text-lg">{stats.top_matches}</div>
              </div>
            </div>

            {stats.severity === 'SEVERE' && (
              <div className="mt-3 flex items-start gap-2 text-sm text-red-600 dark:text-red-400">
                <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <p>This category contains significant content that may not be suitable for younger audiences.</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-900 dark:text-blue-200">
            <p className="font-semibold mb-1">Rating Guide:</p>
            <ul className="space-y-1 ml-4">
              <li><span className="font-semibold text-green-600 dark:text-green-400">NONE:</span> No content concerns</li>
              <li><span className="font-semibold text-yellow-600 dark:text-yellow-400">MILD:</span> Minor content, suitable for most audiences</li>
              <li><span className="font-semibold text-orange-600 dark:text-orange-400">MODERATE:</span> Some content may not be suitable for children</li>
              <li><span className="font-semibold text-red-600 dark:text-red-400">SEVERE:</span> Significant content requiring parental discretion</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ParentsGuide
