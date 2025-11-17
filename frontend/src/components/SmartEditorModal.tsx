import React from 'react'
import { X } from 'lucide-react'
import SmartEditor from './SmartEditor'
import { LineDetection } from '../api/client'
import { useLanguage } from '../contexts/LanguageContext'

interface SmartEditorModalProps {
  scriptId: number
  initialContent: string
  detections: LineDetection[]
  onClose: () => void
  onSave: (content: string) => Promise<void>
  onReanalyze?: () => Promise<void>
}

const SmartEditorModal: React.FC<SmartEditorModalProps> = ({
  scriptId,
  initialContent,
  detections,
  onClose,
  onSave,
  onReanalyze,
}) => {
  const { language } = useLanguage()

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {language === 'ru' ? 'Редактор' : 'Editor'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <X className="w-6 h-6 text-gray-500 dark:text-gray-400" />
          </button>
        </div>
        <div className="overflow-y-auto flex-1 p-6">
          <SmartEditor
            scriptId={scriptId}
            initialContent={initialContent}
            detections={detections}
            onSave={onSave}
            onReanalyze={onReanalyze}
          />
        </div>
      </div>
    </div>
  )
}

export default SmartEditorModal
