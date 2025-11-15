import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { scriptsApi } from '../api/client'
import { Upload, FileText, Loader2 } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

export default function UploadScript() {
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { t } = useLanguage()

  const uploadMutation = useMutation({
    mutationFn: (data: { file: File; title: string }) =>
      scriptsApi.upload(data.file, data.title),
    onSuccess: (script) => {
      queryClient.invalidateQueries({ queryKey: ['scripts'] })
      navigate(`/scripts/${script.id}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (file) {
      uploadMutation.mutate({ file, title: title || file.name })
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-0">
      <div className="bg-white dark:bg-gray-800 shadow-lg rounded-xl border border-gray-100 dark:border-gray-700">
        <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('script.upload_title')}</h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {t('script.upload_subtitle')}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-6">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('script.title')}
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="block w-full rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400 sm:text-sm px-4 py-3 border transition-colors"
              placeholder={t('script.title')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('script.file_label')}
            </label>
            <div className="flex justify-center px-6 pt-8 pb-8 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-xl hover:border-blue-400 dark:hover:border-blue-500 transition-all bg-gray-50 dark:bg-gray-900/50">
              <div className="space-y-2 text-center">
                <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700 rounded-xl flex items-center justify-center mb-3">
                  <FileText className="h-8 w-8 text-white" />
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer rounded-md font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300 focus-within:outline-none transition-colors"
                  >
                    <span>{t('script.file_action')}</span>
                    <input
                      id="file-upload"
                      type="file"
                      className="sr-only"
                      accept=".txt"
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                    />
                  </label>
                  <span className="ml-1">{t('script.file_drag')}</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-500">{t('script.file_format')}</p>
                {file && (
                  <div className="mt-4 inline-flex items-center px-4 py-2 rounded-lg bg-blue-100 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700">
                    <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400 mr-2" />
                    <span className="text-sm text-blue-900 dark:text-blue-300 font-medium">
                      {t('script.file_selected')}: {file.name}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={!file || uploadMutation.isPending}
              className="inline-flex items-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {uploadMutation.isPending ? <Loader2 className="h-5 w-5 mr-2 animate-spin" /> : <Upload className="h-5 w-5 mr-2" />}
              {uploadMutation.isPending ? t('script.uploading') : t('script.upload')}
            </button>
          </div>

          {uploadMutation.isError && (
            <div className="rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4">
              <p className="text-sm text-red-800 dark:text-red-400">
                {t('script.error_upload')}
              </p>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
