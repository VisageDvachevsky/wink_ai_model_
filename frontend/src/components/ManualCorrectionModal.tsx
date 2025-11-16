import React, { useState } from 'react'
import { X, Plus, AlertTriangle } from 'lucide-react'
import { scriptsApi, UserCorrection } from '../api/client'
import { useLanguage } from '../contexts/LanguageContext'

interface ManualCorrectionModalProps {
  scriptId: number
  onClose: () => void
  onSuccess: () => void
}

const CATEGORIES = [
  'violence',
  'gore',
  'profanity',
  'drugs',
  'sex_act',
  'nudity',
  'child_risk',
]

const CORRECTION_TYPES = {
  false_negative: 'False Negative (Missed by system)',
  manual_addition: 'Manual Addition',
}

const ManualCorrectionModal: React.FC<ManualCorrectionModalProps> = ({
  scriptId,
  onClose,
  onSuccess,
}) => {
  const { t } = useLanguage()
  const [correctionType, setCorrectionType] = useState('false_negative')
  const [lineStart, setLineStart] = useState('')
  const [lineEnd, setLineEnd] = useState('')
  const [category, setCategory] = useState('profanity')
  const [severity, setSeverity] = useState(0.5)
  const [note, setNote] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const correction: Omit<UserCorrection, 'id' | 'created_at'> = {
        script_id: scriptId,
        correction_type: correctionType,
        line_start: lineStart ? parseInt(lineStart) : undefined,
        line_end: lineEnd ? parseInt(lineEnd) : undefined,
        category,
        severity,
        note: note || undefined,
      }

      await scriptsApi.createCorrection(scriptId, correction)
      onSuccess()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create correction')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-xl font-semibold flex items-center gap-2">
            <Plus className="w-6 h-6" />
            {t('corrections.addCorrection')}
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">
              {t('corrections.type')}
            </label>
            <select
              value={correctionType}
              onChange={(e) => setCorrectionType(e.target.value)}
              className="w-full p-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
            >
              {Object.entries(CORRECTION_TYPES).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                {t('corrections.lineStart')}
              </label>
              <input
                type="number"
                value={lineStart}
                onChange={(e) => setLineStart(e.target.value)}
                min="1"
                className="w-full p-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
                placeholder="e.g., 42"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                {t('corrections.lineEnd')}
              </label>
              <input
                type="number"
                value={lineEnd}
                onChange={(e) => setLineEnd(e.target.value)}
                min={lineStart || '1'}
                className="w-full p-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
                placeholder="e.g., 45"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              {t('corrections.category')}
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full p-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
            >
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>
                  {t(`category.${cat}`)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              {t('corrections.severity')} ({Math.round(severity * 100)}%)
            </label>
            <input
              type="range"
              value={severity}
              onChange={(e) => setSeverity(parseFloat(e.target.value))}
              min="0"
              max="1"
              step="0.1"
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>{t('corrections.low')}</span>
              <span>{t('corrections.medium')}</span>
              <span>{t('corrections.high')}</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              {t('corrections.note')}
            </label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="w-full p-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 resize-none"
              rows={3}
              placeholder={t('corrections.notePlaceholder')}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {t('corrections.cancel')}
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {submitting ? t('corrections.adding') : t('corrections.add')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ManualCorrectionModal
