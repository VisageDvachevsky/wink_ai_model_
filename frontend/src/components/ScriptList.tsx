import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { scriptsApi } from '../api/client'
import { Film, Clock, Loader2, Sparkles, ChevronDown, ChevronUp, History } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import DemoScripts from './DemoScripts'
import apiClient from '../api/client'

interface ScriptCardProps {
  script: any
  language: string
  t: any
}

function ScriptCard({ script, language, t }: ScriptCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [versions, setVersions] = useState<any[]>([])
  const [loadingVersions, setLoadingVersions] = useState(false)

  const handleToggleVersions = async (e: React.MouseEvent) => {
    e.preventDefault()
    if (!expanded && versions.length === 0) {
      setLoadingVersions(true)
      try {
        const { data } = await apiClient.get(`/scripts/${script.id}/versions`)
        setVersions(data)
      } catch (err) {
        console.error('Failed to load versions:', err)
      } finally {
        setLoadingVersions(false)
      }
    }
    setExpanded(!expanded)
  }

  const hasMultipleVersions = script.current_version && script.current_version > 1

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl dark:shadow-gray-900/50 transition-all duration-300 border border-gray-100 dark:border-gray-700">
      <Link
        to={`/scripts/${script.id}`}
        className="group block p-6 hover:scale-[1.01] transition-transform"
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center flex-1 min-w-0">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700 rounded-lg mr-3 group-hover:scale-110 transition-transform">
              <Film className="h-5 w-5 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
              {script.title}
            </h3>
          </div>
          {script.predicted_rating && (
            <span className="ml-2 inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-sm">
              {script.predicted_rating}
            </span>
          )}
        </div>

        <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2">
          <Clock className="h-4 w-4 mr-2" />
          {new Date(script.created_at).toLocaleDateString(language === 'ru' ? 'ru-RU' : 'en-US')}
        </div>

        {script.total_scenes && (
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {script.total_scenes} {t('script.scenes')}
          </div>
        )}

        {!script.predicted_rating && (
          <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400">
            {t('script.not_rated')}
          </div>
        )}
      </Link>

      {hasMultipleVersions && (
        <>
          <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-3">
            <button
              onClick={handleToggleVersions}
              className="w-full flex items-center justify-between text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
            >
              <span className="flex items-center gap-2">
                <History className="h-4 w-4" />
                {language === 'ru' ? 'Версии' : 'Versions'} ({script.current_version})
              </span>
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
          </div>

          <div
            className={`overflow-hidden transition-all duration-500 ease-out ${
              expanded ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
            }`}
          >
            {loadingVersions ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-5 w-5 animate-spin text-indigo-600 dark:text-indigo-400" />
              </div>
            ) : (
              <div className="px-6 pb-4 space-y-2 max-h-80 overflow-y-auto">
                {versions.map((version, index) => (
                  <Link
                    key={version.id}
                    to={`/scripts/${script.id}?version=${version.version_number}`}
                    className="block p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 hover:shadow-md transform hover:scale-[1.02]"
                    style={{
                      animation: expanded ? `slideIn 0.3s ease-out ${index * 0.05}s both` : 'none'
                    }}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                        {language === 'ru' ? 'Версия' : 'Version'} {version.version_number}
                        {version.is_current && (
                          <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs rounded-full">
                            {language === 'ru' ? 'Текущая' : 'Current'}
                          </span>
                        )}
                      </span>
                      <div className="flex items-center gap-2">
                        {version.total_scenes !== null && version.total_scenes !== undefined && (
                          <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs rounded">
                            {version.total_scenes} {language === 'ru' ? 'сцен' : 'scenes'}
                          </span>
                        )}
                        {version.predicted_rating && (
                          <span className="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 text-xs font-bold rounded">
                            {version.predicted_rating}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                      {new Date(version.created_at).toLocaleString(language === 'ru' ? 'ru-RU' : 'en-US')}
                    </div>
                    {version.change_description && (
                      <div className="text-xs text-gray-500 dark:text-gray-500 italic">
                        {version.change_description}
                      </div>
                    )}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default function ScriptList() {
  const { language, t } = useLanguage()
  const [showDemoScripts, setShowDemoScripts] = useState(false)
  const { data: scripts, isLoading, error } = useQuery({
    queryKey: ['scripts'],
    queryFn: scriptsApi.list,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600 dark:text-blue-400" />
        <span className="ml-3 text-gray-700 dark:text-gray-300">{t('common.loading')}</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 dark:text-red-400 mb-2 font-semibold">{t('script.failed_load')}</div>
        <div className="text-gray-600 dark:text-gray-400 text-sm">{(error as Error).message}</div>
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="sm:flex sm:items-center mb-8">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{t('script.list_title')}</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {t('script.list_subtitle')}
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={() => setShowDemoScripts(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg hover:from-purple-700 hover:to-pink-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-600 transition-all"
          >
            <Sparkles className="h-4 w-4" />
            {language === 'ru' ? 'Демо Сценарии' : 'Demo Scripts'}
          </button>
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {scripts?.map((script) => (
          <ScriptCard key={script.id} script={script} language={language} t={t} />
        ))}
      </div>

      {showDemoScripts && (
        <DemoScripts onClose={() => setShowDemoScripts(false)} />
      )}
    </div>
  )
}
