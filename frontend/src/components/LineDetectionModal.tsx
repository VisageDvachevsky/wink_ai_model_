import React from 'react'
import { X } from 'lucide-react'
import LineDetectionPanel from './LineDetectionPanel'
import { useLanguage } from '../contexts/LanguageContext'

interface LineDetectionModalProps {
  scriptId: number
  onClose: () => void
  onLineClick?: (lineStart: number, lineEnd: number) => void
}

const LineDetectionModal: React.FC<LineDetectionModalProps> = ({ scriptId, onClose, onLineClick }) => {
  const { language } = useLanguage()

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {language === 'ru' ? 'Детекция строк' : 'Line Detection'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <X className="w-6 h-6 text-gray-500 dark:text-gray-400" />
          </button>
        </div>
        <div className="overflow-y-auto flex-1 p-6">
          <LineDetectionPanel scriptId={scriptId} onLineClick={onLineClick} />
        </div>
      </div>
    </div>
  )
}

export default LineDetectionModal
