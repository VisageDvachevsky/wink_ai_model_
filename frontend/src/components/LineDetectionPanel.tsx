import React, { useState, useEffect } from 'react'
import { AlertTriangle, CheckCircle, XCircle, Info, TrendingUp, Filter } from 'lucide-react'
import { scriptsApi, LineDetection, LineDetectionStats } from '../api/client'
import { useLanguage } from '../contexts/LanguageContext'

interface LineDetectionPanelProps {
  scriptId: number
  onLineClick?: (lineStart: number, lineEnd: number) => void
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

const CATEGORY_COLORS: Record<string, string> = {
  violence: 'text-red-600 dark:text-red-400',
  gore: 'text-red-700 dark:text-red-500',
  profanity: 'text-orange-600 dark:text-orange-400',
  drugs: 'text-purple-600 dark:text-purple-400',
  sex_act: 'text-pink-600 dark:text-pink-400',
  nudity: 'text-pink-500 dark:text-pink-300',
  child_risk: 'text-yellow-600 dark:text-yellow-400',
}

const LineDetectionPanel: React.FC<LineDetectionPanelProps> = ({ scriptId, onLineClick }) => {
  const { t } = useLanguage()
  const [detections, setDetections] = useState<LineDetection[]>([])
  const [stats, setStats] = useState<LineDetectionStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [showFalsePositives, setShowFalsePositives] = useState(false)

  useEffect(() => {
    loadDetections()
  }, [scriptId, showFalsePositives])

  const loadDetections = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await scriptsApi.getScriptWithDetections(scriptId, showFalsePositives)
      setDetections(data.detections)
      setStats(data.stats)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load detections')
    } finally {
      setLoading(false)
    }
  }

  const runDetection = async () => {
    setLoading(true)
    setError(null)
    try {
      await scriptsApi.detectLines(scriptId, 3)
      await loadDetections()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run detection')
    } finally {
      setLoading(false)
    }
  }

  const handleMarkFalsePositive = async (detectionId: number, isFalsePositive: boolean) => {
    try {
      await scriptsApi.markFalsePositive(detectionId, isFalsePositive)
      await loadDetections()
    } catch (err) {
      console.error('Failed to mark false positive:', err)
    }
  }

  const filteredDetections = selectedCategory
    ? detections.filter(d => d.category === selectedCategory && !d.is_false_positive)
    : detections.filter(d => !d.is_false_positive)

  const getSeverityColor = (severity: number) => {
    if (severity >= 0.7) return 'bg-red-500'
    if (severity >= 0.4) return 'bg-orange-500'
    return 'bg-yellow-500'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          {t('detections.title')}
        </h3>
        <button
          onClick={runDetection}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? t('detections.analyzing') : t('detections.analyze')}
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <div className="text-2xl font-bold">{stats.total_detections}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('detections.total')}</div>
          </div>
          <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              {stats.false_positives}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('detections.falsePositives')}</div>
          </div>
          <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {stats.user_corrections}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('detections.corrections')}</div>
          </div>
          <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {Object.keys(stats.by_category).length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('detections.categories')}</div>
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-2 items-center">
        <Filter className="w-4 h-4 text-gray-500" />
        <button
          onClick={() => setSelectedCategory(null)}
          className={`px-3 py-1 rounded-full text-sm transition-colors ${
            selectedCategory === null
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          {t('detections.all')}
        </button>
        {stats && Object.entries(stats.by_category).map(([category, count]) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-3 py-1 rounded-full text-sm transition-colors ${
              selectedCategory === category
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            {CATEGORY_ICONS[category]} {t(`category.${category}`)} ({count})
          </button>
        ))}
      </div>

      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={showFalsePositives}
          onChange={(e) => setShowFalsePositives(e.target.checked)}
          className="rounded"
        />
        {t('detections.showFalsePositives')}
      </label>

      {error && (
        <div className="p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg flex items-center gap-2">
          <XCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      <div className="space-y-3">
        {filteredDetections.length === 0 && !loading && (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            <Info className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>{t('detections.noDetections')}</p>
          </div>
        )}

        {filteredDetections.map((detection, index) => (
          <div
            key={detection.id || index}
            className={`p-4 border rounded-lg transition-all hover:shadow-md cursor-pointer ${
              detection.is_false_positive
                ? 'bg-gray-100 dark:bg-gray-800 opacity-60 border-gray-300 dark:border-gray-700'
                : 'bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700'
            }`}
            onClick={() => onLineClick?.(detection.line_start, detection.line_end)}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{CATEGORY_ICONS[detection.category]}</span>
                <div>
                  <span className={`font-semibold ${CATEGORY_COLORS[detection.category]}`}>
                    {t(`category.${detection.category}`)}
                  </span>
                  <span className="text-sm text-gray-500 ml-2">
                    {t('detections.lines')} {detection.line_start}-{detection.line_end}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1">
                  <div className={`w-2 h-2 rounded-full ${getSeverityColor(detection.severity)}`} />
                  <span className="text-xs text-gray-500">
                    {Math.round(detection.severity * 100)}%
                  </span>
                </div>
                {detection.id && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleMarkFalsePositive(detection.id!, !detection.is_false_positive)
                    }}
                    className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
                    title={detection.is_false_positive ? t('detections.markAsValid') : t('detections.markAsFalsePositive')}
                  >
                    {detection.is_false_positive ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <XCircle className="w-4 h-4 text-gray-400" />
                    )}
                  </button>
                )}
              </div>
            </div>

            {detection.context_before && (
              <div className="text-xs text-gray-400 dark:text-gray-600 mb-1 pl-10">
                {detection.context_before}
              </div>
            )}

            <div className="font-mono text-sm bg-gray-50 dark:bg-gray-800 p-2 rounded pl-10">
              {detection.detected_text}
              <span className="ml-2 text-xs text-blue-600 dark:text-blue-400">
                ({detection.matched_patterns.count} {t('detections.matches')})
              </span>
            </div>

            {detection.context_after && (
              <div className="text-xs text-gray-400 dark:text-gray-600 mt-1 pl-10">
                {detection.context_after}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default LineDetectionPanel
